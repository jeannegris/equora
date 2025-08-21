from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Adicionar o diretório pai ao path para poder importar a API do MercadoPago
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..api.apimercadopago import create_payment_preference

# Importar schemas e conexão com banco
from ..schemas.schemas_bkautocenter import Order, OrderCreate, OrderUpdate, OrderItem, PayerData, PaymentStatus, PaymentType
from ..db import db_bkautocenter

router = APIRouter(tags=["Pagamentos BKautoCenter"])

class CartItem(BaseModel):
    id: str
    brand: str
    model: str
    size: str
    price: str  # Vem como string do frontend (ex: "R$ 299,90")
    quantity: int
    image: Optional[str] = None

class PayerInfo(BaseModel):
    name: str
    surname: str
    email: str
    phone_area_code: str = "11"
    phone_number: str
    cpf: str
    zip_code: str
    street_name: str
    street_number: int

class CheckoutRequest(BaseModel):
    cart_items: List[CartItem]
    payer_info: Optional[PayerInfo] = None

def convert_cart_to_mercadopago_items(cart_items: List[CartItem]) -> List[dict]:
    """
    Converte itens do carrinho para o formato esperado pelo MercadoPago
    """
    items = []
    
    for item in cart_items:
        # Converter preço de string (R$ 299,90) para float
        price_str = item.price.replace('R$ ', '').replace('.', '').replace(',', '.')
        unit_price = float(price_str)
        
        # Criar item no formato MercadoPago
        mp_item = {
            "id": item.id,
            "title": f"{item.brand} {item.model}",
            "description": f"Pneu {item.brand} {item.model} - Medida: {item.size}",
            "picture_url": f"http://140.238.187.229/bkautocenter/{item.image}" if item.image else None,
            "category_id": "car_electronics",
            "quantity": item.quantity,
            "currency_id": "BRL",
            "unit_price": unit_price,
        }
        
        items.append(mp_item)
    
    return items

def convert_cart_to_order_items(cart_items: List[CartItem]) -> List[OrderItem]:
    """
    Converte itens do carrinho para OrderItem (formato do banco)
    """
    order_items = []
    
    for item in cart_items:
        # Converter preço de string (R$ 299,90) para float
        price_str = item.price.replace('R$ ', '').replace('.', '').replace(',', '.')
        unit_price = float(price_str)
        
        order_item = OrderItem(
            id=item.id,
            title=f"{item.brand} {item.model}",
            description=f"Pneu {item.brand} {item.model} - Medida: {item.size}",
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=unit_price * item.quantity,
            picture_url=f"http://140.238.187.229/bkautocenter/{item.image}" if item.image else None
        )
        
        order_items.append(order_item)
    
    return order_items

def convert_payer_info(payer_info: PayerInfo) -> dict:
    """
    Converte informações do pagador para o formato MercadoPago
    """
    return {
        "name": payer_info.name,
        "surname": payer_info.surname,
        "email": payer_info.email,
        "phone": {
            "area_code": payer_info.phone_area_code,
            "number": payer_info.phone_number,
        },
        "identification": {
            "type": "CPF",
            "number": payer_info.cpf,
        },
        "address": {
            "zip_code": payer_info.zip_code,
            "street_name": payer_info.street_name,
            "street_number": payer_info.street_number,
        },
    }

@router.post("/checkout")
async def create_checkout(request: CheckoutRequest):
    """
    Endpoint para criar uma preferência de pagamento com os itens do carrinho
    """
    try:
        if not request.cart_items:
            raise HTTPException(status_code=400, detail="Carrinho vazio")
        
        # Converter itens do carrinho para formato MercadoPago
        mercadopago_items = convert_cart_to_mercadopago_items(request.cart_items)
        
        # Converter informações do pagador se fornecidas
        payer_info = None
        if request.payer_info:
            payer_info = convert_payer_info(request.payer_info)
        
        # Criar preferência de pagamento
        payment_url = create_payment_preference(mercadopago_items, payer_info)
        
        if not payment_url:
            raise HTTPException(status_code=500, detail="Erro ao gerar link de pagamento")
        
        # Calcular total para retornar na resposta
        total = sum(
            float(item.price.replace('R$ ', '').replace('.', '').replace(',', '.')) * item.quantity 
            for item in request.cart_items
        )
        
        # Extrair preference_id da URL de pagamento
        preference_id = None
        try:
            if 'pref_id=' in payment_url:
                preference_id = payment_url.split('pref_id=')[1].split('&')[0]
        except:
            pass
        
        # Gerar referência externa única
        import time
        external_reference = f"BKAC-{int(time.time())}"
        
        # Salvar pedido no banco de dados
        order_items = convert_cart_to_order_items(request.cart_items)
        
        payer_data = None
        if request.payer_info:
            payer_data = PayerData(
                name=request.payer_info.name,
                surname=request.payer_info.surname,
                email=request.payer_info.email,
                phone_area_code=request.payer_info.phone_area_code,
                phone_number=request.payer_info.phone_number,
                cpf=request.payer_info.cpf,
                zip_code=request.payer_info.zip_code,
                street_name=request.payer_info.street_name,
                street_number=request.payer_info.street_number
            )
        
        order = Order(
            items=order_items,
            total_amount=total,
            payer=payer_data,
            external_reference=external_reference,
            preference_id=preference_id,
            payment_status=PaymentStatus.PENDING
        )
        
        # Inserir no banco
        order_dict = order.dict(exclude={'id'})
        order_dict['_id'] = external_reference  # Usar external_reference como ID
        await db_bkautocenter.orders.insert_one(order_dict)
        
        return {
            "success": True,
            "payment_url": payment_url,
            "total_amount": total,
            "items_count": len(request.cart_items),
            "external_reference": external_reference,
            "message": "Link de pagamento gerado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/callback")
