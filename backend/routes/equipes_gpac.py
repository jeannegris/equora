from fastapi import APIRouter, HTTPException
from ..db import db_gpac
from ..schemas.schemas_gpac import TeamModel
from bson import ObjectId
from typing import Dict, Any

router = APIRouter(prefix="/equipes", tags=["Equipes GPAC"])

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {"status": "ok", "message": "Equipes API funcionando"}

@router.get("/test-db")
async def test_db_connection():
    """Teste de conexão com o banco"""
    try:
        # Teste simples de conexão
        count = await db_gpac.equipes.count_documents({})
        return {"status": "ok", "message": f"Conexão OK. Total de equipes: {count}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")

@router.post("/")
async def create_team(team: TeamModel):
    try:
        print(f"🔍 Dados recebidos para criação de equipe: {team}")
        team_dict = team.model_dump()
        print(f"🔍 Dados após model_dump: {team_dict}")
        print(f"🔍 Districts específicos: {team_dict.get('districts', 'NÃO ENCONTRADO')}")
        
        result = await db_gpac.equipes.insert_one(team_dict)
        team_dict["_id"] = str(result.inserted_id)
        print(f"✅ Equipe criada com sucesso: {result.inserted_id}")
        
        return team_dict
    except Exception as e:
        print(f"❌ Erro ao criar equipe: {str(e)}")
        import traceback
        print(f"🔍 Stack trace completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/")
async def list_teams():
    try:
        print("🔍 Iniciando listagem de equipes...")
        teams = await db_gpac.equipes.find().to_list(1000)
        print(f"✅ {len(teams)} equipes encontradas")
        
        # Converter ObjectId para string manualmente e verificar districts
        for team in teams:
            if '_id' in team:
                team['_id'] = str(team['_id'])
            print(f"🔍 Equipe: {team.get('name', 'SEM NOME')} - Districts: {team.get('districts', 'NÃO ENCONTRADO')}")
        
        return teams
    except Exception as e:
        print(f"❌ Erro ao listar equipes: {str(e)}")
        import traceback
        print(f"🔍 Stack trace completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/{team_id}")
async def get_team(team_id: str):
    try:
        if not ObjectId.is_valid(team_id):
            raise HTTPException(status_code=400, detail="ID da equipe inválido")
            
        team = await db_gpac.equipes.find_one({"_id": ObjectId(team_id)})
        if not team:
            raise HTTPException(status_code=404, detail="Equipe não encontrada")
        return team
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao buscar equipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.put("/{team_id}")
async def update_team(team_id: str, team: TeamModel):
    try:
        print(f"🔍 Atualizando equipe {team_id} com dados: {team}")
        
        if not ObjectId.is_valid(team_id):
            raise HTTPException(status_code=400, detail="ID da equipe inválido")
            
        team_dict = team.model_dump(exclude_unset=True)
        print(f"🔍 Dados processados para atualização: {team_dict}")
        print(f"🔍 Districts para atualização: {team_dict.get('districts', 'NÃO ENCONTRADO')}")
        
        result = await db_gpac.equipes.update_one(
            {"_id": ObjectId(team_id)},
            {"$set": team_dict}
        )
        print(f"🔍 Resultado da atualização: matched={result.matched_count}, modified={result.modified_count}")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Equipe não encontrada")
            
        updated_team = await db_gpac.equipes.find_one({"_id": ObjectId(team_id)})
        if updated_team and '_id' in updated_team:
            updated_team['_id'] = str(updated_team['_id'])
        
        print(f"✅ Equipe atualizada com sucesso: {updated_team}")
        return updated_team
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao atualizar equipe: {str(e)}")
        import traceback
        print(f"🔍 Stack trace completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.delete("/{team_id}")
async def delete_team(team_id: str):
    try:
        if not ObjectId.is_valid(team_id):
            raise HTTPException(status_code=400, detail="ID da equipe inválido")
            
        result = await db_gpac.equipes.delete_one({"_id": ObjectId(team_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Equipe não encontrada")
        return {"message": "Equipe excluída com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao excluir equipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
