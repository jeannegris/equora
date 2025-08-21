from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from ..schemas.schemas_bkautocenter import Tire, TireCreate, TireUpdate
from ..db import db_bkautocenter
from datetime import datetime
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/tires", tags=["Pneus BkAutoCenter"])

# Diretório para salvar as imagens
UPLOAD_DIR = Path("/var/www/html/bkautocenter/img/pneus")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=Tire)
async def create_tire(tire: TireCreate):
    """Criar um novo pneu"""
    tire_dict = tire.dict()
    tire_obj = Tire(**tire_dict)
    
    try:
        await db_bkautocenter.tires.insert_one(tire_obj.model_dump())
        return tire_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar pneu: {str(e)}")

@router.get("/", response_model=List[Tire])
async def get_tires():
    """Listar todos os pneus"""
    try:
        tires = await db_bkautocenter.tires.find().to_list(1000)
        return [Tire(**tire) for tire in tires]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pneus: {str(e)}")

@router.get("/{tire_id}", response_model=Tire)
async def get_tire(tire_id: str):
    """Buscar um pneu específico"""
    try:
        tire = await db_bkautocenter.tires.find_one({"id": tire_id})
        if not tire:
            raise HTTPException(status_code=404, detail="Pneu não encontrado")
        return Tire(**tire)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pneu: {str(e)}")

@router.put("/{tire_id}", response_model=Tire)
async def update_tire(tire_id: str, tire_update: TireUpdate):
    """Atualizar um pneu"""
    try:
        # Buscar o pneu existente
        existing_tire = await db_bkautocenter.tires.find_one({"id": tire_id})
        if not existing_tire:
            raise HTTPException(status_code=404, detail="Pneu não encontrado")
        
        # Preparar dados para atualização
        update_data = tire_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Atualizar no banco
        await db_bkautocenter.tires.update_one(
            {"id": tire_id},
            {"$set": update_data}
        )
        
        # Buscar e retornar o pneu atualizado
        updated_tire = await db_bkautocenter.tires.find_one({"id": tire_id})
        return Tire(**updated_tire)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar pneu: {str(e)}")

@router.delete("/{tire_id}")
async def delete_tire(tire_id: str):
    """Deletar um pneu"""
    try:
        # Buscar o pneu para obter a URL da imagem
        tire = await db_bkautocenter.tires.find_one({"id": tire_id})
        if not tire:
            raise HTTPException(status_code=404, detail="Pneu não encontrado")
        
        # Deletar o pneu do banco de dados
        result = await db_bkautocenter.tires.delete_one({"id": tire_id})
        
        # Se tiver uma URL de imagem, tentar deletar o arquivo
        if "image_url" in tire and tire["image_url"]:
            try:
                # Extrair o nome do arquivo da URL
                image_url = tire["image_url"]
                if "tire_" in image_url and ("/img/pneus/" in image_url or "/bkautocenter/img/pneus/" in image_url):
                    filename = image_url.split("/")[-1]
                    file_path = UPLOAD_DIR / filename
                    
                    # Verificar se o arquivo existe e tentar remover
                    if file_path.exists():
                        os.remove(file_path)
                        print(f"Imagem removida: {file_path}")
                    else:
                        print(f"Arquivo de imagem não encontrado: {file_path}")
            except Exception as img_error:
                print(f"Erro ao remover arquivo de imagem: {str(img_error)}")
        
        return {"message": "Pneu e imagem associada deletados com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar pneu: {str(e)}")

