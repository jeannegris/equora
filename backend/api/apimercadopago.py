import mercadopago
import time

def create_payment_preference(items, payer_info=None):
    """
    Cria uma preferência de pagamento no MercadoPago e retorna o init_point
    
    Args:
        items (list): Lista de itens para pagamento
        payer_info (dict): Informações do pagador (opcional)
    
    Returns:
        str: URL do init_point para redirecionamento ao pagamento
    """
    
    sdk = mercadopago.SDK("APP_USR-3249431675786728-080813-9a08bd9f1d953457f00024ca2551d7c9-797769360")
    
    # Informações padrão do pagador se não fornecidas
    default_payer = {
        "name": "Cliente",
        "surname": "BKAutoCenter",
        "email": "cliente@bkautocenter.com",
        "phone": {
            "area_code": "21",
            "number": "99999-9999",
        },
        "identification": {
            "type": "CPF",
            "number": "12345678901",
        },
        "address": {
            "zip_code": "01234567",
            "street_name": "Rua Teste",
            "street_number": 123,
        },
    }
    
    request = {
        "items": items,
        "marketplace_fee": 0,
        "payer": payer_info if payer_info else default_payer,
        "back_urls": {
            "success": "http://140.238.187.229/bkautocenter/sucesso",
            "failure": "http://140.238.187.229/bkautocenter/falha",
            "pending": "http://140.238.187.229/bkautocenter/pendente",
        },
        "expires": False,
        "additional_info": "BKAutoCenter - Serviços Automotivos",
        "binary_mode": False,
        "external_reference": "BKAC-" + str(int(time.time())),
        "notification_url": "http://140.238.187.229/api/bkautocenter/webhook/mercadopago",
        "operation_type": "regular_payment",
        "payment_methods": {
            "excluded_payment_types": [
                {
                    "id": "ticket",
                },
            ],
            "installments": 12,
            "default_installments": 1,
        },
        "statement_descriptor": "BKAutoCenter",
    }
    
    try:
        preference_response = sdk.preference().create(request)
        preference = preference_response["response"]
        return preference['init_point']
    except Exception as e:
        print(f"Erro ao criar preferência: {e}")
        return None

# Exemplo de uso:
if __name__ == "__main__":
    # Itens de exemplo
    items_exemplo = [
        {
            "id": "001",
            "title": "Troca de Óleo Completa",
            "description": "Serviço completo de troca de óleo com filtro",
            "picture_url": "http://140.238.187.229/bkautocenter/public/troca-de-oleo.jpg",
            "category_id": "car_electronics",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 120.00,
        },
        {
            "id": "002", 
            "title": "Revisão Preventiva",
            "description": "Revisão completa do veículo com diagnóstico",
            "picture_url": "http://140.238.187.229/bkautocenter/public/Revisao.jpg",
            "category_id": "car_electronics",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 250.00,
        },
    ]
    
    # Chama a função e obtém o init_point
    payment_url = create_payment_preference(items_exemplo)
    
    if payment_url:
        print(f"Link de pagamento: {payment_url}")
    else:
        print("Erro ao gerar link de pagamento")