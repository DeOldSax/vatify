from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.session import get_db
from db.models import ApiKey, MonthlyQuota
from schemas.apikey import APIKeyCreateIn, APIKeyCreateOut, APIKeyListItem
from core.security import generate_api_key, hash_api_key
from deps import get_current_user
from datetime import date

router = APIRouter()

@router.post("", response_model=APIKeyCreateOut, status_code=201)
async def create_key(data: APIKeyCreateIn, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    secret, prefix, last4 = generate_api_key()
    key_hash = hash_api_key(secret)
    rec = ApiKey(user_id=user.id, name=data.name, key_hash=key_hash, prefix=prefix, last4=last4)
    db.add(rec); await db.commit(); await db.refresh(rec)
    return APIKeyCreateOut(id=str(rec.id), name=rec.name, created_at=rec.created_at, prefix=rec.prefix, last4=rec.last4, revoked=rec.revoked, secret=secret)

@router.get("", response_model=list[APIKeyListItem])
async def list_keys(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc()))).scalars().all()
    return [APIKeyListItem(id=str(r.id), name=r.name, created_at=r.created_at, prefix=r.prefix, last4=r.last4, revoked=r.revoked) for r in rows]

@router.post("/{key_id}/revoke")
async def revoke_key(key_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    key = await db.scalar(q)
    if not key:
        raise HTTPException(404, "Key not found")
    key.revoked = True
    await db.commit()
    return {"ok": True}

@router.post("/{key_id}/rotate", response_model=APIKeyCreateOut)
async def rotate_key(key_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    key = await db.scalar(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id))
    if not key:
        raise HTTPException(404, "Key not found")
    # revoke alt + neu erstellen
    key.revoked = True
    secret, prefix, last4 = generate_api_key()
    new_hash = hash_api_key(secret)
    new_key = ApiKey(user_id=user.id, name=key.name, key_hash=new_hash, prefix=prefix, last4=last4)
    db.add(new_key); await db.commit(); await db.refresh(new_key)
    return APIKeyCreateOut(id=str(new_key.id), name=new_key.name, created_at=new_key.created_at, prefix=new_key.prefix, last4=new_key.last4, revoked=new_key.revoked, secret=secret)

@router.get("/{key_id}/usage")
async def key_usage(key_id: str, month: str | None = None, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # month als YYYY-MM, default heute
    from datetime import datetime
    if month is None:
        m = date.today().replace(day=1)
    else:
        m = datetime.strptime(month, "%Y-%m").date().replace(day=1)

    key = await db.scalar(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id))
    if not key:
        raise HTTPException(404, "Key not found")

    row = await db.get(MonthlyQuota, {"month": m, "api_key_id": key.id})
    total = row.requests if row else 0

    # optional: byEndpoint live aus usage_counters aggregieren (für MVP weglassen/ergänzen)
    return {"month": str(m), "total": total}
