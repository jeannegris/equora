import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from starlette.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel, Field
from typing import List
import uuid
import traceback
from datetime import datetime
from backend.schemas.email_utils import send_email

# Importação dos bancos separados
from backend.db import db_gpac, db_bkautocenter, db_agua_na_boca, db_equora, client

# Rotas GPAC
from backend.routes.pacientes_gpac import router as pacientes_router
from backend.routes.colaboradores_gpac import router as colaboradores_router
from backend.routes.agendamentos_gpac import router as agendamentos_router
from backend.routes.comorbidades_gpac import router as comorbidades_router
from backend.routes.especialidades_gpac import router as especialidades_router
from backend.routes.perfis_gpac import router as perfis_router
from backend.routes.equipes_gpac import router as equipes_router
from backend.routes.localizacao_gpac import router as localizacao_router
from backend.routes.twoFactor_gpac import router as twofactor_router

# Rotas BKAutocenter
from backend.routes.services_bkautocenter import router as services_bk_router
from backend.routes.tires_bkautocenter import router as tires_bk_router
from backend.routes.auth_bkautocenter import router as auth_bk_router
from backend.routes.payments_bkautocenter import router as payments_bk_router


# Schemas consolidados
from backend.schemas.email_schemas import EmailRequest

# Rotas Aguá na Boca
from backend.routes.produtos_aguanaboca import router as produtos_aguanaboca_router
from backend.routes.auth_aguanaboca import router as auth_aguanaboca_router

# Rotas Equora Systems
from backend.routes.admin_equora import router as admin_equora_router

# Carregar variáveis de ambiente
ROOT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")
print(">>> SENDGRID_API_KEY:", os.getenv("SENDGRID_API_KEY"))
print(">>> FROM_EMAIL:", os.getenv("FROM_EMAIL"))

# Modelos
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# App e router
app = FastAPI(root_path="/api")
# Servir imagens estáticas do frontend/build/img no caminho /img
IMG_DIR = Path(__file__).parent.parent / "frontend" / "build" / "img"
if IMG_DIR.exists():
    app.mount("/img", StaticFiles(directory=str(IMG_DIR)), name="img")
api_router = APIRouter()

# Rotas principais
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db_gpac.status_checks.insert_one(status_obj.dict())  # Agora usa o banco GPAC
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db_gpac.status_checks.find().to_list(1000)  # Agora usa o banco GPAC
    return [StatusCheck(**status_check) for status_check in status_checks]

# Nova rota de envio de e-mail
@api_router.post("/send-email")
async def send_custom_email(email: EmailRequest):
    try:
        status = send_email(email.to_email, email.subject, email.content)
        return {"msg": "Email enviado", "status_code": status}
    except Exception as e:
        logging.error("Erro ao enviar e-mail:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")

# Incluir rotas e CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:5173"],  # Permite a origem do frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir subrotas dentro do api_router (GPAC)
api_router.include_router(pacientes_router)
api_router.include_router(colaboradores_router)
api_router.include_router(agendamentos_router)
api_router.include_router(comorbidades_router)
api_router.include_router(especialidades_router)
api_router.include_router(perfis_router)
api_router.include_router(equipes_router)
api_router.include_router(localizacao_router, prefix="/localizacao")
api_router.include_router(twofactor_router, prefix="/2fa")


# Incluir subrotas dentro do api_router (BKAutocenter)
api_router.include_router(services_bk_router, prefix="/bkautocenter")
api_router.include_router(tires_bk_router, prefix="/bkautocenter")
api_router.include_router(auth_bk_router, prefix="/bkautocenter")
api_router.include_router(payments_bk_router, prefix="/bkautocenter")

# Incluir subrotas dentro do api_router (Aguá na Boca)
api_router.include_router(produtos_aguanaboca_router)
api_router.include_router(auth_aguanaboca_router)

# Incluir subrotas dentro do api_router (Equora Systems)
api_router.include_router(admin_equora_router)

# Agora inclui o api_router no app
app.include_router(api_router)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Encerrar conexões ao finalizar
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
