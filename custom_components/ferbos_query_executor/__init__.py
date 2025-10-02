from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.components import websocket_api
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
import aiosqlite
from pathlib import Path
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _run_sqlite_query(hass: HomeAssistant, args: dict) -> dict:
    """Execute SQLite query against Home Assistant database"""
    query: str | None = (args or {}).get("query")
    params = (args or {}).get("params") or []
    if not query:
        return {"success": False, "error": {"code": "invalid", "message": "Missing query"}}

    db_path = Path(hass.config.path("home-assistant_v2.db"))
    if not db_path.exists():
        return {"success": False, "error": {"code": "not_found", "message": f"DB not found: {db_path}"}}

    try:
        async with aiosqlite.connect(db_path.as_posix()) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            is_select = query.strip().lower().startswith("select")
            if is_select:
                rows = await cursor.fetchall()
                await cursor.close()
                result = [dict(r) for r in rows]
                return {"success": True, "data": result}
            else:
                await db.commit()
                rowcount = cursor.rowcount
                lastrowid = cursor.lastrowid
                await cursor.close()
                return {"success": True, "data": {"rowcount": rowcount, "lastrowid": lastrowid}}
    except Exception as exc:
        return {"success": False, "error": {"code": "sqlite_error", "message": str(exc)}}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Ferbos Query Executor via YAML configuration."""
    @websocket_api.websocket_command({
        "type": "ferbos/query",
        "id": int,
        vol.Optional("args"): dict,
        vol.Optional("query"): cv.string,
        vol.Optional("params"): list,
    })
    @websocket_api.async_response
    async def ws_ferbos_query(hass, connection, msg):
        # Normalize payload
        args = msg.get("args")
        if args is None:
            args = {
                "query": msg.get("query"),
                "params": msg.get("params") or [],
            }
        result = await _run_sqlite_query(hass, args)
        connection.send_result(msg["id"], result)

    websocket_api.async_register_command(hass, ws_ferbos_query)
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up Ferbos Query Executor from a config entry."""
    @websocket_api.websocket_command({
        "type": "ferbos/query",
        "id": int,
        vol.Optional("args"): dict,
        vol.Optional("query"): cv.string,
        vol.Optional("params"): list,
    })
    @websocket_api.async_response
    async def ws_ferbos_query(hass, connection, msg):
        args = msg.get("args") or {"query": msg.get("query"), "params": msg.get("params") or []}
        result = await _run_sqlite_query(hass, args)
        connection.send_result(msg["id"], result)

    websocket_api.async_register_command(hass, ws_ferbos_query)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    return True
