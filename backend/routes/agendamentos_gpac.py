from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..db import db_gpac
from bson import ObjectId
from ..schemas.schemas_gpac import Agendamento

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos GPAC"])

@router.post("/")
async def criar_agendamento(agendamento: Agendamento):
    agendamento_dict = agendamento.dict()
    result = await db_gpac.agendamentos.insert_one(agendamento_dict)
    agendamento_dict["_id"] = str(result.inserted_id)
    return agendamento_dict

@router.get("/")
async def listar_agendamentos():
    agendamentos = []
    async for doc in db_gpac.agendamentos.find():
        agendamento = {
            "_id": str(doc["_id"]),
            "patientId": doc.get("patientId", ""),
            "patientName": doc.get("patientName", ""),
            "collaboratorId": doc.get("collaboratorId", ""),
            "collaboratorName": doc.get("collaboratorName", ""),
            "date": doc.get("date", ""),
            "time": doc.get("time", ""),
            "type": doc.get("type", ""),
            "status": doc.get("status", "scheduled"),
            "notes": doc.get("notes", ""),
            "createdAt": doc.get("createdAt", datetime.utcnow()),
        }
        agendamentos.append(agendamento)
    return agendamentos

@router.put("/{id}")
async def atualizar_agendamento(id: str, agendamento: dict = Body(...)):
    try:
        result = await db_gpac.agendamentos.update_one(
            {"_id": ObjectId(id)},
            {"$set": agendamento}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado ou dados iguais")
        return {"message": "Agendamento atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def excluir_agendamento(id: str):
    try:
        result = await db_gpac.agendamentos.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return {"message": "Agendamento excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
