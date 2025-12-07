# app/routes/cta.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os

from app.db import get_db

router = APIRouter(prefix="/cta", tags=["CTA"])


def _auth_admin(request: Request):
    admin_tok = (os.getenv("ADMIN_TOKEN") or "").strip()
    req_tok = (request.headers.get("x-admin-token") or "").strip()
    if admin_tok and req_tok != admin_tok:
        raise HTTPException(status_code=401, detail="invalid admin token")

@router.get("/incidents_v2")
async def cta_incidents_v2(
    request: Request,
    status: str = Query("", description="new|confirmed|resolved"),
    limit: int = Query(20, ge=1, le=200),
    debug: int = Query(0, description="1 = renvoyer l'erreur détaillée"),
    db: AsyncSession = Depends(get_db),
):
    _auth_admin(request)

    where_status = (
        "AND COALESCE(r.status,'new') = :status"
        if (status or "").strip().lower() in {"new", "confirmed", "resolved"}
        else ""
    )

    sql = f"""
    SELECT
      r.id,
      r.kind::text   AS kind,
      r.signal::text AS signal,
      ST_Y(r.geom::geometry) AS lat,
      ST_X(r.geom::geometry) AS lng,
      r.created_at,
      COALESCE(r.status,'new') AS status,
      r.phone,

      -- 📎 Média le plus récent de même type, à proximité (~50 m) du report
      (
        SELECT a.url
        FROM attachments a
        WHERE LOWER(TRIM(a.kind::text)) = LOWER(TRIM(r.kind::text))
          AND ST_DWithin(a.geom::geography, r.geom::geography, 50)
          AND a.created_at > r.created_at - INTERVAL '24 hours'
        ORDER BY a.created_at DESC
        LIMIT 1
      ) AS photo_url,

      -- 📊 Nombre de pièces jointes de même type à proximité (~50 m)
      (
        SELECT COUNT(*)::int
        FROM attachments a
        WHERE LOWER(TRIM(a.kind::text)) = LOWER(TRIM(r.kind::text))
          AND ST_DWithin(a.geom::geography, r.geom::geography, 50)
          AND a.created_at > r.created_at - INTERVAL '24 hours'
      ) AS attachments_count,

      -- 👥 Nombre de reports proches du même type (rayon ~50 m)
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

    try:
        res = await db.execute(text(sql), params)
        rows = res.fetchall()

        items = []
        for r in rows:
            m = r._mapping
            items.append(
                {
                    "id": m.get("id"),
                    "kind": m.get("kind"),
                    "signal": m.get("signal"),
                    "lat": float(m.get("lat")),
                    "lng": float(m.get("lng")),
                    "created_at": m.get("created_at"),
                    "status": m.get("status"),
                    "phone": m.get("phone"),
                    "photo_url": m.get("photo_url"),
                    "attachments_count": int(m.get("attachments_count") or 0),
                    "reports_count": int(m.get("reports_count") or 0),
                    "age_min": (
                        int(m.get("age_min"))
                        if m.get("age_min") is not None
                        else None
                    ),
                }
            )

        return {
            "api_version": "v2-proprete",
            "items": items,
            "count": len(items),
        }

    except Exception as e:
        if debug:
            raise HTTPException(
                status_code=500,
                detail=f"cta_incidents_v2 error: {e}",
            )
        raise HTTPException(status_code=500, detail="cta_incidents_v2 error")


@router.get("/incidents")
async def cta_incidents(
    request: Request,
    status: str = Query("", description="new|confirmed|resolved"),
    limit: int = Query(20, ge=1, le=200),
    debug: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    return await cta_incidents_v2(request, status, limit, debug, db)
