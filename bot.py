from telethon import TelegramClient, events
import asyncio
import datetime
import os
import re
import requests

# =========================
# PASTA DOWNLOADS
# =========================

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# =========================
# CONFIG
# =========================

api_id = 38493557
api_hash = 'a2d2c39d0edf0fa4215b7d80f38a7eaf'

grupos_origem = [
    -167117841,
    -1003751501506,
    -1003889254760
]

canal_destino = -1003609621801
canal_publico = -1003768135396

paste_ee_api_key = "ayYqXBwrZ5cpGh25NTqgpAjAmEt5TlMsupvniX28Z"

bot_token_publico = "8602342926:AAGKPRpjRmY_XDWxU_AhIZLtWDCgsC4aBqc"

palavras_hotmail = [r"HOTMA!LS", r"HOT", r"MICROSOFT"]
palavras_mix = [r"M!X", r"MIX"]

mensagem_premium = """⚠️ Stop wasting time with weak or reused lines — upgrade to PRIVATE premium data now.

💻 PRIVATE — Premium Access

💲 Pricing Plans:

🟢 3 Days  : 7$
🟢 1 Week  : 12$
🟢 2 Weeks : 25$
🟢 1 Month : 35$
🟢 3 Months: 70$
🟢 1 Year  : 200$

📩 Contact:
@LpbCloud
"""

# =========================
# CLIENT
# =========================

client = TelegramClient(
    'session',
    api_id,
    api_hash
)

# =========================
# DETECTAR TIPO
# =========================

def detectar_tipo(nome):

    nome = nome.upper()

    for p in palavras_hotmail:
        if re.search(p, nome):
            return "HOTMAIL"

    for p in palavras_mix:
        if re.search(p, nome):
            return "MIX"

    return "OUTROS"

# =========================
# PASTEEE
# =========================

def enviar_paste(conteudo, nome):

    url = "https://api.paste.ee/v1/pastes"

    headers = {
        "X-Auth-Token": paste_ee_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "sections": [{
            "name": nome,
            "syntax": "text",
            "contents": conteudo[:500000]
        }]
    }

    try:

        r = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=60
        )

        if r.status_code == 201:
            return r.json()["link"]

        print("Erro paste:", r.text)

    except Exception as e:

        print("Erro paste:", e)

    return None

# =========================
# HANDLER
# =========================

@client.on(events.NewMessage(chats=grupos_origem))
async def handler(event):

    try:

        if not event.file:
            return

        if not event.file.name:
            return

        if not event.file.name.upper().endswith(".TXT"):
            return

        nome_original = event.file.name.upper()

        print("Origem:", event.chat_id)
        print("Arquivo:", nome_original)

        caminho = await event.download_media(file="downloads/")

        with open(
            caminho,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            linhas = f.readlines()

        tipo = detectar_tipo(nome_original)

        if tipo == "OUTROS":
            return

        # REMOVER 25 LINHAS DO NOVO CANAL

        if event.chat_id == -1003751501506:

            linhas = [mensagem_premium+"\n"] + linhas[25:]

        else:

            linhas = [mensagem_premium+"\n"] + linhas

        qtd = len(linhas)

        nome_novo = f"[{qtd}]LpBCLOUD_{tipo}.txt"

        novo = os.path.join("downloads", nome_novo)

        with open(novo,"w",encoding="utf-8") as f:
            f.writelines(linhas)

        # ENVIO VIP

        await client.send_file(
            canal_destino,
            novo
        )

        print("Enviado VIP:", nome_novo)

        # AVISO IMEDIATO PUBLICO

        aviso = f"""🟢 NEW VIP UPLOAD DETECTED

📄 FILE: {nome_novo}

💻 VIP ACCESS PLANS:

🟢 1 Week  : 12$
🟢 2 Weeks : 25$
🟢 1 Month : 35$

📩 Contact:
@LpbCloud
"""

        requests.post(
            f"https://api.telegram.org/bot{bot_token_publico}/sendMessage",
            json={
                "chat_id": canal_publico,
                "text": aviso
            }
        )

        print("Aviso imediato enviado")

        os.remove(novo)

        # DELAY PUBLICO

        async def publico():

            link = await asyncio.to_thread(
                enviar_paste,
                "".join(linhas),
                nome_novo
            )

            if link:

                print("Link:", link)

                print("Aguardando 30 minutos...")

                await asyncio.sleep(1800)

                msg = f"""🟢 SYSTEM READY

FILE: {nome_novo}
LINES: {qtd}
TYPE: {tipo}

🔥 VIP received this before public release

📩 JOIN VIP:
@LpbCloud
"""

                requests.post(
                    f"https://api.telegram.org/bot{bot_token_publico}/sendMessage",
                    json={
                        "chat_id": canal_publico,
                        "text": msg,
                        "reply_markup": {
                            "inline_keyboard":[[
                                {
                                    "text":"🟢 DOWNLOAD FILE",
                                    "url":link
                                }
                            ]]
                        }
                    }
                )

                print("Mensagem publica enviada")

        asyncio.create_task(publico())

    except Exception as e:

        print("Erro handler:", e)

# =========================
# START
# =========================

async def main():

    print("Conectando...")

    await client.start()

    print("Rodando...")

    while True:

        print(
            "Bot ativo:",
            datetime.datetime.now().strftime("%H:%M:%S")
        )

        await asyncio.sleep(600)

# =========================
# RUN
# =========================

with client:
    client.loop.run_until_complete(main())
