from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from ..db import db_gpac
from bson import ObjectId

router = APIRouter(prefix="/patients", tags=["Pacientes GPAC"])

# Modelo Pydantic para criação
class Paciente(BaseModel):
    name: str
    email: EmailStr
    phone: str
    cpf: str
    city: Optional[str] = "-"
    age: Optional[int] = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    gender: Optional[str] = "masculino"
    rg: Optional[str] = ""
    rgOrgan: Optional[str] = ""
    cns: Optional[str] = ""
    cep: Optional[str] = ""
    address: Optional[str] = ""
    neighborhood: Optional[str] = ""
    state: Optional[str] = ""
    careTypes: Optional[List[str]] = []
    medicalReports: Optional[List[str]] = []
    birthDate: Optional[str] = ""
    medicalHistory: Optional[str] = ""

@router.post("/")
async def criar_paciente(paciente: Paciente):
    paciente_dict = paciente.dict()
    result = await db_gpac.pacientes.insert_one(paciente_dict)
    paciente_dict["_id"] = str(result.inserted_id)
    return paciente_dict

@router.get("/pacientes")
async def listar_pacientes():
    pacientes = []
    async for doc in db_gpac.pacientes.find():
        paciente = {
            "_id": str(doc["_id"]),
            "name": doc.get("name", ""),
            "email": doc.get("email", ""),
            "phone": doc.get("phone", ""),
            "cpf": doc.get("cpf", ""),
            "city": doc.get("city", ""),
            "age": doc.get("age", 0),
            "createdAt": doc.get("createdAt", datetime.utcnow()),
            "gender": doc.get("gender", "masculino"),
            "rg": doc.get("rg", ""),
            "rgOrgan": doc.get("rgOrgan", ""),
            "cns": doc.get("cns", ""),
            "cep": doc.get("cep", ""),
            "address": doc.get("address", ""),
            "neighborhood": doc.get("neighborhood", ""),
            "state": doc.get("state", ""),
            "careTypes": doc.get("careTypes", []),
            "medicalReports": doc.get("medicalReports", []),
            "birthDate": doc.get("birthDate", ""),
            "medicalHistory": doc.get("medicalHistory", ""),
        }
        pacientes.append(paciente)
    return pacientes

@router.put("/{id}")
async def atualizar_paciente(id: str, paciente: dict = Body(...)):
    try:
        result = await db_gpac.pacientes.update_one(
            {"_id": ObjectId(id)},
            {"$set": paciente}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Paciente não encontrado ou dados iguais")
        
        # Buscar e retornar o paciente atualizado
        updated_doc = await db_gpac.pacientes.find_one({"_id": ObjectId(id)})
        if updated_doc:
            paciente_atualizado = {
                "_id": str(updated_doc["_id"]),
                "name": updated_doc.get("name", ""),
                "email": updated_doc.get("email", ""),
                "phone": updated_doc.get("phone", ""),
                "cpf": updated_doc.get("cpf", ""),
                "city": updated_doc.get("city", ""),
                "age": updated_doc.get("age", 0),
                "createdAt": updated_doc.get("createdAt", datetime.utcnow()),
                "gender": updated_doc.get("gender", "masculino"),
                "rg": updated_doc.get("rg", ""),
                "rgOrgan": updated_doc.get("rgOrgan", ""),
                "cns": updated_doc.get("cns", ""),
                "cep": updated_doc.get("cep", ""),
                "address": updated_doc.get("address", ""),
                "neighborhood": updated_doc.get("neighborhood", ""),
                "state": updated_doc.get("state", ""),
                "careTypes": updated_doc.get("careTypes", []),
                "medicalReports": updated_doc.get("medicalReports", []),
                "birthDate": updated_doc.get("birthDate", ""),
                "medicalHistory": updated_doc.get("medicalHistory", ""),
            }
            return paciente_atualizado
        else:
            return {"message": "Paciente atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def excluir_paciente(id: str):
    try:
        result = await db_gpac.pacientes.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return {"message": "Paciente excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint temporário para debug - verificar estrutura dos pacientes
@router.get("/debug/structure")
async def debug_patient_structure():
    try:
        count = await db_gpac.pacientes.count_documents({})
        sample_patient = await db_gpac.pacientes.find_one()
        
        # Removido: contagem de pacientes com comorbidities
        
        return {
            "total_patients": count,
            "sample_patient_keys": list(sample_patient.keys()) if sample_patient else [],
            "sample_patient": {
                "_id": str(sample_patient["_id"]) if sample_patient else None,
                "name": sample_patient.get("name") if sample_patient else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint temporário para adicionar comorbidities a um paciente (para teste)
## Endpoint removido: test-comorbidities
