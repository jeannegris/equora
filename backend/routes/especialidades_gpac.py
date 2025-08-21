from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Definindo o router para especialidades
router = APIRouter(prefix="/especialidades", tags=["Especialidades GPAC"])

# Modelos Pydantic para requests
class SpecialtyBase(BaseModel):
    cbo: str
    name: str
    description: Optional[str] = ""

class SpecialtyCreate(SpecialtyBase):
    pass

class SpecialtyUpdate(SpecialtyBase):
    pass

# Dados iniciais para especialidades médicas
especialidades_data = [
    {"id": "1", "cbo": "2251", "name": "Médico Clínico", "description": "Médico generalista responsável pelo diagnóstico e tratamento de doenças em adultos"},
    {"id": "2", "cbo": "2252", "name": "Médico em Medicina de Família e Comunidade", "description": "Especialista em cuidados primários de saúde para indivíduos e famílias"},
    {"id": "3", "cbo": "2253", "name": "Médico Cardiologista", "description": "Especialista em diagnóstico e tratamento de doenças do coração e sistema cardiovascular"},
    {"id": "4", "cbo": "2254", "name": "Médico Dermatologista", "description": "Especialista em diagnóstico e tratamento de doenças da pele, cabelos e unhas"},
    {"id": "5", "cbo": "2255", "name": "Médico Ginecologista e Obstetra", "description": "Especialista em saúde reprodutiva feminina, gravidez e parto"},
    {"id": "6", "cbo": "2256", "name": "Médico Oftalmologista", "description": "Especialista em diagnóstico e tratamento de doenças dos olhos"},
    {"id": "7", "cbo": "2257", "name": "Médico Ortopedista", "description": "Especialista em diagnóstico e tratamento de doenças do sistema músculo-esquelético"},
    {"id": "8", "cbo": "2258", "name": "Médico Pediatra", "description": "Especialista em cuidados médicos de bebês, crianças e adolescentes"},
    {"id": "9", "cbo": "2259", "name": "Médico Psiquiatra", "description": "Especialista em diagnóstico e tratamento de transtornos mentais"},
    {"id": "10", "cbo": "2260", "name": "Médico Neurologista", "description": "Especialista em diagnóstico e tratamento de doenças do sistema nervoso"}
]

@router.get("/")
async def get_specialties():
    """Retorna todas as especialidades"""
    try:
        # Por enquanto usar dados em memória, depois migrar para MongoDB
        return especialidades_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_specialty(specialty: SpecialtyCreate):
    """Cria uma nova especialidade"""
    try:
        # Verificar se o CBO já existe
        for esp in especialidades_data:
            if esp['cbo'] == specialty.cbo:
                raise HTTPException(status_code=400, detail="CBO já existe")
        
        # Criar nova especialidade
        new_id = str(len(especialidades_data) + 1)
        new_specialty = {
            "id": new_id,
            "cbo": specialty.cbo,
            "name": specialty.name,
            "description": specialty.description or ""
        }
        
        especialidades_data.append(new_specialty)
        return new_specialty
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{specialty_id}")
async def update_specialty(specialty_id: str, specialty: SpecialtyUpdate):
    """Atualiza uma especialidade existente"""
    try:
        # Encontrar a especialidade
        specialty_index = None
        for i, esp in enumerate(especialidades_data):
            if esp['id'] == specialty_id:
                specialty_index = i
                break
        
        if specialty_index is None:
            raise HTTPException(status_code=404, detail="Especialidade não encontrada")
        
        # Verificar se o CBO já existe em outra especialidade
        for esp in especialidades_data:
            if esp['cbo'] == specialty.cbo and esp['id'] != specialty_id:
                raise HTTPException(status_code=400, detail="CBO já existe")
        
        # Atualizar a especialidade
        especialidades_data[specialty_index].update({
            "cbo": specialty.cbo,
            "name": specialty.name,
            "description": specialty.description or ""
        })
        
        return especialidades_data[specialty_index]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{specialty_id}")
async def delete_specialty(specialty_id: str):
    """Exclui uma especialidade"""
    try:
        # Encontrar e remover a especialidade
        for i, esp in enumerate(especialidades_data):
            if esp['id'] == specialty_id:
                del especialidades_data[i]
                return {"message": "Especialidade excluída com sucesso"}
        
        raise HTTPException(status_code=404, detail="Especialidade não encontrada")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cbo/{cbo}")
async def get_specialty_by_cbo(cbo: str):
    """Busca especialidade pelo CBO"""
    try:
        # Primeiro, tentar encontrar nos dados em memória
        for esp in especialidades_data:
            if esp["cbo"] == cbo:
                return {
                    "name": esp["name"],
                    "description": esp.get("description", "")
                }
        
        # Se não encontrar, buscar no dicionário de CBOs conhecidos
        cbo_especialidades = {
            '2251': {
                'name': 'Médico Clínico',
                'description': 'Médico generalista responsável pelo diagnóstico e tratamento de doenças em adultos'
            },
            '2252': {
                'name': 'Médico em Medicina de Família e Comunidade',
                'description': 'Especialista em cuidados primários de saúde para indivíduos e famílias'
            },
            '2253': {
                'name': 'Médico Cardiologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do coração e sistema cardiovascular'
            },
            '2254': {
                'name': 'Médico Dermatologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças da pele, cabelos e unhas'
            },
            '2255': {
                'name': 'Médico Ginecologista e Obstetra',
                'description': 'Especialista em saúde reprodutiva feminina, gravidez e parto'
            },
            '2256': {
                'name': 'Médico Oftalmologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças dos olhos'
            },
            '2257': {
                'name': 'Médico Ortopedista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema músculo-esquelético'
            },
            '2258': {
                'name': 'Médico Pediatra',
                'description': 'Especialista em cuidados médicos de bebês, crianças e adolescentes'
            },
            '2259': {
                'name': 'Médico Psiquiatra',
                'description': 'Especialista em diagnóstico e tratamento de transtornos mentais'
            },
            '2260': {
                'name': 'Médico Neurologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema nervoso'
            },
            '2261': {
                'name': 'Médico Endocrinologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema endócrino'
            },
            '2262': {
                'name': 'Médico Gastroenterologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema digestivo'
            },
            '2263': {
                'name': 'Médico Pneumologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema respiratório'
            },
            '2264': {
                'name': 'Médico Nefrologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças dos rins'
            },
            '2265': {
                'name': 'Médico Oncologista',
                'description': 'Especialista em diagnóstico e tratamento de câncer'
            },
            '2266': {
                'name': 'Médico Urologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças do sistema urinário'
            },
            '2267': {
                'name': 'Médico Anestesiologista',
                'description': 'Especialista em anestesia e cuidados perioperatórios'
            },
            '2268': {
                'name': 'Médico Radiologista',
                'description': 'Especialista em diagnóstico por imagem'
            },
            '2269': {
                'name': 'Médico Patologista',
                'description': 'Especialista em diagnóstico de doenças através de análise de tecidos'
            },
            '2270': {
                'name': 'Médico Infectologista',
                'description': 'Especialista em diagnóstico e tratamento de doenças infecciosas'
            }
        }
        
        especialidade = cbo_especialidades.get(cbo)
        if especialidade:
            return especialidade
        else:
            # Retornar uma mensagem mais amigável em vez de 404
            return {
                "name": "",
                "description": "",
                "message": f"CBO {cbo} não encontrado na base de dados. Você pode cadastrar manualmente."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
