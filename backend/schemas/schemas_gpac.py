from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any, List
from datetime import date, datetime
from bson import ObjectId
from pydantic_core import core_schema

# Suporte a ObjectId do MongoDB para Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, v: str) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("ID inválido")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict:
        return {
            "type": "string",
            "example": "507f1f77bcf86cd799439011"
        }

# -----------------------------
# Modelo de Colaborador (staff)
# -----------------------------
class CollaboratorModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    phone: str
    role: str  # 'medico' | 'enfermeiro' | 'recepcionista' | 'administrador' (compatível com valores antigos também)
    specialty: Optional[list[str]] = None
    crm: Optional[str] = None
    gender: Optional[str] = None  # 'masculino' | 'feminino' | 'outros'
    birthDate: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    rgOrgan: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    cep: Optional[str] = None
    photo: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None  # Esta será hasheada antes de salvar
    changePasswordOnFirstLogin: Optional[bool] = False
    twoFactorAuth: Optional[bool] = False
    totp_secret: Optional[str] = None  # <-- Adicione este campo
    userProfile: Optional[str] = None  # 'administradores' | 'gestores' | 'equipe_medica' | 'cadastro'
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Agendamento
# -----------------------------
class Agendamento(BaseModel):
    patientId: str
    patientName: str
    collaboratorId: str
    collaboratorName: str
    date: str  # formato ISO ou 'YYYY-MM-DD'
    time: str  # formato 'HH:MM'
    type: str
    status: str = 'scheduled'  # scheduled, confirmed, completed, cancelled
    notes: Optional[str] = ''
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Comorbidade
# -----------------------------
class ComorbidityModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    specialty_suggestion: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Especialidade
# -----------------------------
class SpecialtyModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    cbo: str = Field(..., description="Código CBO da especialidade médica")
    name: str = Field(..., description="Nome da especialidade")
    description: Optional[str] = Field(default="", description="Descrição da especialidade")
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Perfil de Acesso
# -----------------------------
class ProfileModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Nome do perfil de acesso")
    description: Optional[str] = Field(default="", description="Descrição do perfil")
    permissions: list[str] = Field(default=[
        "overview",
        "patients",
        "patient-history",
        "collaborators",
        "appointments",
        "admin",
        "admin-comorbidities",
        "admin-specialties",
        "admin-profiles",
        "equipe"
    ], description="Lista de permissões/chaves de acesso")
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Localização
# -----------------------------
class EstadoModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    codigo_ibge: int = Field(..., description="Código IBGE do estado")
    sigla: str = Field(..., description="Sigla do estado (UF)")
    nome: str = Field(..., description="Nome do estado")
    regiao: str = Field(..., description="Região do estado")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

class MunicipioModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    codigo_ibge: int = Field(..., description="Código IBGE do município")
    nome: str = Field(..., description="Nome do município")
    estado_sigla: str = Field(..., description="Sigla do estado")
    estado_nome: str = Field(..., description="Nome do estado")
    estado_codigo_ibge: int = Field(..., description="Código IBGE do estado")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

class BairroModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    nome: str = Field(..., description="Nome do bairro/distrito")
    municipio_codigo_ibge: int = Field(..., description="Código IBGE do município")
    municipio_nome: str = Field(..., description="Nome do município")
    estado_sigla: str = Field(..., description="Sigla do estado")
    estado_nome: str = Field(..., description="Nome do estado")
    tipo: str = Field(default="bairro", description="Tipo: 'bairro', 'distrito', 'vila', etc.")
    fonte: str = Field(default="ibge", description="Fonte dos dados: 'ibge', 'local', 'brasil_api'")
    ativo: bool = Field(default=True, description="Se o bairro está ativo no sistema")
    criado_em: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# -----------------------------
# Modelo de Equipe
# -----------------------------

class TeamModel(BaseModel):
    name: str
    description: Optional[str] = ""
    collaborators: Optional[List[str]] = []
    collaboratorNames: Optional[List[str]] = []
    specialties: Optional[List[str]] = []
    state: str
    city: str
    districts: Optional[List[str]] = []
# -----------------------------
# Schemas Consolidados das Rotas
# -----------------------------

# Colaboradores - Schemas adicionais
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: str
    requiresPasswordChange: Optional[bool] = False
    twoFactorAuth: Optional[bool] = False

# Especialidades - Schemas base
class SpecialtyBase(BaseModel):
    cbo: str
    name: str
    description: Optional[str] = ""

class SpecialtyCreate(SpecialtyBase):
    pass

class SpecialtyUpdate(SpecialtyBase):
    pass

# Pacientes - Modelo principal
class PacienteModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    phone: str
    cpf: str
    city: Optional[str] = "-"
    age: Optional[int] = 0
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
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

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# Alias para compatibilidade
Paciente = PacienteModel

# Colaboradores - Alias para compatibilidade
Colaborador = CollaboratorModel
