import asyncio
import websockets
import disnake
from disnake.ext import commands
import json



connected = set()  # WebSocket клиенты


# --- WebSocket --- #
async def handle_client(websocket):
    connected.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)


async def send_to_clients(data):
    if not connected:
        return
    disconnected_clients = []
    for client in connected:
        try:
            await client.send(data)
        except (websockets.ConnectionClosed, ConnectionResetError):
            disconnected_clients.append(client)
    for client in disconnected_clients:
        connected.discard(client)


# --- Disnake Bot --- #
intents = disnake.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # обязательно для чтения текста сообщений

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.event
async def on_message(message):
    if message.channel.id not in [1449454381404520682, 1449453871633268957, 1446564111298203780]:
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
            await send_to_clients(json_data)


# --- Main --- #
async def main():
    bot_token = (
        "token"
    )
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("WebSocket ws://0.0.0.0:8765")
        await bot.start(bot_token)


if __name__ == "__main__":
    asyncio.run(main())
