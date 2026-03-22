#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#
#  WPPConnect Admin - Echo Bot (Webhook Mode)
#
#  PT: Bot de eco simples que repete todas as mensagens recebidas.
#      Utiliza webhooks do WPPConnect Server para receber mensagens em
#      tempo real e a API do backend SaaS para enviar respostas.
#
#  EN: Simple echo bot that repeats all received messages.
#      Uses WPPConnect Server webhooks to receive messages in real time
#      and the SaaS backend API to send responses.
#
#  ES: Bot de eco simple que repite todos los mensajes recibidos.
#      Utiliza webhooks del WPPConnect Server para recibir mensajes en
#      tiempo real y la API del backend SaaS para enviar respuestas.
#
# =============================================================================
#
#  PT: COMO FUNCIONA:
#      1. O bot inicia um servidor HTTP local (Flask) para receber webhooks
#      2. Verifica se a sessao WhatsApp existe e se tem permissao
#      3. O WPPConnect Server envia mensagens via POST para /webhook
#      4. Para cada mensagem nova recebida, envia a mesma mensagem de volta
#      5. Nao precisa resolver @lid — o webhook ja traz o numero @c.us
#
#  EN: HOW IT WORKS:
#      1. The bot starts a local HTTP server (Flask) to receive webhooks
#      2. Checks if the WhatsApp session exists and has permissions
#      3. WPPConnect Server sends messages via POST to /webhook
#      4. For each new received message, sends the same message back
#      5. No @lid resolution needed — the webhook already provides @c.us
#
#  ES: COMO FUNCIONA:
#      1. El bot inicia un servidor HTTP local (Flask) para recibir webhooks
#      2. Verifica si la sesion de WhatsApp existe y tiene permisos
#      3. WPPConnect Server envia mensajes via POST a /webhook
#      4. Para cada mensaje nuevo recibido, envia el mismo mensaje de vuelta
#      5. No necesita resolver @lid — el webhook ya trae el numero @c.us
#
# =============================================================================
#
#  PT: ARQUITETURA:
#
#      Celular WhatsApp  <-->  WPPConnect Server  --(webhook)--> Este Bot
#      (dispositivo)           (zapi.monitor)                    (Flask)
#                                     ^                            |
#                                     |                            |
#                              Backend SaaS  <--(send-message)-----+
#                              (zapi.vilios)
#
#  EN: ARCHITECTURE:
#
#      WhatsApp Phone  <-->  WPPConnect Server  --(webhook)--> This Bot
#      (device)              (zapi.monitor)                    (Flask)
#                                   ^                            |
#                                   |                            |
#                            SaaS Backend  <--(send-message)-----+
#                            (zapi.vilios)
#
#  ES: ARQUITECTURA:
#
#      Celular WhatsApp  <-->  WPPConnect Server  --(webhook)--> Este Bot
#      (dispositivo)           (zapi.monitor)                    (Flask)
#                                     ^                            |
#                                     |                            |
#                              Backend SaaS  <--(send-message)-----+
#                              (zapi.vilios)
#
# =============================================================================
#
#  PT: REQUISITOS:
#      pip install flask requests
#
#  EN: REQUIREMENTS:
#      pip install flask requests
#
#  ES: REQUISITOS:
#      pip install flask requests
#
# =============================================================================

import os
import sys

import requests
from flask import Flask, request as flask_request, jsonify
from urllib.parse import quote


# =============================================================================
# PT: CONFIGURACAO - Altere os valores abaixo conforme seu ambiente
# EN: CONFIGURATION - Change the values below according to your environment
# ES: CONFIGURACION - Cambie los valores a continuacion segun su entorno
# =============================================================================

# PT: URL base do backend SaaS da plataforma WPPConnect Admin.
# EN: Base URL of the WPPConnect Admin SaaS backend.
# ES: URL base del backend SaaS de la plataforma WPPConnect Admin.
SAAS_API_URL = "https://zapi.vilios.com.br"

# PT: Chave de API (API Key) gerada na plataforma WPPConnect Admin.
#     ATENCAO: Em producao, use variaveis de ambiente em vez de hardcode!
# EN: API Key generated on the WPPConnect Admin platform.
#     WARNING: In production, use environment variables instead of hardcoding!
# ES: Clave de API generada en la plataforma WPPConnect Admin.
#     ATENCION: En produccion, use variables de entorno en vez de hardcode!
API_KEY = "put your api key here"

# PT: Nome da sessao WhatsApp ativa na plataforma.
# EN: Name of the active WhatsApp session on the platform.
# ES: Nombre de la sesion de WhatsApp activa en la plataforma.
SESSION_NAME = "ZapadminBot"

