import os
from fastapi import FastAPI, Request, Header, HTTPException
import httpx
import asyncio

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SECRET_TOKEN = os.getenv("TELEGRAM_SECRET_TOKEN", "set-this-to-a-random-string")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    if x_telegram_bot_api_secret_token != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid secret token.")

    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    text = data.get("message", {}).get("text")
    if chat_id and text:
        reply = f"You said: {text}"
        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })
    return {"ok": True}
