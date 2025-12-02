# app/routes/cta.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os
from app.db import get_db

# Router CTA (prefix = /cta)
router = APIRouter(prefix="/cta", tags=["CTA"])

def _auth_admin(request: Request):
    admin_tok = (os.getenv("ADMIN_TOKEN") or "").strip()
    req_tok   = (request.headers.get("x-admin-token") or "").strip()
    if admin_tok and req_tok != admin_tok:
        raise HTTPException(status_code=401, detail="invalid admin token")

# -----------------------------
# V2 (phone + média lié au report + stats)
# -----------------------------
@router.get("/incidents_v2")
async def cta_incidents_v2(
    request: Request,
    status: str = Query("", description="new|confirmed|resolved"),
    limit: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    _auth_admin(request)

    where_status = (
        "AND COALESCE(r.status,'new') = :status"
        if (status or "").strip().lower() in {"new", "confirmed", "resolved"}
        else ""
    )

    # ⚠️ On ne garde que les reports "to_clean" (propreté RATP)
    sql = f"""
    SELECT
      r.id,
      r.kind::text   AS kind,
      r.signal::text AS signal,
      ST_Y(r.geom::geometry) AS lat,
      ST_X(r.geom::geometry) AS lng,
      r.created_at,
      COALESCE(r.status,'new') AS status,
      r.phone,  -- téléphone saisi dans le report

      -- 📎 Dernier média lié à CE report (image ou vidéo)
      (
        SELECT a.url
        FROM attachments a
        WHERE a.report_id = r.id
        ORDER BY a.created_at DESC
        LIMIT 1
      ) AS photo_url,

      (
        SELECT a.mime_type
        FROM attachments a
        WHERE a.report_id = r.id
        ORDER BY a.created_at DESC
        LIMIT 1
      ) AS mime_type,

      -- 📊 Nombre de pièces jointes sur ce report
      (
        SELECT COUNT(*)::int
        FROM attachments a
        WHERE a.report_id = r.id
      ) AS attachments_count,

      -- 👥 Nombre de reports proches du même type (même kind, rayon 50 m)
      (
        SELECT COUNT(*)::int
        FROM reports r2
        WHERE r2.kind = r.kind
          AND LOWER(TRIM(r2.signal::text)) = 'to_clean'
          AND ST_DWithin(r2.geom::geography, r.geom::geography, 50)
      ) AS reports_count,

      -- ⏱ âge en minutes
      EXTRACT(EPOCH FROM (NOW() - r.created_at))::int / 60 AS age_min

    FROM reports r
    WHERE LOWER(TRIM(r.signal::text)) = 'to_clean'
      {where_status}
    ORDER BY r.created_at DESC
    LIMIT :lim
    """

    params = {"lim": int(limit)}
    if "status" in where_status:
        params["status"] = status.strip().lower()

    res = await db.execute(text(sql), params)
    rows = res.fetchall()

    items = []
    for r in rows:
        m = r._mapping
        items.append(
            {
                "id": m["id"],
                "kind": m["kind"],
                "signal": m["signal"],
                "lat": float(m["lat"]),
                "lng": float(m["lng"]),
                "created_at": m["created_at"],
                "status": m["status"],
                "phone": m.get("phone"),

                # média
                "photo_url": m["photo_url"],
                "mime_type": m.get("mime_type"),

                # stats
                "attachments_count": int(m["attachments_count"] or 0),
                "reports_count": int(m["reports_count"] or 0),
                "age_min": int(m["age_min"]) if m["age_min"] is not None else None,
            }
        )

    return {
        "api_version": "v2-proprete",
        "items": items,
        "count": len(items),
    }


# -----------------------------
# ALIAS /cta/incidents → même réponse que V2
# -----------------------------
@router.get("/incidents")
async def cta_incidents(
    request: Request,
    status: str = Query("", description="new|confirmed|resolved"),
    limit: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    # On réutilise EXACTEMENT la V2
    return await cta_incidents_v2(request, status, limit, db)