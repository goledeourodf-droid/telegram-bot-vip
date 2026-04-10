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

# Limpar arquivos antigos
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

def aviso_imediato(nome_arquivo):

    url = f"https://api.telegram.org/bot8602342926:AAGKPRpjRmY_XDWxU_AhIZLtWDCgsC4aBqc/sendMessage"

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
        "chat_id": canal_publico,
        "text": texto
    }

    requests.post(url, json=payload)

# =========================
# DELAY PUBLICO
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

        print("Arquivo hospedado:", link)

        await asyncio.sleep(1800)

        mensagem = f"""🟢 SYSTEM UPDATE READY

📄 FILE : {nome_arquivo}
📊 LINES: {qtd_linhas}
📁 TYPE : {tipo}

🔥 VIP received this before public release

⚠️ This file was released HOURS AGO inside VIP.

📩 JOIN VIP:
@LpbCloud
"""

        url = f"https://api.telegram.org/bot8602342926:AAGKPRpjRmY_XDWxU_AhIZLtWDCgsC4aBqc/sendMessage"

        payload = {
            "chat_id": canal_publico,
            "text": mensagem,
            "reply_markup": {
                "inline_keyboard": [[
                    {
                        "text": "🟢 DOWNLOAD FILE",
                        "url": link
                    }
                ]]
            }
        }

        requests.post(url, json=payload)

# =========================
# CLIENT
# =========================

client = TelegramClient(
    'session',
    api_id,
    api_hash
)

@client.on(events.NewMessage(chats=grupos_origem))
async def handler(event):

    try:

        if event.file and event.file.name:

            if not event.file.name.upper().endswith('.TXT'):
                return

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
                novo_caminho
            )

            print("Enviado VIP:", novo_nome)

            aviso_imediato(novo_nome)

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

        print("Erro:", e)

# =========================
# INICIAR CLIENTE
# =========================

async def main():

    print("Conectando ao Telegram...")

    await client.start()

    print("Rodando...")

    while True:

        print(
            "Bot ativo:",
            datetime.datetime.now().strftime("%H:%M:%S")
        )

        await asyncio.sleep(600)

async def run():

    await asyncio.gather(
        main(),
        client.run_until_disconnected()
    )

if __name__ == "__main__":

    while True:

        try:

            asyncio.run(run())

        except Exception as e:

            print("Erro geral:", e)
            time.sleep(5)
