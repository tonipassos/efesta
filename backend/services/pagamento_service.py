"""
É FESTA — Serviço de Pagamento (Mercado Pago)
Arquivo: backend/services/pagamento_service.py
Cobre: assinaturas recorrentes, pagamentos avulsos (anúncios), webhooks
"""

import mercadopago
from datetime import datetime, timedelta
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

# ── Cliente Mercado Pago ──────────────────────────────────────────────────────
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


# ══════════════════════════════════════════════════════════════════════════════
# PREFERÊNCIAS DE PAGAMENTO (checkout único)
# ══════════════════════════════════════════════════════════════════════════════

def criar_preferencia_assinatura(
    profissional_id: int,
    plano: str,
    preco: float,
    email_payer: str,
) -> dict:
    """
    Cria preferência de pagamento para assinatura mensal.
    Retorna o init_point (URL de checkout do Mercado Pago).
    """
    preference_data = {
        "items": [
            {
                "id": f"assinatura_{plano}_{profissional_id}",
                "title": f"É Festa — Plano {plano.capitalize()}",
                "description": f"Assinatura mensal do plano {plano} na plataforma É Festa",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco,
            }
        ],
        "payer": {"email": email_payer},
        "back_urls": {
            "success": f"{settings.APP_URL}/pagamento/sucesso?tipo=assinatura&plano={plano}",
            "failure": f"{settings.APP_URL}/pagamento/falha",
            "pending": f"{settings.APP_URL}/pagamento/pendente",
        },
        "auto_return": "approved",
        "notification_url": f"{settings.APP_URL}/api/pagamentos/webhook",
        "external_reference": f"assinatura_{profissional_id}_{plano}",
        "expires": True,
        "expiration_date_from": datetime.utcnow().isoformat(),
        "expiration_date_to": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "payment_methods": {
            "excluded_payment_types": [],
            "installments": 1,
        },
    }

    response = sdk.preference().create(preference_data)
    if response["status"] in [200, 201]:
        return {
            "preference_id": response["response"]["id"],
            "init_point": response["response"]["init_point"],
            "sandbox_init_point": response["response"].get("sandbox_init_point"),
        }

    logger.error(f"Erro ao criar preferência: {response}")
    raise Exception("Erro ao criar preferência de pagamento no Mercado Pago.")


def criar_preferencia_anuncio(
    profissional_id: int,
    tipo_anuncio: str,
    preco: float,
    email_payer: str,
) -> dict:
    """
    Cria preferência de pagamento para anúncio em destaque.
    """
    descricoes = {
        "semanal":    "Anúncio em Destaque por 7 dias no carrossel da homepage",
        "quinzenal":  "Anúncio em Destaque por 15 dias no carrossel da homepage",
        "mensal":     "Anúncio em Destaque por 30 dias no carrossel da homepage",
        "banner_topo": "Banner Premium no topo da página inicial por 30 dias",
    }

    preference_data = {
        "items": [
            {
                "id": f"anuncio_{tipo_anuncio}_{profissional_id}",
                "title": f"É Festa — Anúncio {tipo_anuncio.replace('_', ' ').capitalize()}",
                "description": descricoes.get(tipo_anuncio, "Anúncio em destaque"),
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco,
            }
        ],
        "payer": {"email": email_payer},
        "back_urls": {
            "success": f"{settings.APP_URL}/pagamento/sucesso?tipo=anuncio&subtipo={tipo_anuncio}",
            "failure": f"{settings.APP_URL}/pagamento/falha",
            "pending": f"{settings.APP_URL}/pagamento/pendente",
        },
        "auto_return": "approved",
        "notification_url": f"{settings.APP_URL}/api/pagamentos/webhook",
        "external_reference": f"anuncio_{profissional_id}_{tipo_anuncio}",
    }

    response = sdk.preference().create(preference_data)
    if response["status"] in [200, 201]:
        return {
            "preference_id": response["response"]["id"],
            "init_point": response["response"]["init_point"],
            "sandbox_init_point": response["response"].get("sandbox_init_point"),
        }

    raise Exception("Erro ao criar preferência de pagamento para anúncio.")


# ══════════════════════════════════════════════════════════════════════════════
# CONSULTA DE PAGAMENTO
# ══════════════════════════════════════════════════════════════════════════════

def consultar_pagamento(payment_id: str) -> dict:
    """Consulta status de um pagamento pelo ID."""
    response = sdk.payment().get(payment_id)
    if response["status"] == 200:
        return response["response"]
    raise Exception(f"Pagamento {payment_id} não encontrado.")


# ══════════════════════════════════════════════════════════════════════════════
# PROCESSAR WEBHOOK
# ══════════════════════════════════════════════════════════════════════════════

def processar_webhook(dados: dict, db) -> dict:
    """
    Processa notificações do Mercado Pago (IPN/Webhook).
    Atualiza status de pagamentos e assinaturas no banco.
    """
    from models.models import Pagamento, Assinatura, AnuncioDestaque, StatusPagamento, StatusAssinatura
    from datetime import datetime

    tipo = dados.get("type")
    payment_id = dados.get("data", {}).get("id")

    if not payment_id:
        return {"status": "ignored"}

    try:
        pagamento_mp = consultar_pagamento(str(payment_id))
        status_mp    = pagamento_mp.get("status")
        external_ref = pagamento_mp.get("external_reference", "")

        # Mapear status do MP para nosso enum
        status_map = {
            "approved": StatusPagamento.aprovado,
            "rejected": StatusPagamento.recusado,
            "cancelled": StatusPagamento.cancelado,
            "refunded": StatusPagamento.reembolsado,
        }
        novo_status = status_map.get(status_mp, StatusPagamento.pendente)

        # Atualizar pagamento local
        pagamento_local = (
            db.query(Pagamento)
            .filter(Pagamento.mp_payment_id == str(payment_id))
            .first()
        )

        if pagamento_local:
            pagamento_local.status = novo_status
            if novo_status == StatusPagamento.aprovado:
                pagamento_local.pago_em = datetime.utcnow()

                # Se for assinatura, ativar
                if pagamento_local.assinatura_id:
                    assinatura = db.query(Assinatura).get(pagamento_local.assinatura_id)
                    if assinatura:
                        assinatura.status = StatusAssinatura.ativa
                        from models.models import Profissional, StatusConta
                        prof = db.query(Profissional).get(assinatura.profissional_id)
                        if prof:
                            prof.status = StatusConta.ativo

                # Se for anúncio, ativar
                if pagamento_local.anuncio_id:
                    anuncio = db.query(AnuncioDestaque).get(pagamento_local.anuncio_id)
                    if anuncio:
                        anuncio.status = StatusPagamento.aprovado
                        anuncio.inicio = datetime.utcnow()
                        dias = {"semanal": 7, "quinzenal": 15, "mensal": 30, "banner_topo": 30}
                        anuncio.fim = datetime.utcnow() + timedelta(
                            days=dias.get(str(anuncio.tipo), 30)
                        )
                        prof = db.query(Profissional).get(anuncio.profissional_id)
                        if prof:
                            prof.destaque_ativo = True

            db.commit()

        return {"status": "processed", "payment_status": status_mp}

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return {"status": "error", "detail": str(e)}
