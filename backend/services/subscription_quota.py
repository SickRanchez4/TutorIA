"""Monthly token quota helpers shared by AI request handlers and coordinator views."""
from datetime import datetime, timezone

from sqlalchemy import func

from models import db, ConsumoTokens
from models.institucion import Suscripcion


def utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def current_month_start(reference=None):
    value = reference or utcnow_naive()
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def subscription_summary(institucion_id, reference=None):
    """Return the current month's quota balance for an institution."""
    now = reference or utcnow_naive()
    subscription = Suscripcion.query.filter_by(institucion_id=institucion_id).first()
    if not subscription:
        return None

    is_valid = bool(
        subscription.is_active
        and subscription.fecha_inicio <= now
        and subscription.fecha_fin >= now
    )
    used = int(
        db.session.query(
            func.coalesce(func.sum(ConsumoTokens.prompt_tokens + ConsumoTokens.completion_tokens), 0)
        )
        .filter(
            ConsumoTokens.institucion_id == institucion_id,
            ConsumoTokens.fecha >= current_month_start(now),
            ConsumoTokens.fecha <= now,
        )
        .scalar()
        or 0
    )
    limit = int(subscription.limite_tokens_mensual or 0)
    remaining = max(limit - used, 0)

    return {
        'plan_nombre': subscription.plan.nombre if subscription.plan else None,
        'limite_tokens_mensual': limit,
        'tokens_usados_mes': used,
        'tokens_disponibles': remaining,
        'porcentaje_consumido': round((used / limit) * 100, 1) if limit else 100,
        'fecha_inicio': subscription.fecha_inicio.isoformat(),
        'fecha_fin': subscription.fecha_fin.isoformat(),
        'is_active': is_valid,
        'motivo_no_disponible': None if is_valid else 'La suscripción no está activa o ya venció.',
    }


def request_is_allowed(institucion_id, reservation_tokens, reference=None):
    """Return (allowed, summary) after checking an AI request's conservative reservation."""
    summary = subscription_summary(institucion_id, reference)
    if not summary:
        return False, None
    if not summary['is_active']:
        return False, summary
    return summary['tokens_disponibles'] >= reservation_tokens, summary