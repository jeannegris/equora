# routes/localizacao_gpac.py
from fastapi import APIRouter, HTTPException
from typing import List
import asyncio
from ..db import db_gpac
# routes/localizacao_gpac.py
from fastapi import APIRouter, HTTPException
from typing import List
import asyncio
from ..db import db_gpac

router = APIRouter(tags=["Localização GPAC"])

# Coleções do MongoDB
estados_collection = db_gpac["estados"]
municipios_collection = db_gpac["municipios"] 
bairros_collection = db_gpac["bairros"]

@router.get("/estados", response_model=List[dict])
async def get_estados():
    """Retorna lista de estados do banco local"""
    try:
        cursor = estados_collection.find({}).sort("nome", 1)
        estados = []
        async for estado in cursor:
            estados.append({
                "id": estado.get("codigo_ibge"),
                "sigla": estado.get("sigla"),
                "nome": estado.get("nome")
            })
        return estados
    except Exception as e:
        print(f"Erro ao buscar estados: {e}")
        return []

@router.get("/municipios/{estado_sigla}", response_model=List[dict])
async def get_municipios_by_estado(estado_sigla: str):
    """Retorna municípios de um estado do banco local"""
    try:
        cursor = municipios_collection.find({"estado_sigla": estado_sigla.upper()}).sort("nome", 1)
        municipios = []
        async for municipio in cursor:
            municipios.append({
                "id": municipio.get("codigo_ibge"),
                "nome": municipio.get("nome")
            })
        return municipios
    except Exception as e:
        print(f"Erro ao buscar municípios: {e}")
        return []

@router.get("/bairros/{municipio_codigo}", response_model=List[str])
async def get_bairros_by_municipio(municipio_codigo: int):
    """Retorna bairros de um município do banco local"""
    try:
        cursor = bairros_collection.find(
            {"municipio_codigo_ibge": municipio_codigo, "ativo": True}
        ).sort("nome", 1)
        
        bairros = []
        async for bairro in cursor:
            bairros.append(bairro.get("nome"))
        
        return sorted(list(set(bairros)))
    except Exception as e:
        print(f"Erro ao buscar bairros: {e}")
        return []

@router.get("/admin/stats")
async def get_stats():
    """Retorna estatísticas do banco de localização"""
    try:
        stats = {
            "estados": await estados_collection.count_documents({}),
            "municipios": await municipios_collection.count_documents({}),
            "bairros": await bairros_collection.count_documents({"ativo": True}),
        }
        municipios_com_bairros = await bairros_collection.distinct("municipio_codigo_ibge")
        stats["municipios_com_bairros"] = len(municipios_com_bairros)
        return stats
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return {"estados": 0, "municipios": 0, "bairros": 0, "municipios_com_bairros": 0}