# PT: Prefixo adicionado antes da mensagem de eco.
# EN: Prefix added before the echo message.
# ES: Prefijo agregado antes del mensaje de eco.
ECHO_PREFIX = "Echo: "

# PT: Host e porta onde o servidor webhook vai escutar.
#     Use 0.0.0.0 para aceitar conexoes de qualquer interface de rede.
# EN: Host and port where the webhook server will listen.
#     Use 0.0.0.0 to accept connections from any network interface.
# ES: Host y puerto donde el servidor webhook va a escuchar.
#     Use 0.0.0.0 para aceptar conexiones de cualquier interfaz de red.
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = 5001

# PT: URL publica opcional do webhook (ex.: ngrok, cloudflared).
#     Defina via variavel de ambiente PUBLIC_WEBHOOK_URL.
# EN: Optional public webhook URL (e.g., ngrok, cloudflared).
#     Set it via PUBLIC_WEBHOOK_URL environment variable.
# ES: URL publica opcional del webhook (ej.: ngrok, cloudflared).
#     Definala via variable de entorno PUBLIC_WEBHOOK_URL.
PUBLIC_WEBHOOK_URL = os.getenv("PUBLIC_WEBHOOK_URL", "").strip()


# =============================================================================
# PT: FUNCOES AUXILIARES
# EN: HELPER FUNCTIONS
# ES: FUNCIONES AUXILIARES
# =============================================================================

def get_headers():
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def wpp_url(path):
    session_encoded = quote(SESSION_NAME, safe="")
    return f"{SAAS_API_URL}/api/{session_encoded}/{path}"


def saas_url(path):
    return f"{SAAS_API_URL}/api/v1/{path}"


# =============================================================================
# PT: FUNCOES DA API
# EN: API FUNCTIONS
# ES: FUNCIONES DE LA API
# =============================================================================

def check_connection():
    resp = requests.get(
        saas_url("session-permissions/my-sessions"),
        headers=get_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    sessions = resp.json()

    for s in sessions:
        if s.get("session_name") == SESSION_NAME:
            return {
                "found": True,
                "can_read": s.get("can_read", False),
                "can_send": s.get("can_send", False),
            }

    return {"found": False, "can_read": False, "can_send": False}


def send_text(phone, message, is_group=False):
    resp = requests.post(
        wpp_url("send-message"),
        headers=get_headers(),
        json={
            "phone": phone,
            "message": message,
            "isGroup": is_group,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# =============================================================================
# PT: SERVIDOR WEBHOOK (Flask)
# EN: WEBHOOK SERVER (Flask)
# ES: SERVIDOR WEBHOOK (Flask)
# =============================================================================

app = Flask(__name__)

# PT: Flag para controlar se o bot tem permissao de enviar
# EN: Flag to control whether the bot has send permission
_can_send = False


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/webhook", methods=["POST", "OPTIONS"])
def webhook_handler():
    if flask_request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = flask_request.get_json(silent=True)
    if not data:
        return jsonify({"status": "ignored", "reason": "no payload"}), 200

    event = data.get("event", "")
    session = data.get("session", "")

    print(f"  EVENT: {event} | session={session}")

    # PT: Processar apenas eventos de mensagem recebida
    # EN: Only process incoming message events
    if event != "onmessage":
        return jsonify({"status": "ignored", "reason": f"event={event}"}), 200

    # PT: Filtrar por sessao
    # EN: Filter by session
    if session and session != SESSION_NAME:
        return jsonify({"status": "ignored", "reason": f"session={session}"}), 200

    # PT: Ignorar mensagens enviadas por mim
    # EN: Skip messages sent by me
    if data.get("fromMe", False):
        return jsonify({"status": "ignored", "reason": "fromMe"}), 200

    # PT: Processar apenas mensagens de texto
    # EN: Process only text messages
    msg_type = data.get("type", "")
    if msg_type != "chat":
        return jsonify({"status": "ignored", "reason": f"type={msg_type}"}), 200

    # PT: Ignorar mensagens vazias
    # EN: Skip empty messages
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"status": "ignored", "reason": "empty"}), 200

    # PT: Extrair telefone do remetente — o webhook ja traz no formato @c.us!
    # EN: Extract sender phone — the webhook already provides @c.us format!
    phone = data.get("from", "")
    if not phone or "status@broadcast" in phone:
        return jsonify({"status": "ignored", "reason": "no sender"}), 200

    sender_obj = data.get("sender") or {}
    sender_name = (
        data.get("notifyName")
        or sender_obj.get("pushname")
        or sender_obj.get("name")
        or phone
    )
    is_group = data.get("isGroupMsg", False) or "@g.us" in phone

    print(f"  IN  [{sender_name}] {phone}: {body}")

    if not _can_send:
        print(f"  -> (no send permission, skipping echo)")
        return jsonify({"status": "received", "echo": False}), 200

    echo_text = f"{ECHO_PREFIX}{body}"
    try:
        send_text(phone, echo_text, is_group=is_group)
        print(f"  OUT [{sender_name}] Bot: {echo_text}")
    except Exception as e:
        print(f"  ERR sending echo to {phone}: {e}")

    return jsonify({"status": "processed", "echo": True}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "session": SESSION_NAME}), 200


