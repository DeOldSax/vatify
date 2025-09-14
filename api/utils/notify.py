# utils/notify.py
import os, json, httpx
from core.config import settings

WEBHOOK = settings.SLACK_WEBHOOK_URL

async def notify(title: str, payload: dict):
    """Send a lightweight Slack message"""
    if not WEBHOOK:
        return
    text = f"*{title}*\n```{json.dumps(payload, indent=2, ensure_ascii=False)}```"
    async with httpx.AsyncClient(timeout=8) as c:
        await c.post(WEBHOOK, json={"text": text})
