from __future__ import annotations

import os
import re
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# -------------------------------------------------------------------
# DATABASE_URL : on nettoie sslmode pour asyncpg
# -------------------------------------------------------------------
RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")

# Si l'URL contient ?sslmode=require ou &sslmode=require → on le supprime
if RAW_DATABASE_URL and "sslmode=" in RAW_DATABASE_URL:
    # supprime le paramètre sslmode dans la query
    DATABASE_URL = re.sub(r"[?&]sslmode=[^&]+", "", RAW_DATABASE_URL)
else:
    DATABASE_URL = RAW_DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# -------------------------------------------------------------------
# Engine async SQLAlchemy (sans connect_args, compatible asyncpg)
# -------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# -------------------------------------------------------------------
# Dependency FastAPI
# -------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
