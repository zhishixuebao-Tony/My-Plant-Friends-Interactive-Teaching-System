from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.mongodb import db_instance
from app.websockets.ws_manager import ws_manager

router = APIRouter()

NEXT_BUTTON_DEFAULTS = {
    'welcome_next': True,
    'sensory_submit_next': True,
    'sensory_transition_next': True,
    'view_record_cards_next': True,
    'record_card_submit_next': True,
    'record_card_transition_next': True,
    'resource_pack_next': True,
    'final_draft_submit_next': True,
}


class OpsPasswordReq(BaseModel):
    password: str


class ButtonToggleReq(BaseModel):
    enabled: bool


async def _get_admin_config_value(key: str):
    config = await db_instance.db.admin_config.find_one({'key': key})
    if not config:
        return None
    return config.get('value')


async def _set_admin_config_value(key: str, value):
    await db_instance.db.admin_config.update_one(
        {'key': key},
        {'$set': {'key': key, 'value': value}},
        upsert=True,
    )


async def _get_next_button_controls():
    stored = await _get_admin_config_value('next_button_controls')
    if not isinstance(stored, dict):
        return dict(NEXT_BUTTON_DEFAULTS)
    merged = dict(NEXT_BUTTON_DEFAULTS)
    merged.update({k: bool(v) for k, v in stored.items() if k in NEXT_BUTTON_DEFAULTS})
    return merged


@router.post('/verify-password')
async def verify_ops_password(req: OpsPasswordReq):
    stored_password = await _get_admin_config_value('ops_password')
    if not stored_password:
        stored_password = 'ops123456'
        await _set_admin_config_value('ops_password', stored_password)

    input_password = str(req.password or '').strip()
    if input_password == str(stored_password).strip():
        return {'success': True}
    return {'success': False, 'message': '密码错误'}


@router.get('/next-buttons')
async def get_next_button_controls():
    controls = await _get_next_button_controls()
    return {'success': True, 'controls': controls}


@router.post('/next-buttons/{button_key}')
async def set_next_button_control(button_key: str, req: ButtonToggleReq):
    if button_key not in NEXT_BUTTON_DEFAULTS:
        raise HTTPException(status_code=400, detail='invalid button key')

    controls = await _get_next_button_controls()
    controls[button_key] = bool(req.enabled)
    await _set_admin_config_value('next_button_controls', controls)

    await ws_manager.notify_students(
        {
            'action': 'NEXT_BUTTON_CONTROL_UPDATE',
            'key': button_key,
            'enabled': controls[button_key],
            'controls': controls,
        }
    )
    return {'success': True, 'controls': controls}