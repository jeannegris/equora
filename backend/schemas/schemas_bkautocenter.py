from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class ServiceCreate(BaseModel):
    name: str
    description: str
    price: str
    duration: str
    image_url: str

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    duration: Optional[str] = None
    image_url: Optional[str] = None

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: str
    duration: str
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TireCreate(BaseModel):
    brand: str
    model: str
    size: str
    price: str
    image_url: str
    in_stock: bool = True

class TireUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    size: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: Optional[bool] = None

class Tire(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand: str
    model: str
    size: str
    price: str
    image_url: str
    in_stock: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AdminAuth(BaseModel):
    username: str
    password: str

class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# SCHEMAS DE PEDIDOS E PAGAMENTOS - MERCADOPAGO
# =====================================================

class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    AUTHORIZED = "authorized"
    IN_PROCESS = "in_process"
    IN_MEDIATION = "in_mediation"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"

class PaymentType(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    TICKET = "ticket"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"

class OrderItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float  # quantity * unit_price
    picture_url: Optional[str] = None

class PayerData(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone_area_code: Optional[str] = None
    phone_number: Optional[str] = None
    cpf: Optional[str] = None
    zip_code: Optional[str] = None
    street_name: Optional[str] = None
    street_number: Optional[int] = None

class Order(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Dados do MercadoPago
    payment_id: Optional[str] = None
    collection_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    preference_id: Optional[str] = None
    external_reference: Optional[str] = None
    site_id: Optional[str] = None
    
    # Status e tipo de pagamento
    payment_status: PaymentStatus = PaymentStatus.PENDING
    collection_status: Optional[str] = None
    payment_type: Optional[PaymentType] = None
    processing_mode: Optional[str] = None
    
    # Dados do pedido
    items: List[OrderItem] = []
    total_amount: float = 0.0
    currency: str = "BRL"
    
    # Dados do cliente
    payer: Optional[PayerData] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    payment_date: Optional[datetime] = None
    
    # Dados adicionais
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True

class OrderCreate(BaseModel):
    items: List[OrderItem]
    payer: Optional[PayerData] = None
    external_reference: str
    preference_id: str
    total_amount: float

class OrderUpdate(BaseModel):
    payment_id: Optional[str] = None
    collection_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None
    collection_status: Optional[str] = None
    payment_type: Optional[PaymentType] = None
    processing_mode: Optional[str] = None
    payment_date: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.now)
