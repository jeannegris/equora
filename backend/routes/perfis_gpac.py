from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from datetime import datetime
from bson import ObjectId

from ..db import db_gpac
from ..schemas.schemas_gpac import ProfileModel

router = APIRouter(prefix="/perfis", tags=["Perfis GPAC"])

@router.post("/")
async def create_profile(profile_data: dict = Body(...)):
    """Criar um novo perfil de acesso"""
    try:
        # Verificar se já existe um perfil com o mesmo nome
        existing_profile = await db_gpac.profiles.find_one({"name": profile_data["name"]})
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um perfil com este nome"
            )
        
        # Criar novo perfil
        profile_dict = {
            "name": profile_data["name"],
            "description": profile_data.get("description", ""),
            "permissions": profile_data.get("permissions", []),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Inserir no banco
        result = await db_gpac.profiles.insert_one(profile_dict)
        
        # Recuperar o perfil inserido
        created_profile = await db_gpac.profiles.find_one({"_id": result.inserted_id})
        created_profile["id"] = str(created_profile["_id"])
        created_profile.pop("_id", None)
        
        return created_profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/")
async def get_profiles():
    """Listar todos os perfis de acesso"""
    try:
        profiles = []
        async for doc in db_gpac.profiles.find():
            profile = {
                "id": str(doc["_id"]),
                "name": doc.get("name", ""),
                "description": doc.get("description", ""),
                "permissions": doc.get("permissions", []),
                "createdAt": doc.get("createdAt", datetime.utcnow()).isoformat() if doc.get("createdAt") else datetime.utcnow().isoformat(),
                "updatedAt": doc.get("updatedAt", datetime.utcnow()).isoformat() if doc.get("updatedAt") else datetime.utcnow().isoformat()
            }
            profiles.append(profile)
        return profiles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )
