import asyncio
import json
import websockets
import disnake
from disnake.ext import commands

connected = {}  # websocket -> user info

async def get_connected_clients():
    """Возвращает список всех подключённых клиентов."""
    return list(connected.values())

# ---------- WebSocket ---------- #

async def send_to_all(data: str):
    if not connected:
        return

    for client in list(connected):
        try:
            print(data)
            await client.send(data)
        except (websockets.ConnectionClosed, ConnectionResetError):
            connected.pop(client, None)

async def handle_client(websocket):
    user = "unknown"  # <-- гарантируем, что переменная всегда определена
    try:
        raw = await websocket.recv()
        hello = json.loads(raw)
        user = hello.get("user", "unknown")

        connected[websocket] = {"user": user}
        print(f"🔌 WS connected: {user}")
        print("Connected clients:", connected)

        clients = list(connected.values())
        await send_to_all(json.dumps({"type": "clients_list", "data": clients}))

        while True:
            msg = await websocket.recv()
            print(f"Received from {user}: {msg}")

    except websockets.ConnectionClosed as e:
        print(f"WS closed: {user} ({e.code} - {e.reason})")
    except Exception as e:
        print("WS error:", e)
    finally:
        connected.pop(websocket, None)
        print(f"❌ WS disconnected: {user}")

# ---------- Discord Bot ---------- #
intents = disnake.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"🤖 Bot logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.channel.id not in [
        1449454381404520682,
        1449453871633268957,
        1446564111298203780,
        1446564138720690348,
    ]:
        return

    print(f"Message in: {message.channel.name}")

    for embed in message.embeds:
        jobid = None
        money = None
        name = embed.title.replace("**", "").strip()
        joiner = "zabei"

        for field in embed.fields:
            clean_value = field.value.replace("```", "").strip()
            if field.name == "🆔 Job ID":
                jobid = clean_value
            elif field.name == "💰 Money/s":
                money = (
                    clean_value.replace("$", "")
                    .replace(",", "")
                    .replace("/s", "")
                    .strip()
                )

        if jobid and money and name:
            data = {"jobid": jobid, "money": money, "name": name, "joiner": joiner}
            print(data)
            json_data = json.dumps(data)
            await send_to_all(json_data)


# ---------- Main ---------- #
async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("🌐 WebSocket started")

        await bot.start(
            ".Gc28k2.LE9tiEQ7GxioO0hq5GgNuPrOszb0iO2NtJCNhQ"
        )


asyncio.run(main())
