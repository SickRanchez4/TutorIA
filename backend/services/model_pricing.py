"""Resolve versioned AI model prices and calculate token costs in USD."""
from datetime import datetime, timezone
from decimal import Decimal

from models.agenda_notificaciones import PrecioModeloIA

DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'gpt-5.4-mini'
TOKENS_PER_MILLION = Decimal('1000000')


def utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_active_model_price(provider=DEFAULT_PROVIDER, model=DEFAULT_MODEL, reference=None):
    """Return the price record active for a model at a given moment, if configured."""
    now = reference or utcnow_naive()
    return (
        PrecioModeloIA.query
        .filter(
            PrecioModeloIA.proveedor == provider,
            PrecioModeloIA.modelo == model,
            PrecioModeloIA.is_active == True,  # noqa: E712 - emits SQL Server-compatible "= 1"
            PrecioModeloIA.vigente_desde <= now,
            (PrecioModeloIA.vigente_hasta.is_(None) | (PrecioModeloIA.vigente_hasta >= now)),
        )
        .order_by(PrecioModeloIA.vigente_desde.desc())
        .first()
    )


def calculate_cost_usd(prompt_tokens, completion_tokens, price):
    """Calculate USD cost from a configured per-million-token price record."""
    if not price:
        return Decimal('0')

    return (
        Decimal(prompt_tokens) * Decimal(price.precio_prompt_por_millon_usd)
        + Decimal(completion_tokens) * Decimal(price.precio_completion_por_millon_usd)
    ) / TOKENS_PER_MILLION