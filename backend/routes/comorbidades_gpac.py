from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
from ..db import db_gpac
from bson import ObjectId

router = APIRouter(prefix="/comorbidities", tags=["Comorbidades GPAC"])

class Comorbidity(BaseModel):
    name: str
    description: Optional[str] = None
    specialty_suggestion: Optional[str] = None

@router.post("/")
async def criar_comorbidade(comorbidade: Comorbidity):
    comorbidade_dict = comorbidade.dict()
    result = await db_gpac.comorbidities.insert_one(comorbidade_dict)
    comorbidade_dict["_id"] = str(result.inserted_id)
    return comorbidade_dict

@router.get("/lista")
async def listar_comorbidades():
    comorbidades = []
    async for doc in db_gpac.comorbidities.find():
        comorbidade = {
            "_id": str(doc["_id"]),
            "name": doc.get("name", ""),
            "description": doc.get("description", ""),
            "specialty_suggestion": doc.get("specialty_suggestion", "")
        }
        comorbidades.append(comorbidade)
    return comorbidades

@router.put("/{id}")
async def atualizar_comorbidade(id: str, comorbidade: dict = Body(...)):
    try:
        result = await db_gpac.comorbidities.update_one(
            {"_id": ObjectId(id)},
            {"$set": comorbidade}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Comorbidade não encontrada ou dados iguais")
        return {"message": "Comorbidade atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def excluir_comorbidade(id: str):
    try:
        result = await db_gpac.comorbidities.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Comorbidade não encontrada")
        return {"message": "Comorbidade excluída com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
