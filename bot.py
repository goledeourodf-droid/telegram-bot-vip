from telethon import TelegramClient, events
import asyncio
import time
import datetime
import os
import re
import requests

# =========================
# GARANTIR PASTA DOWNLOADS
# =========================

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Limpar arquivos antigos ao iniciar
for file in os.listdir("downloads"):
    caminho = os.path.join("downloads", file)
    if os.path.isfile(caminho):
        os.remove(caminho)

# =========================
# CONFIGURAÇÕES
# =========================

api_id = 38493557
api_hash = 'a2d2c39d0edf0fa4215b7d80f38a7eaf'

grupos_origem = [
    -167117841,
    -1003751501506,
    -3889254760
]

canal_destino = -1003609621801
canal_publico = -1003768135396

paste_ee_api_key = "ayYqXBwrZ5cpGh25NTqgpAjAmEt5TlMsupvniX28Z"

bot_token = "8602342926:AAGKPRpjRmY_XDWxU_AhIZLtWDCgsC4aBqc"

palavras_hotmail = [r"HOTMA!LS", r"HOT", r"MICROSOFT"]
palavras_mix = [r"M!X", r"MIX"]

# =========================
# MENSAGEM PREMIUM
# =========================

mensagem_premium = """⚠️ Stop wasting time with weak or reused lines — upgrade to PRIVATE premium data now.

💻 PRIVATE — Premium Access

💲 Pricing Plans:

🟢 3 Days  : 7$ (Trial)
🟢 1 Week  : 12$
🟢 2 Weeks : 25$
🟢 1 Month : 35$
🟢 3 Months: 70$
🟢 1 Year  : 200$ ⭐

💳 Payment Method: Crypto Only

📩 Secure your access now:
@LpbCloud
"""

# =========================
# DETECTAR TIPO
# =========================

def detectar_tipo(nome):

    nome = nome.upper()

    for padrao in palavras_hotmail:
        if re.search(padrao, nome):
            return "HOTMAIL"

    for padrao in palavras_mix:
        if re.search(padrao, nome):
            return "MIX"

    return "OUTROS"

# =========================
# PASTEEE
# =========================

def enviar_para_paste_ee(conteudo, nome_arquivo):

    url = "https://api.paste.ee/v1/pastes"

    headers = {
        "X-Auth-Token": paste_ee_api_key,
        "Content-Type": "application/json"
    }

    max_chars = 500000

    if len(conteudo) > max_chars:
        conteudo = conteudo[:max_chars]

    data = {
        "sections": [
            {
                "name": nome_arquivo,
                "syntax": "text",
                "contents": conteudo
            }
        ]
    }

    try:

        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=60
        )

        if response.status_code != 201:
            print("Erro Paste.ee:", response.text)
            return None

        result = response.json()

        return result["link"]

    except Exception as e:

        print("Erro ao enviar para Paste.ee:", e)

        return None

# =========================
# AVISO IMEDIATO
# =========================

def aviso_imediato(chat_id, nome_arquivo):

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    texto = f"""🟢 NEW VIP UPLOAD DETECTED

📄 FILE: {nome_arquivo}

💻 VIP ACCESS PLANS:

🟢 1 Week  : 12$
🟢 2 Weeks : 25$
🟢 1 Month : 35$

📩 Contact:
@LpbCloud
"""

    payload = {
        "chat_id": chat_id,
        "text": texto
    }

    try:
        requests.post(url, json=payload)

    except Exception as e:
        print("Erro aviso imediato:", e)

# =========================
# BOTÃO DOWNLOAD
# =========================

def enviar_mensagem_bot(chat_id, texto, link):

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": texto,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "🟢 DOWNLOAD FILE",
                        "url": link
                    }
                ]
            ]
        }
    }

    try:
        requests.post(url, json=payload)

    except Exception as e:
        print("Erro ao enviar mensagem bot:", e)

# =========================
# ENVIO COM DELAY
# =========================

async def enviar_publico_apos_delay(
    linhas,
    nome_arquivo,
    qtd_linhas,
    tipo
):

    link = await asyncio.to_thread(
        enviar_para_paste_ee,
        "".join(linhas),
        nome_arquivo
    )

    if link:

        print("Arquivo hospedado no Paste.ee:", link)

        await asyncio.sleep(1800)  # 30 minutos

        mensagem_publica = f"""🟢 SYSTEM UPDATE READY

┌─[ LPB CLOUD NODE ]

├── 📄 FILE : {nome_arquivo}
├── 📊 LINES: {qtd_linhas}
├── 📁 TYPE : {tipo}

└── STATUS : READY FOR DOWNLOAD

🔥 VIP received this before public release

⚠️ This file was released HOURS AGO inside VIP.

💻 For immediate access to new files:

📩 JOIN VIP:
@LpbCloud
"""

        await asyncio.to_thread(
            enviar_mensagem_bot,
            canal_publico,
            mensagem_publica,
            link
        )

# =========================
# CLIENT TELEGRAM
# =========================

client = TelegramClient(
    'session',
    api_id,
    api_hash,
    auto_reconnect=True
)

@client.on(events.NewMessage(chats=grupos_origem))
async def handler(event):

    try:

        if (
            event.file
            and event.file.name
            and event.file.name.upper().endswith('.TXT')
        ):

            nome_original = event.file.name.upper()

            print("Origem:", event.chat_id)
            print("Arquivo detectado:", nome_original)

            caminho = await event.download_media(file='downloads/')

            with open(
                caminho,
                'r',
                encoding='utf-8',
                errors='ignore'
            ) as f:

                linhas = f.readlines()

            tipo = detectar_tipo(nome_original)

            if tipo == "OUTROS":
                return

            if event.chat_id == -1003751501506:

                linhas = [mensagem_premium + "\n"] + linhas[25:]

            else:

                linhas = [mensagem_premium + "\n"] + linhas

            qtd_linhas = len(linhas)

            novo_nome = f"[{qtd_linhas}]LpBCLOUD_{tipo}.txt"

            novo_caminho = os.path.join(
                'downloads',
                novo_nome
            )

            with open(
                novo_caminho,
                'w',
                encoding='utf-8',
                errors='ignore'
            ) as f:
                f.writelines(linhas)

            await client.send_file(
                canal_destino,
                novo_caminho,
                force_document=True
            )

            print("Enviado para canal VIP como:", novo_nome)

            await asyncio.to_thread(
                aviso_imediato,
                canal_publico,
                novo_nome
            )

            if os.path.exists(novo_caminho):
                os.remove(novo_caminho)

            asyncio.create_task(
                enviar_publico_apos_delay(
                    linhas,
                    novo_nome,
                    qtd_linhas,
                    tipo
                )
            )

    except Exception as e:

        print("Erro no handler:", e)

# =========================
# INICIAR BOT (FINAL CORRETO)
# =========================

async def iniciar_cliente():

    print("Conectando ao Telegram...")

    await client.start(bot_token=bot_token)

    print("Rodando...")

    async def heartbeat():

        while True:

            print(
                "Bot ativo:",
                datetime.datetime.now().strftime("%H:%M:%S")
            )

            await asyncio.sleep(600)

    asyncio.create_task(heartbeat())

    await client.run_until_disconnected()

# ✅ FINAL DEFINITIVO

if __name__ == "__main__":

    while True:

        try:

            asyncio.run(iniciar_cliente())

        except Exception as e:

            print("Erro geral:", e)
            print("Reiniciando em 5s...")
            time.sleep(5)
