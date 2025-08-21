# -------------------------------------------------------------------
# Ajuste do PATH e imports padrão do sistema
# -------------------------------------------------------------------

import sys
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

import os
import logging
import traceback
import uuid
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# Importações internas (bancos e schemas)
# -------------------------------------------------------------------
from schemas.email_utils import send_email
from schemas.email_schemas import EmailRequest
from db import db_gpac, db_bkautocenter, db_agua_na_boca, db_equora, client

# -------------------------------------------------------------------
# Importações de rotas GPAC
# -------------------------------------------------------------------
from routes.pacientes_gpac import router as pacientes_router
from routes.colaboradores_gpac import router as colaboradores_router
from routes.agendamentos_gpac import router as agendamentos_router
from routes.comorbidades_gpac import router as comorbidades_router
from routes.especialidades_gpac import router as especialidades_router
from routes.perfis_gpac import router as perfis_router
from routes.equipes_gpac import router as equipes_router
from routes.localizacao_gpac import router as localizacao_router
from routes.twoFactor_gpac import router as twofactor_router

# -------------------------------------------------------------------
# Importações de rotas BKAutocenter
# -------------------------------------------------------------------
from routes.services_bkautocenter import router as services_bk_router
from routes.tires_bkautocenter import router as tires_bk_router
from routes.auth_bkautocenter import router as auth_bk_router
from routes.payments_bkautocenter import router as payments_bk_router

# -------------------------------------------------------------------
# Importações de rotas Aguá na Boca
# -------------------------------------------------------------------
from routes.produtos_aguanaboca import router as produtos_aguanaboca_router
from routes.auth_aguanaboca import router as auth_aguanaboca_router

# -------------------------------------------------------------------
# Importações de rotas Equora Systems
# -------------------------------------------------------------------
from routes.admin_equora import router as admin_equora_router

# -------------------------------------------------------------------
# Carregar variáveis de ambiente
# -------------------------------------------------------------------
load_dotenv(dotenv_path=ROOT_DIR / ".env")
print(">>> SENDGRID_API_KEY:", os.getenv("SENDGRID_API_KEY"))
print(">>> FROM_EMAIL:", os.getenv("FROM_EMAIL"))

# -------------------------------------------------------------------
# Modelos Pydantic
# -------------------------------------------------------------------
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# -------------------------------------------------------------------
# Inicialização do FastAPI e configuração de diretórios estáticos
# -------------------------------------------------------------------
app = FastAPI(root_path="/api")

# Servir imagens estáticas do frontend/build/img
IMG_DIR = ROOT_DIR.parent / "frontend" / "build" / "img"
if IMG_DIR.exists():
    app.mount("/img", StaticFiles(directory=str(IMG_DIR)), name="img")

api_router = APIRouter()

# -------------------------------------------------------------------
# Rotas principais
# -------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.dict())
    await db_gpac.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db_gpac.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/send-email")
async def send_custom_email(email: EmailRequest):
    try:
        status = send_email(email.to_email, email.subject, email.content)
        return {"msg": "Email enviado", "status_code": status}
    except Exception as e:
        logging.error("Erro ao enviar e-mail:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")

# -------------------------------------------------------------------
# Configuração de CORS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Liberado para qualquer origem
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Inclusão das rotas no api_router
# -------------------------------------------------------------------

# GPAC
api_router.include_router(pacientes_router)
api_router.include_router(colaboradores_router)
api_router.include_router(agendamentos_router)
api_router.include_router(comorbidades_router)
api_router.include_router(especialidades_router)
api_router.include_router(perfis_router)
api_router.include_router(equipes_router)
api_router.include_router(localizacao_router, prefix="/localizacao")
api_router.include_router(twofactor_router, prefix="/2fa")

# BKAutocenter
api_router.include_router(services_bk_router, prefix="/bkautocenter")
api_router.include_router(tires_bk_router, prefix="/bkautocenter")
api_router.include_router(auth_bk_router, prefix="/bkautocenter")
api_router.include_router(payments_bk_router, prefix="/bkautocenter")

# Aguá na Boca
api_router.include_router(produtos_aguanaboca_router)
api_router.include_router(auth_aguanaboca_router)

# Equora Systems
api_router.include_router(admin_equora_router)

# -------------------------------------------------------------------
# Incluir api_router no app
# -------------------------------------------------------------------
app.include_router(api_router)

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Shutdown do servidor
# -------------------------------------------------------------------
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