async def payment_callback(
    request: Request,
    collection_id: Optional[str] = Query(None),
    collection_status: Optional[str] = Query(None),
    payment_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    external_reference: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    merchant_order_id: Optional[str] = Query(None),
    preference_id: Optional[str] = Query(None),
    site_id: Optional[str] = Query(None),
    processing_mode: Optional[str] = Query(None)
):
    """
    Endpoint para processar o retorno do MercadoPago e atualizar o pedido no banco
    """
    try:
        if not external_reference:
            raise HTTPException(status_code=400, detail="external_reference é obrigatório")
        
        # Buscar pedido no banco
        existing_order = await db_bkautocenter.orders.find_one({"_id": external_reference})
        
        if not existing_order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        # Mapear status do MercadoPago para nosso enum
        payment_status = PaymentStatus.PENDING
        if status:
            status_mapping = {
                "approved": PaymentStatus.APPROVED,
                "pending": PaymentStatus.PENDING,
                "authorized": PaymentStatus.AUTHORIZED,
                "in_process": PaymentStatus.IN_PROCESS,
                "in_mediation": PaymentStatus.IN_MEDIATION,
                "rejected": PaymentStatus.REJECTED,
                "cancelled": PaymentStatus.CANCELLED,
                "refunded": PaymentStatus.REFUNDED,
                "charged_back": PaymentStatus.CHARGED_BACK
            }
            payment_status = status_mapping.get(status.lower(), PaymentStatus.PENDING)
        
        # Mapear tipo de pagamento
        payment_type_enum = None
        if payment_type:
            type_mapping = {
                "credit_card": PaymentType.CREDIT_CARD,
                "debit_card": PaymentType.DEBIT_CARD,
                "bank_transfer": PaymentType.BANK_TRANSFER,
                "ticket": PaymentType.TICKET,
                "digital_wallet": PaymentType.DIGITAL_WALLET
            }
            payment_type_enum = type_mapping.get(payment_type.lower(), PaymentType.OTHER)
        
        # Atualizar pedido
        update_data = {
            "payment_id": payment_id,
            "collection_id": collection_id,
            "merchant_order_id": merchant_order_id,
            "payment_status": payment_status.value,
            "collection_status": collection_status,
            "payment_type": payment_type_enum.value if payment_type_enum else None,
            "processing_mode": processing_mode,
            "updated_at": datetime.now()
        }
        
        # Se aprovado, definir data de pagamento
        if payment_status == PaymentStatus.APPROVED:
            update_data["payment_date"] = datetime.now()
        
        # Remover campos None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Atualizar no banco
        await db_bkautocenter.orders.update_one(
            {"_id": external_reference},
            {"$set": update_data}
        )
        
        # Log da atualização
        print(f"Pedido {external_reference} atualizado: {status} -> {payment_status}")
        
        return {
            "success": True,
            "message": "Pedido atualizado com sucesso",
            "external_reference": external_reference,
            "status": payment_status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/orders")
async def get_orders(skip: int = 0, limit: int = 100):
    """
    Endpoint para listar pedidos
    """
    try:
        orders = await db_bkautocenter.orders.find().skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
        
        # Converter para formato legível
        formatted_orders = []
        for order in orders:
            order["id"] = order["_id"]
            formatted_orders.append(order)
        
        return {
            "success": True,
            "orders": formatted_orders,
            "total": len(formatted_orders)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/orders/{external_reference}")
async def get_order(external_reference: str):
    """
    Endpoint para buscar um pedido específico
    """
    try:
        order = await db_bkautocenter.orders.find_one({"_id": external_reference})
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        order["id"] = order["_id"]
        
        return {
            "success": True,
            "order": order
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Webhook para receber notificações do MercadoPago
    Este endpoint é chamado automaticamente pelo MercadoPago quando há mudanças no status do pagamento
    """
    try:
        # Obter dados do webhook
        webhook_data = await request.json()
        
        # Log dos dados recebidos
        print(f"Webhook recebido: {webhook_data}")
        
        # Verificar se é uma notificação de pagamento
        if webhook_data.get('type') == 'payment':
            payment_id = webhook_data.get('data', {}).get('id')
            
            if payment_id:
                # Aqui você poderia consultar a API do MercadoPago para obter detalhes do pagamento
                # Por ora, vamos apenas logar
                print(f"Payment ID do webhook: {payment_id}")
        
        return {"status": "received"}
        
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/test")
async def test_payment():
    """
    Endpoint de teste para verificar se a integração está funcionando
    """
    test_items = [
        {
            "id": "test-001",
            "title": "Pneu Teste Michelin",
            "description": "Pneu de teste para validação",
            "category_id": "car_electronics",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 299.90,
        }
    ]
    
    try:
        payment_url = create_payment_preference(test_items)
        
        if payment_url:
            return {
                "success": True,
                "payment_url": payment_url,
                "message": "Teste realizado com sucesso"
            }
        else:
            return {
                "success": False,
                "message": "Erro ao gerar link de teste"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")
