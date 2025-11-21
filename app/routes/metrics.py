# app/routes/metrics.py
from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db

router = APIRouter(prefix="/metrics", tags=["Metrics"])

# --- Kinds RATP uniquement ---
RATP_KINDS = {"blood", "urine", "vomit", "excrement", "syringe", "glass"}

# --- auth admin simple (x-admin-token) ---
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


@router.get("/summary")
async def metrics_summary(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=720),
):
    """
    Vue d'ensemble (last X hours) RATP :
    - nb reports total
    - nb par kind (RATP only)
    """

    try:
        params = {"h": hours}

        # total (tous reports confondus)
        q_tot = text("""
            SELECT COUNT(*)::int AS n_total
              FROM reports
             WHERE created_at > NOW() - (:h || ' hours')::interval
        """)
        res_tot = await db.execute(q_tot, params)
        row_tot = res_tot.mappings().first() or {"n_total": 0}
        total = int(row_tot["n_total"])

        # par kind (on filtrera RATP après)
        q_kind = text("""
            SELECT kind::text AS kind, COUNT(*)::int AS n
              FROM reports
             WHERE created_at > NOW() - (:h || ' hours')::interval
             GROUP BY 1 ORDER BY 2 DESC
        """)
        rows_kind_raw = (await db.execute(q_kind, params)).mappings().all()
        rows_kind: List[Dict[str, Any]] = [dict(r) for r in rows_kind_raw]

        # 🔹 Garde uniquement les types RATP
        rows_kind = [r for r in rows_kind if (r.get("kind") in RATP_KINDS)]

        return {
            "window_h": hours,
            "total": {
                "n_total": total,
            },
            "by_kind": rows_kind,
            "server_now": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    except Exception as e:
        print(f"[metrics_summary] error: {e}")
        raise HTTPException(status_code=500, detail=f"metrics_summary error: {e}")


@router.get("/incidents_by_day")
async def metrics_incidents_by_day(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    kind: Optional[str] = Query(None),
):
    """
    Série temporelle: nombre de reports par jour (RATP only).
    On ne filtre plus sur 'cut' (propreté) : on compte tous les reports du kind.
    """

    try:
        where = ["created_at >= NOW() - (:d || ' days')::interval"]
        params: Dict[str, Any] = {"d": days}

        if kind:
            k = kind.strip().lower()
            if k not in RATP_KINDS:
                # Pas de données pour ce type
                return {"days": days, "kind": k, "series": []}
            where.append("LOWER(kind::text) = :k")
            params["k"] = k
        else:
            # uniquement les kinds RATP
            ratp_list = ", ".join(f"'{k}'" for k in RATP_KINDS)
            where.append(f"kind::text IN ({ratp_list})")

        q = text(f"""
            SELECT date_trunc('day', created_at)::date AS day, COUNT(*)::int AS n
              FROM reports
             WHERE {" AND ".join(where)}
             GROUP BY 1 ORDER BY 1
        """)
        rows_raw = (await db.execute(q, params)).mappings().all()
        rows: List[Dict[str, Any]] = [dict(r) for r in rows_raw]

        # normalisation date -> string
        for r in rows:
            d = r.get("day")
            if isinstance(d, datetime):
                r["day"] = d.date().isoformat()
            elif hasattr(d, "isoformat"):
                r["day"] = d.isoformat()
            else:
                r["day"] = str(d)

        return {"days": days, "kind": kind, "series": rows}
    except Exception as e:
        print(f"[metrics_incidents_by_day] error: {e}")
        raise HTTPException(status_code=500, detail=f"metrics_incidents_by_day error: {e}")


@router.get("/kind_breakdown")
async def metrics_kind_breakdown(
    ok: bool = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """
    Répartition par kind (pie RATP only).
    """

    try:
        q = text("""
            SELECT kind::text AS kind, COUNT(*)::int AS n
              FROM reports
             WHERE created_at >= NOW() - (:d || ' days')::interval
             GROUP BY 1 ORDER BY 2 DESC
        """)
        rows_raw = (await db.execute(q, {"d": days})).mappings().all()
        rows: List[Dict[str, Any]] = [dict(r) for r in rows_raw]

        # 🔹 Ne garder QUE les types RATP
        rows = [r for r in rows if (r.get("kind") in RATP_KINDS)]

        return {"days": days, "items": rows}
    except Exception as e:
        print(f"[metrics_kind_breakdown] error: {e}")
        raise HTTPException(status_code=500, detail=f"metrics_kind_breakdown error: {e}")
