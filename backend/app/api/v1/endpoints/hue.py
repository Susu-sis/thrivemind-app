"""
endpoints/hue.py — Perfiles de iluminación Philips Hue.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_supabase
from app.services.hue_custom_service import get_all_profiles, create_custom_profile, delete_custom_profile

router = APIRouter()

# ── Hue bridge helpers ────────────────────────────────────────────────────────

def _hue_base() -> str:
    return f"http://{settings.hue_bridge_ip}/api/{settings.hueappkey}"

def _hue_configured() -> bool:
    return bool(settings.hue_bridge_ip and settings.hueappkey)


class HueProfileCreate(BaseModel):
    name: str
    kelvin: int
    brightness: int
    color_hex: Optional[str] = None
    description: str = ""


class HueApplyBody(BaseModel):
    kelvin: int
    brightness: int  # 0–100 %


# ── Bridge status ─────────────────────────────────────────────────────────────

@router.get("/status", summary="Estado de la bridge Hue y luces disponibles")
async def hue_status(current_user=Depends(get_current_user)):
    if not _hue_configured():
        return {"configured": False, "message": "HUE_BRIDGE_IP / hueappkey not set"}
    try:
        async with httpx.AsyncClient(timeout=4) as client:
            r = await client.get(f"{_hue_base()}/lights")
        r.raise_for_status()
        lights = r.json()
        return {
            "configured": True,
            "bridge_ip": settings.hue_bridge_ip,
            "lights_total": len(lights),
            "lights": {
                lid: {
                    "name": l["name"],
                    "on": l["state"]["on"],
                    "bri": l["state"].get("bri"),
                    "reachable": l["state"].get("reachable"),
                }
                for lid, l in lights.items()
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bridge unreachable: {exc}")


# ── Apply profile to all lights ───────────────────────────────────────────────

@router.post("/apply", summary="Aplicar temperatura de color y brillo a todas las luces")
async def hue_apply(body: HueApplyBody, current_user=Depends(get_current_user)):
    if not _hue_configured():
        raise HTTPException(status_code=503, detail="Hue bridge not configured")

    # Convert kelvin → mired (Hue uses mired colour temperature)
    ct = round(1_000_000 / body.kelvin)
    ct = max(153, min(500, ct))  # Hue valid range: 153 (6500 K) – 500 (2000 K)
    bri = round(body.brightness / 100 * 254)
    bri = max(1, min(254, bri))

    try:
        async with httpx.AsyncClient(timeout=4) as client:
            # Fetch light ids
            lights_r = await client.get(f"{_hue_base()}/lights")
            lights_r.raise_for_status()
            lights = lights_r.json()

            results = {}
            for lid in lights:
                r = await client.put(
                    f"{_hue_base()}/lights/{lid}/state",
                    json={"on": True, "ct": ct, "bri": bri, "transitiontime": 10},
                )
                results[lid] = r.json()

        return {
            "applied": True,
            "kelvin": body.kelvin,
            "brightness_pct": body.brightness,
            "ct_mired": ct,
            "bri_raw": bri,
            "lights_updated": len(results),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bridge error: {exc}")


# ── Profile CRUD ──────────────────────────────────────────────────────────────

@router.get("/profiles", summary="Listar perfiles predefinidos + custom")
async def list_profiles(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await get_all_profiles(current_user["id"], supabase)


@router.post("/profiles/custom", summary="Crear perfil personalizado")
async def create_profile(
    body: HueProfileCreate,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await create_custom_profile(
        user_id=current_user["id"],
        name=body.name,
        kelvin=body.kelvin,
        brightness=body.brightness,
        color_hex=body.color_hex,
        description=body.description,
        supabase=supabase,
    )


@router.delete("/profiles/{profile_id}", summary="Eliminar perfil custom")
async def delete_profile(
    profile_id: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await delete_custom_profile(current_user["id"], profile_id, supabase)



class HueProfileCreate(BaseModel):
    name: str
    kelvin: int
    brightness: int
    color_hex: Optional[str] = None
    description: str = ""


@router.get("/profiles", summary="Listar perfiles predefinidos + custom")
async def list_profiles(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await get_all_profiles(current_user["id"], supabase)


@router.post("/profiles/custom", summary="Crear perfil personalizado")
async def create_profile(
    body: HueProfileCreate,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await create_custom_profile(
        user_id=current_user["id"],
        name=body.name,
        kelvin=body.kelvin,
        brightness=body.brightness,
        color_hex=body.color_hex,
        description=body.description,
        supabase=supabase,
    )


@router.delete("/profiles/{profile_id}", summary="Eliminar perfil custom")
async def delete_profile(
    profile_id: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await delete_custom_profile(current_user["id"], profile_id, supabase)