@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    """Obter um perfil específico"""
    try:
        if not ObjectId.is_valid(profile_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do perfil inválido"
            )
        
        profile = await db_gpac.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado"
            )
        
        profile["id"] = str(profile["_id"])
        profile.pop("_id", None)
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.put("/{profile_id}")
async def update_profile(profile_id: str, profile_data: dict = Body(...)):
    """Atualizar um perfil de acesso"""
    try:
        if not ObjectId.is_valid(profile_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do perfil inválido"
            )
        
        # Verificar se o perfil existe
        existing_profile = await db_gpac.profiles.find_one({"_id": ObjectId(profile_id)})
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado"
            )
        
        # Verificar se o novo nome já existe (se foi alterado)
        if "name" in profile_data and profile_data["name"] != existing_profile["name"]:
            name_check = await db_gpac.profiles.find_one({
                "name": profile_data["name"],
                "_id": {"$ne": ObjectId(profile_id)}
            })
            if name_check:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um perfil com este nome"
                )
        
        # Preparar dados para atualização
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        if "name" in profile_data:
            update_data["name"] = profile_data["name"]
        if "description" in profile_data:
            update_data["description"] = profile_data["description"]
        if "permissions" in profile_data:
            update_data["permissions"] = profile_data["permissions"]
        
        # Atualizar no banco
        result = await db_gpac.profiles.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Perfil não encontrado ou dados iguais")
        
        # Se o nome do perfil foi alterado, sincronizar colaboradores
        if "name" in profile_data and profile_data["name"] != existing_profile["name"]:
            await db_gpac.colaboradores.update_many(
                {"userProfile": existing_profile["name"]},
                {"$set": {"userProfile": profile_data["name"]}}
            )
        
        # Recuperar o perfil atualizado
        updated_profile = await db_gpac.profiles.find_one({"_id": ObjectId(profile_id)})
        updated_profile["id"] = str(updated_profile["_id"])
        updated_profile.pop("_id", None)
        
        return updated_profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    """Excluir um perfil de acesso"""
    try:
        if not ObjectId.is_valid(profile_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do perfil inválido"
            )
        
        # Verificar se o perfil existe
        profile = await db_gpac.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado"
            )
        
        # Buscar colaboradores usando este perfil
        collaborators_using_profile = []
        async for doc in db_gpac.colaboradores.find({"userProfile": profile["name"]}):
            collaborators_using_profile.append(doc)
            
        if collaborators_using_profile:
            # Em vez de bloquear a exclusão, vamos:
            # 1. Notificar quantos colaboradores serão afetados
            # 2. Definir um perfil padrão para esses colaboradores
            default_profile = "equipe_medica"  # Perfil padrão
            
            # Verificar se existe um perfil padrão disponível
            fallback_profile = await db_gpac.profiles.find_one({"name": default_profile})
            if not fallback_profile:
                # Se não existe perfil padrão, buscar qualquer outro perfil
                fallback_profile = await db_gpac.profiles.find_one({
                    "_id": {"$ne": ObjectId(profile_id)}
                })
                if fallback_profile:
                    default_profile = fallback_profile["name"]
                else:
                    # Se não há outros perfis, bloquear exclusão
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Não é possível excluir o último perfil do sistema. {len(collaborators_using_profile)} colaborador(es) estão usando este perfil."
                    )
            
            # Atualizar colaboradores para usar o perfil padrão
            await db_gpac.colaboradores.update_many(
                {"userProfile": profile["name"]},
                {"$set": {"userProfile": default_profile}}
            )
        
        # Excluir perfil
        result = await db_gpac.profiles.delete_one({"_id": ObjectId(profile_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        response_message = "Perfil excluído com sucesso"
        if collaborators_using_profile:
            response_message += f". {len(collaborators_using_profile)} colaborador(es) foram automaticamente movidos para o perfil '{default_profile}'"
        
        return {"message": response_message}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/permissions/available")
async def get_available_permissions():
    """Obter lista de permissões disponíveis no sistema"""
    try:
        permissions = [
            {"id": "1", "name": "Visão Geral", "key": "overview", "type": "menu"},
            {"id": "2", "name": "Pacientes", "key": "patients", "type": "menu"},
            {"id": "3", "name": "Histórico de Pacientes", "key": "patient-history", "type": "menu"},
            {"id": "4", "name": "Colaboradores", "key": "collaborators", "type": "menu"},
            {"id": "5", "name": "Agendamentos", "key": "appointments", "type": "menu"},
            {"id": "6", "name": "Administração", "key": "admin", "type": "menu"},
            {"id": "7", "name": "Comorbidades", "key": "admin-comorbidities", "type": "submenu", "parentKey": "admin"},
            {"id": "8", "name": "Especialidades", "key": "admin-specialties", "type": "submenu", "parentKey": "admin"},
            {"id": "9", "name": "Perfis", "key": "admin-profiles", "type": "submenu", "parentKey": "admin"},
            {"id": "10", "name": "Equipes", "key": "equipe", "type": "menu"},
        ]
        return permissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/sync-collaborators")
async def sync_collaborators_profiles():
    """Sincronizar perfis de colaboradores com perfis existentes"""
    try:
        # Buscar todos os perfis disponíveis
        available_profiles = []
        async for profile in db_gpac.profiles.find():
            available_profiles.append(profile["name"])
        
        if not available_profiles:
            return {"message": "Nenhum perfil encontrado no sistema"}
        
        # Buscar colaboradores com perfis inválidos
        invalid_collaborators = []
        async for collaborator in db_gpac.colaboradores.find():
            user_profile = collaborator.get("userProfile")
            if user_profile and user_profile not in available_profiles:
                invalid_collaborators.append({
                    "id": str(collaborator["_id"]),
                    "name": collaborator.get("name"),
                    "current_profile": user_profile
                })
        
        if not invalid_collaborators:
            return {"message": "Todos os colaboradores possuem perfis válidos"}
        
        # Definir perfil padrão (primeiro da lista ou 'equipe_medica' se existir)
        default_profile = "equipe_medica" if "equipe_medica" in available_profiles else available_profiles[0]
        
        # Atualizar colaboradores com perfis inválidos
        updated_count = 0
        for collab in invalid_collaborators:
            result = await db_gpac.colaboradores.update_one(
                {"_id": ObjectId(collab["id"])},
                {"$set": {"userProfile": default_profile}}
            )
            if result.modified_count > 0:
                updated_count += 1
        
        return {
            "message": f"Sincronização concluída. {updated_count} colaborador(es) atualizado(s)",
            "updated_collaborators": len(invalid_collaborators),
            "default_profile_used": default_profile,
            "available_profiles": available_profiles
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sincronizar perfis: {str(e)}"
        )
