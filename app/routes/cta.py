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

      -- 📎 Média lié UNIQUEMENT à ce report
      (
        SELECT a.url
        FROM attachments a
        WHERE a.report_id = r.id
        ORDER BY a.created_at DESC
        LIMIT 1
      ) AS photo_url,

      -- 📊 Nombre de pièces jointes LIÉES à ce report
      (
        SELECT COUNT(*)::int
        FROM attachments a
        WHERE a.report_id = r.id
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
                "photo_url": m["photo_url"],
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


@router.get("/incidents")
async def cta_incidents(
    request: Request,
    status: str = Query("", description="new|confirmed|resolved"),
    limit: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await cta_incidents_v2(request, status, limit, db)
