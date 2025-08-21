from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
import os
from pathlib import Path
from fastapi.responses import FileResponse
from pydantic import ValidationError
from schemas.schemas_aguanaboca import Produto, ProdutoCreate, ProdutoUpdate
from db import db_agua_na_boca

router = APIRouter(prefix="/Produtos", tags=["Produtos Aguanaboca"])


UPLOADS_DIR = Path("/var/www/html/aguanaboca/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

@router.get("/", response_model=List[Produto], summary="Listar Produtos")
async def listar_produtos(category: Optional[str] = None):
    query = {"category": category} if category else {}
    produtos = await db_agua_na_boca.produtos.find(query).to_list(100)
    for p in produtos:
        p["id"] = str(p["_id"])
    return [Produto(**p) for p in produtos]

@router.post("/", response_model=Produto, summary="Criar Produto")
async def criar_produto(produto: ProdutoCreate):
    data = produto.dict()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    res = await db_agua_na_boca.produtos.insert_one(data)
    data["id"] = str(res.inserted_id)
    return Produto(**data)

@router.put("/{id}", response_model=Produto, summary="Atualizar Produto")
async def atualizar_produto(id: str, produto: ProdutoUpdate):
    data = {k: v for k, v in produto.dict().items() if v is not None}
    data["updated_at"] = datetime.utcnow()
    res = await db_agua_na_boca.produtos.update_one({"_id": ObjectId(id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    prod = await db_agua_na_boca.produtos.find_one({"_id": ObjectId(id)})
    prod["id"] = str(prod["_id"])
    return Produto(**prod)


@router.delete("/{id}", summary="Deletar Produto")
async def deletar_produto(id: str):
    produto = await db_agua_na_boca.produtos.find_one({"_id": ObjectId(id)})
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    # Excluir imagem se for de uploads ou nome simples
    image_url = produto.get("image_url")
    image_path = None
    if image_url:
        if image_url.startswith("/uploads/"):
            image_path = UPLOADS_DIR / image_url.replace("/uploads/", "")
        elif "/" not in image_url:
            image_path = UPLOADS_DIR / image_url
    if image_path:
        try:
            if image_path.exists():
                image_path.unlink()
        except Exception as e:
            print(f"Erro ao excluir imagem: {e}")
    res = await db_agua_na_boca.produtos.delete_one({"_id": ObjectId(id)})
    return {"ok": True}


@router.post("/upload-image", summary="Upload Imagem")
def upload_imagem(
    image: UploadFile = File(...),
    category: str = Form(...)
):
    ext = image.filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    folder = UPLOADS_DIR
    url = f"/uploads/{filename}"
    filepath = folder / filename
    with open(filepath, "wb") as f:
        f.write(image.file.read())
    # Ajustar dono do arquivo para www-data
    import shutil
    try:
        shutil.chown(str(filepath), user='www-data', group='www-data')
    except Exception as e:
        print(f"Erro ao ajustar dono do arquivo: {e}")
    return {"image_url": url}



# Endpoint para listar imagens órfãs
@router.get("/maintenance/orphaned-images", summary="Listar Imagens Órfãs")
async def listar_imagens_orfas():
    # Lista todos os arquivos em uploads
    arquivos = set(os.listdir(UPLOADS_DIR))
    # Busca todas as imagens associadas a produtos
    produtos = await db_agua_na_boca.produtos.find({"image_url": {"$ne": None}}).to_list(1000)
    imagens_usadas = set()
    for p in produtos:
        url = p.get("image_url")
        if url:
            if url.startswith("/uploads/"):
                imagens_usadas.add(url.replace("/uploads/", ""))
            elif "/" not in url:
                imagens_usadas.add(url)
    # Imagens órfãs = arquivos - imagens usadas
    orfas = arquivos - imagens_usadas
    result = []
    for nome in sorted(orfas):
        path = UPLOADS_DIR / nome
        result.append({
            "name": nome,
            "url": f"/uploads/{nome}",
            "size_kb": round(path.stat().st_size / 1024, 1) if path.exists() else 0
        })
    return {"orphaned_images": result}

# Endpoint para deletar uma imagem órfã
@router.delete("/maintenance/orphaned-images/{filename}", summary="Deletar Imagem Órfã")
async def deletar_imagem_orfa(filename: str):
    path = UPLOADS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    # Garante que não está em uso por nenhum produto
    produto = await db_agua_na_boca.produtos.find_one({"image_url": {"$regex": filename}})
    if produto:
        raise HTTPException(status_code=400, detail="Imagem ainda está associada a um produto")
    path.unlink()
    return {"ok": True, "deleted": filename}