@router.post("/upload-image")
async def upload_tire_image(file: UploadFile = File(...)):
    """Upload de imagem para pneu"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Gerar nome único para o arquivo
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"tire_{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Definir permissões corretas para o arquivo
        os.chmod(file_path, 0o664)  # rw-rw-r--
        
        # Tentar definir o grupo correto (ubuntu:www-data)
        try:
            import pwd, grp
            uid = pwd.getpwnam('ubuntu').pw_uid
            gid = grp.getgrnam('www-data').gr_gid
            os.chown(file_path, uid, gid)
        except (KeyError, PermissionError) as e:
            # Se não conseguir mudar o owner, pelo menos garante que está legível
            print(f"Aviso: Não foi possível alterar owner do arquivo: {e}")
            os.chmod(file_path, 0o666)  # rw-rw-rw-
        
        # Retornar URL relativa
        return {"image_url": f"http://140.238.187.229/bkautocenter/img/pneus/{unique_filename}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload da imagem: {str(e)}")

@router.get("/maintenance/image-files", response_model=List[dict])
async def list_tire_image_files():
    """Listar todos os arquivos de imagens de pneus no servidor"""
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file() and file_path.name.startswith("tire_"):
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_kb": round(os.path.getsize(file_path) / 1024, 2),
                    "url": f"http://140.238.187.229/bkautocenter/img/pneus/{file_path.name}",
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                files.append(file_info)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos de imagens: {str(e)}")

@router.get("/maintenance/orphaned-images")
async def find_orphaned_tire_images():
    """Encontrar imagens órfãs (sem pneu associado) no servidor"""
    try:
        # 1. Listar todas as imagens no servidor
        all_files = []
        for file_path in UPLOAD_DIR.glob("tire_*"):
            if file_path.is_file():
                all_files.append(file_path.name)
        
        # 2. Buscar todas as URLs de imagens no banco de dados
        tires = await db_bkautocenter.tires.find({}, {"image_url": 1}).to_list(1000)
        used_images = []
        
        for tire in tires:
            if "image_url" in tire and tire["image_url"]:
                # Extrair o nome do arquivo da URL
                image_url = tire["image_url"]
                if "tire_" in image_url:
                    filename = image_url.split("/")[-1]
                    used_images.append(filename)
        
        # 3. Encontrar imagens órfãs (arquivos no servidor que não estão no banco)
        orphaned_images = []
        for file_name in all_files:
            if file_name not in used_images:
                file_path = UPLOAD_DIR / file_name
                orphaned_images.append({
                    "name": file_name,
                    "path": str(file_path),
                    "size_kb": round(os.path.getsize(file_path) / 1024, 2),
                    "url": f"http://140.238.187.229/bkautocenter/img/pneus/{file_name}",
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
        
        return {
            "total_images": len(all_files),
            "used_images": len(used_images),
            "orphaned_images": orphaned_images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar imagens órfãs: {str(e)}")

@router.delete("/maintenance/orphaned-images/{filename}")
async def delete_orphaned_tire_image(filename: str):
    """Deletar uma imagem órfã específica"""
    try:
        # Verificar se o arquivo existe
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Verificar se a imagem não está sendo usada
        tire = await db_bkautocenter.tires.find_one({"image_url": {"$regex": filename}})
        if tire:
            raise HTTPException(
                status_code=400, 
                detail=f"Esta imagem está sendo usada pelo pneu {tire.get('brand', '')} {tire.get('model', '')}"
            )
        
        # Deletar o arquivo
        os.remove(file_path)
        return {"message": f"Imagem {filename} deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar imagem: {str(e)}")

@router.delete("/maintenance/clean-all-orphaned-images")
async def clean_all_orphaned_tire_images():
    """Limpar todas as imagens órfãs de pneus"""
    try:
        # 1. Listar todas as imagens no servidor
        all_files = []
        for file_path in UPLOAD_DIR.glob("tire_*"):
            if file_path.is_file():
                all_files.append(file_path.name)
        
        # 2. Buscar todas as URLs de imagens no banco de dados
        tires = await db_bkautocenter.tires.find({}, {"image_url": 1}).to_list(1000)
        used_images = []
        
        for tire in tires:
            if "image_url" in tire and tire["image_url"]:
                # Extrair o nome do arquivo da URL
                image_url = tire["image_url"]
                if "tire_" in image_url:
                    filename = image_url.split("/")[-1]
                    used_images.append(filename)
        
        # 3. Deletar imagens órfãs
        deleted_count = 0
        for file_name in all_files:
            if file_name not in used_images:
                file_path = UPLOAD_DIR / file_name
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Erro ao deletar {file_path}: {str(e)}")
        
        return {
            "message": f"{deleted_count} imagens órfãs deletadas com sucesso",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar imagens órfãs: {str(e)}")
