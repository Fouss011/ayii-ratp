# app/routes/metrics.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db

router = APIRouter(prefix="/metrics", tags=["Metrics"])

# ---------------------------------------------------------------------------
# Admin token (x-admin-token)
# ---------------------------------------------------------------------------

def _admin_token() -> str:
    return (os.getenv("ADMIN_TOKEN") or os.getenv("NEXT_PUBLIC_ADMIN_TOKEN") or "").strip()

async def require_admin(request: Request) -> bool:
    tok = _admin_token()
    if not tok:
        raise HTTPException(status_code=401, detail="admin token not configured")
    hdr = (request.headers.get("x-admin-token") or "").strip()
    if hdr != tok:
        raise HTTPException(status_code=401, detail="invalid admin token")
    return True


# ---------------------------------------------------------------------------
# Types RATP (propreté)
# ---------------------------------------------------------------------------

RATP_KINDS = {
    "blood",       # sang
    "urine",
    "vomit",       # vomi
    "excrement",   # excréments
    "syringe",     # seringue
    "glass",       # verre / bouteille cassée
}

# ---------------------------------------------------------------------------
# /metrics/summary
# ---------------------------------------------------------------------------

@router.get("/summary")
async def metrics_summary(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=720),
):
    """
    Vue d'ensemble (last X hours) :
    - nb total de reports
    - nb par status (new / confirmed / resolved)
    - breakdown par kind (tous kinds présents dans la table)
    """

    params: Dict[str, Any] = {"h": hours}

    # Total & par status
    q_tot = text("""
        SELECT
          COUNT(*)::int AS n_total,
          COUNT(*) FILTER (WHERE COALESCE(status,'new') = 'new')::int       AS n_new,
          COUNT(*) FILTER (WHERE status = 'confirmed')::int                 AS n_confirmed,
          COUNT(*) FILTER (WHERE status = 'resolved')::int                  AS n_resolved
        FROM reports
        WHERE created_at > NOW() - ((:h::text || ' hours')::interval)
    """)
    res_tot = await db.execute(q_tot, params)
    tot = res_tot.mappings().first() or {
        "n_total": 0,
        "n_new": 0,
        "n_confirmed": 0,
        "n_resolved": 0,
    }

    # Breakdown par kind (tous kinds, pour debug général)
    q_kind = text("""
        SELECT kind::text AS kind, COUNT(*)::int AS n
          FROM reports
         WHERE created_at > NOW() - ((:h::text || ' hours')::interval)
         GROUP BY 1
         ORDER BY 2 DESC
    """)
    rows_kind = (await db.execute(q_kind, params)).mappings().all()

    return {
        "window_h": hours,
        "total": dict(tot),
        "by_kind": rows_kind,
        "avg_to_resolved_min": None,
        "server_now": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ---------------------------------------------------------------------------
# /metrics/incidents_by_day
# ---------------------------------------------------------------------------

@router.get("/incidents_by_day")
async def metrics_incidents_by_day(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    kind: Optional[str] = Query(None),
):
    """
    Série temporelle : nombre de reports 'to_clean' par jour (option : filtrer par kind).
    Spécifique RATP propreté : on ne regarde que signal = 'to_clean'.
    """

    where = ["LOWER(TRIM(signal::text)) = 'to_clean'"]
    params: Dict[str, Any] = {"d": days}

    if kind:
        where.append("LOWER(kind::text) = LOWER(:k)")
        params["k"] = kind

    q = text(f"""
        SELECT
          date_trunc('day', created_at)::date AS day,
          COUNT(*)::int AS n
        FROM reports
        WHERE {" AND ".join(where)}
          AND created_at >= NOW() - ((:d::text || ' days')::interval)
        GROUP BY 1
        ORDER BY 1
    """)

    rows = (await db.execute(q, params)).mappings().all()
    return {"days": days, "kind": kind, "series": rows}


# ---------------------------------------------------------------------------
# /metrics/kind_breakdown
# ---------------------------------------------------------------------------

@router.get("/kind_breakdown")
async def metrics_kind_breakdown(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """
    Répartition par kind sur la fenêtre (par défaut 30 jours).
    ⚠️ Ici on ne renvoie que les kinds RATP propreté :
        blood, urine, vomit, excrement, syringe, glass
    Même si la table contient encore d'anciens 'traffic', 'accident', etc.
    """

    q = text("""
        SELECT kind::text AS kind, COUNT(*)::int AS n
          FROM reports
         WHERE created_at >= NOW() - ((:d::text || ' days')::interval)
         GROUP BY 1
         ORDER BY 2 DESC
    """)

    rows_raw = (await db.execute(q, {"d": days})).mappings().all()

    items = []
    for r in rows_raw:
        k = (r["kind"] or "").lower()
        if k in RATP_KINDS:
            items.append({"kind": k, "n": r["n"]})

    return {"days": days, "items": items}