# =============================================================================
# PT: FUNCAO PRINCIPAL
# EN: MAIN FUNCTION
# ES: FUNCION PRINCIPAL
# =============================================================================

def main():
    global _can_send

    print("=" * 60)
    print("  WPPConnect Admin - Echo Bot (Webhook)")
    print("=" * 60)
    print(f"  API:      {SAAS_API_URL}")
    print(f"  Session:  {SESSION_NAME}")
    print(f"  Prefix:   {ECHO_PREFIX}")
    print(f"  Webhook:  http://{WEBHOOK_HOST}:{WEBHOOK_PORT}/webhook")
    print("=" * 60)

    # ------------------------------------------------------------------
    # PT: Etapa 1 - Verificar conexao e permissoes
    # EN: Step 1 - Check connection and permissions
    # ------------------------------------------------------------------
    print("\n[1/2] Checking connection and permissions...")

    try:
        status = check_connection()
    except requests.exceptions.ConnectionError:
        print(f"  ERROR: Could not connect to {SAAS_API_URL}")
        print("  Check if the URL is correct and the server is running.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            print("  ERROR: Invalid API Key (401 Unauthorized).")
            print("  Check your API_KEY value.")
        elif e.response is not None and e.response.status_code == 403:
            try:
                detail = e.response.json().get("detail", "Forbidden")
            except Exception:
                detail = e.response.text
            print("  ERROR: API Key lacks necessary scopes (403 Forbidden).")
            print(f"  Server detail: {detail}")
            print("  -> Please generate a new API Key with the required scopes.")
            sys.exit(1)
        else:
            print(f"  ERROR: HTTP {e.response.status_code if e.response else '?'}")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    if not status["found"]:
        print(f"  ERROR: Session '{SESSION_NAME}' not found in your permissions.")
        sys.exit(1)

    if not status["can_read"]:
        print(f"  ERROR: No read permission for session '{SESSION_NAME}'.")
        sys.exit(1)

    _can_send = status["can_send"]

    if not _can_send:
        print(f"  WARNING: No send permission for session '{SESSION_NAME}'.")
        print("  The bot will log messages but will NOT echo them back.")
    else:
        print(f"  OK: Session '{SESSION_NAME}' - read and send permissions confirmed.")

    # ------------------------------------------------------------------
    # PT: Etapa 2 - Verificar se a sessao esta conectada ao WhatsApp
    # EN: Step 2 - Check if the session is connected to WhatsApp
    # ------------------------------------------------------------------
    print("\n[2/2] Checking WhatsApp connection status...")

    try:
        resp = requests.get(
            wpp_url("check-connection-session"),
            headers=get_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        conn_data = resp.json()
        is_connected = conn_data.get("status") is True or conn_data.get("message") == "Connected"

        if is_connected:
            print("  OK: WhatsApp session is CONNECTED.")
        else:
            print("  WARNING: Session may not be connected.")
            print(f"  Server response: {conn_data}")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            try:
                detail = e.response.json().get("detail", "Forbidden")
            except Exception:
                detail = e.response.text
            print(f"\n  [!] CRITICAL ERROR: {detail}")
            print("  [!] Please generate a new API Key with the necessary scopes.")
            sys.exit(1)
        print(f"  WARNING: Could not verify WhatsApp status: {e}")
    except Exception as e:
        print(f"  WARNING: Could not verify WhatsApp status: {e}")

    # ------------------------------------------------------------------
    # PT: Etapa 3 - Iniciar servidor webhook
    # EN: Step 3 - Start webhook server
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Bot is running! Waiting for webhook events...")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    print(f"\n  Configure the webhook URL in WPPConnect Server or Admin:")
    if PUBLIC_WEBHOOK_URL:
        print(f"    {PUBLIC_WEBHOOK_URL}")
    else:
        print(f"    http://YOUR_IP:{WEBHOOK_PORT}/webhook")
    print(f"\n  For local testing (same machine as WPPConnect Server):")
    print(f"    http://localhost:{WEBHOOK_PORT}/webhook")
    print()

    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT, debug=False)


# =============================================================================
if __name__ == "__main__":
    main()
