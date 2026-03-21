#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#
#  WPPConnect Admin - Echo Bot
#
#  PT: Bot de eco simples que repete todas as mensagens recebidas.
#      Utiliza a API do backend SaaS do WPPConnect Admin com autenticacao
#      via API Key (X-API-Key) e faz polling periodico de novas mensagens.
#
#  EN: Simple echo bot that repeats all received messages.
#      Uses the WPPConnect Admin SaaS backend API with API Key
#      authentication (X-API-Key) and periodic polling for new messages.
#
#  ES: Bot de eco simple que repite todos los mensajes recibidos.
#      Utiliza la API del backend SaaS de WPPConnect Admin con autenticacion
#      via API Key (X-API-Key) y polling periodico de nuevos mensajes.
#
# =============================================================================
#
#  PT: COMO FUNCIONA:
#      1. O bot se conecta ao backend SaaS do WPPConnect Admin
#      2. Verifica se a sessao WhatsApp existe e se tem permissao
#      3. A cada N segundos, busca todos os chats com mensagens nao lidas
#      4. Para cada mensagem nova recebida, envia a mesma mensagem de volta
#      5. Mensagens ja processadas sao armazenadas em memoria para evitar
#         duplicatas
#
#  EN: HOW IT WORKS:
#      1. The bot connects to the WPPConnect Admin SaaS backend
#      2. Checks if the WhatsApp session exists and has permissions
#      3. Every N seconds, fetches all chats with unread messages
#      4. For each new received message, sends the same message back
#      5. Already processed messages are stored in memory to avoid
#         duplicates
#
#  ES: COMO FUNCIONA:
#      1. El bot se conecta al backend SaaS de WPPConnect Admin
#      2. Verifica si la sesion de WhatsApp existe y tiene permisos
#      3. Cada N segundos, busca todos los chats con mensajes no leidos
#      4. Para cada mensaje nuevo recibido, envia el mismo mensaje de vuelta
#      5. Los mensajes ya procesados se almacenan en memoria para evitar
#         duplicados
#
# =============================================================================
#
#  PT: ARQUITETURA:
#
#      Celular WhatsApp  <-->  WPPConnect Server  <-->  Backend SaaS  <-->  Este Bot
#      (dispositivo)           (zapi.monitor)           (zapi.vilios)       (polling)
#
#      O backend SaaS atua como proxy inteligente: recebe a requisicao
#      autenticada com API Key, verifica permissoes e limites, e encaminha
#      para o WPPConnect Server que se comunica diretamente com o WhatsApp.
#
#  EN: ARCHITECTURE:
#
#      WhatsApp Phone  <-->  WPPConnect Server  <-->  SaaS Backend  <-->  This Bot
#      (device)              (zapi.monitor)           (zapi.vilios)       (polling)
#
#      The SaaS backend acts as a smart proxy: receives the API Key
#      authenticated request, checks permissions and limits, and forwards
#      it to the WPPConnect Server which communicates directly with WhatsApp.
#
#  ES: ARQUITECTURA:
#
#      Celular WhatsApp  <-->  WPPConnect Server  <-->  Backend SaaS  <-->  Este Bot
#      (dispositivo)           (zapi.monitor)           (zapi.vilios)       (polling)
#
#      El backend SaaS actua como proxy inteligente: recibe la solicitud
#      autenticada con API Key, verifica permisos y limites, y redirige
#      al WPPConnect Server que se comunica directamente con WhatsApp.
#
# =============================================================================

import sys
import time

import requests
from urllib.parse import quote


# =============================================================================
# PT: CONFIGURACAO - Altere os valores abaixo conforme seu ambiente
# EN: CONFIGURATION - Change the values below according to your environment
# ES: CONFIGURACION - Cambie los valores a continuacion segun su entorno
# =============================================================================

# PT: URL base do backend SaaS da plataforma WPPConnect Admin.
#     Esta e a API que autentica via API Key e faz proxy para o WPPConnect Server.
# EN: Base URL of the WPPConnect Admin SaaS backend.
#     This is the API that authenticates via API Key and proxies to WPPConnect Server.
# ES: URL base del backend SaaS de la plataforma WPPConnect Admin.
#     Esta es la API que autentica via API Key y hace proxy al WPPConnect Server.
SAAS_API_URL = "https://zapi.vilios.com.br"

# PT: Chave de API (API Key) gerada na plataforma WPPConnect Admin.
#     Para gerar sua chave, acesse: Menu lateral > API Keys > Gerar Nova Chave.
#     ATENCAO: Em producao, use variaveis de ambiente em vez de hardcode!
# EN: API Key generated on the WPPConnect Admin platform.
#     To generate your key, go to: Side menu > API Keys > Generate New Key.
#     WARNING: In production, use environment variables instead of hardcoding!
# ES: Clave de API generada en la plataforma WPPConnect Admin.
#     Para generar su clave, vaya a: Menu lateral > API Keys > Generar Nueva Clave.
#     ATENCION: En produccion, use variables de entorno en vez de hardcode!
import os
# API_KEY = "put your secret api key here" # (REMOVIDO: nunca deixe segredo no código)
API_KEY = os.getenv("WPP_API_KEY", "")  # Defina a variável de ambiente WPP_API_KEY com sua chave

# PT: Nome da sessao WhatsApp ativa na plataforma.
#     A sessao deve estar com status "CONECTADO" (verde) para que o bot funcione.
#     Para criar uma sessao: Menu lateral > Sessoes > + Nova Sessao > Escanear QR.
# EN: Name of the active WhatsApp session on the platform.
#     The session must have "CONNECTED" (green) status for the bot to work.
#     To create a session: Side menu > Sessions > + New Session > Scan QR.
# ES: Nombre de la sesion de WhatsApp activa en la plataforma.
#     La sesion debe estar con estado "CONECTADO" (verde) para que el bot funcione.
#     Para crear una sesion: Menu lateral > Sesiones > + Nueva Sesion > Escanear QR.
SESSION_NAME = "Jose Silva"

# PT: Intervalo entre cada verificacao de novas mensagens (em segundos).
#     Valores menores = resposta mais rapida, mas mais consumo de API.
#     Recomendado: 3 a 10 segundos.
# EN: Interval between each check for new messages (in seconds).
#     Lower values = faster response, but more API consumption.
#     Recommended: 3 to 10 seconds.
# ES: Intervalo entre cada verificacion de nuevos mensajes (en segundos).
#     Valores menores = respuesta mas rapida, pero mas consumo de API.
#     Recomendado: 3 a 10 segundos.
POLL_INTERVAL = 5

# PT: Prefixo adicionado antes da mensagem de eco.
#     Ajuda a identificar que a resposta veio do bot.
# EN: Prefix added before the echo message.
#     Helps identify that the response came from the bot.
# ES: Prefijo agregado antes del mensaje de eco.
#     Ayuda a identificar que la respuesta vino del bot.
ECHO_PREFIX = "Echo: "


# =============================================================================
# PT: FUNCOES AUXILIARES
# EN: HELPER FUNCTIONS
# ES: FUNCIONES AUXILIARES
# =============================================================================

def get_headers():
    """
    PT: Retorna os headers HTTP necessarios para autenticacao via API Key.
        O header X-API-Key e o metodo de autenticacao para acesso programatico.
    EN: Returns the HTTP headers required for API Key authentication.
        The X-API-Key header is the authentication method for programmatic access.
    ES: Retorna los headers HTTP necesarios para autenticacion via API Key.
        El header X-API-Key es el metodo de autenticacion para acceso programatico.
    """
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def wpp_url(path):
    """
    PT: Constroi a URL do proxy WPPConnect no backend SaaS.
        O backend recebe em /api/{sessao}/{caminho} e encaminha ao WPPConnect Server.
        O nome da sessao e codificado para URL (espacos viram %20).
    EN: Builds the WPPConnect proxy URL on the SaaS backend.
        The backend receives at /api/{session}/{path} and forwards to WPPConnect Server.
        The session name is URL-encoded (spaces become %20).
    ES: Construye la URL del proxy WPPConnect en el backend SaaS.
        El backend recibe en /api/{sesion}/{ruta} y reenvía al WPPConnect Server.
        El nombre de la sesion se codifica para URL (espacios se vuelven %20).
    """
    session_encoded = quote(SESSION_NAME, safe="")
    return f"{SAAS_API_URL}/api/{session_encoded}/{path}"


def saas_url(path):
    """
    PT: Constroi a URL para endpoints proprios do backend SaaS (nao proxy).
        Usado para verificar permissoes, listar sessoes, etc.
    EN: Builds the URL for SaaS backend own endpoints (not proxy).
        Used to check permissions, list sessions, etc.
    ES: Construye la URL para endpoints propios del backend SaaS (no proxy).
        Usado para verificar permisos, listar sesiones, etc.
    """
    return f"{SAAS_API_URL}/api/v1/{path}"


# =============================================================================
# PT: FUNCOES DA API
# EN: API FUNCTIONS
# ES: FUNCIONES DE LA API
# =============================================================================

def check_connection():
    """
    PT: Verifica se a sessao WhatsApp esta acessivel com a API Key fornecida.
        Consulta o endpoint /my-sessions do backend SaaS para listar as sessoes
        que o usuario da API Key tem permissao de acessar.
        Retorna um dicionario com: found (bool), can_read (bool), can_send (bool).
    EN: Checks if the WhatsApp session is accessible with the provided API Key.
        Queries the /my-sessions endpoint of the SaaS backend to list sessions
        that the API Key user has permission to access.
        Returns a dict with: found (bool), can_read (bool), can_send (bool).
    ES: Verifica si la sesion de WhatsApp es accesible con la API Key proporcionada.
        Consulta el endpoint /my-sessions del backend SaaS para listar las sesiones
        que el usuario de la API Key tiene permiso de acceder.
        Retorna un diccionario con: found (bool), can_read (bool), can_send (bool).
    """
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


def get_all_chats():
    """
    PT: Busca todos os chats da sessao WhatsApp.
        Retorna uma lista de chats, cada um contendo informacoes como:
        - id: identificador do chat (telefone@c.us ou grupo@g.us)
        - name: nome do contato ou grupo
        - unreadCount: quantidade de mensagens nao lidas
        A API WPPConnect retorna no formato { status, response: [...] }.
    EN: Fetches all chats from the WhatsApp session.
        Returns a list of chats, each containing information such as:
        - id: chat identifier (phone@c.us or group@g.us)
        - name: contact or group name
        - unreadCount: number of unread messages
        The WPPConnect API returns in format { status, response: [...] }.
    ES: Busca todos los chats de la sesion de WhatsApp.
        Retorna una lista de chats, cada uno conteniendo informacion como:
        - id: identificador del chat (telefono@c.us o grupo@g.us)
        - name: nombre del contacto o grupo
        - unreadCount: cantidad de mensajes no leidos
        La API WPPConnect retorna en formato { status, response: [...] }.
    """
    resp = requests.get(wpp_url("all-chats"), headers=get_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # PT: A resposta do WPPConnect vem como { status: "success", response: [...] }
    # EN: The WPPConnect response comes as { status: "success", response: [...] }
    # ES: La respuesta de WPPConnect viene como { status: "success", response: [...] }
    if isinstance(data, dict):
        return data.get("response", [])
    return data


def get_messages(phone, count=20):
    """
    PT: Busca as ultimas N mensagens de um chat especifico.
        O parametro phone deve estar no formato do WhatsApp:
        - Contato individual: 5527999999999@c.us
        - Grupo: 120363xxxxx@g.us
    EN: Fetches the last N messages from a specific chat.
        The phone parameter must be in WhatsApp format:
        - Individual contact: 5527999999999@c.us
        - Group: 120363xxxxx@g.us
    ES: Busca los ultimos N mensajes de un chat especifico.
        El parametro phone debe estar en formato de WhatsApp:
        - Contacto individual: 5527999999999@c.us
        - Grupo: 120363xxxxx@g.us
    """
    phone_encoded = quote(phone, safe="")
    resp = requests.get(
        wpp_url(f"all-messages-in-chat/{phone_encoded}"),
        headers=get_headers(),
        params={
            "count": count,
            "includeMe": "true",
            "includeNotifications": "false",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return data.get("response", [])
    return data


def send_text(phone, message, is_group=False):
    """
    PT: Envia uma mensagem de texto para um contato ou grupo.
        O campo isGroup deve ser True para grupos (@g.us) e False para contatos (@c.us).
        A API do WPPConnect Server trata o envio de forma diferente para cada tipo.
    EN: Sends a text message to a contact or group.
        The isGroup field must be True for groups (@g.us) and False for contacts (@c.us).
        The WPPConnect Server API handles sending differently for each type.
    ES: Envia un mensaje de texto a un contacto o grupo.
        El campo isGroup debe ser True para grupos (@g.us) y False para contactos (@c.us).
        La API del WPPConnect Server trata el envio de forma diferente para cada tipo.
    """
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
# PT: FUNCAO PRINCIPAL - Loop de polling do bot
# EN: MAIN FUNCTION - Bot polling loop
# ES: FUNCION PRINCIPAL - Loop de polling del bot
# =============================================================================

def main():
    """
    PT: Funcao principal do echo bot.
        1. Exibe informacoes de configuracao
        2. Valida conexao e permissoes
        3. Inicia loop infinito de polling
        4. Para cada mensagem nova, envia eco de volta
    EN: Main function of the echo bot.
        1. Displays configuration information
        2. Validates connection and permissions
        3. Starts infinite polling loop
        4. For each new message, sends echo back
    ES: Funcion principal del echo bot.
        1. Muestra informacion de configuracion
        2. Valida conexion y permisos
        3. Inicia loop infinito de polling
        4. Para cada mensaje nuevo, envia eco de vuelta
    """
    print("=" * 60)
    print("  WPPConnect Admin - Echo Bot")
    print("=" * 60)
    print(f"  API:      {SAAS_API_URL}")
    print(f"  Session:  {SESSION_NAME}")
    print(f"  Interval: {POLL_INTERVAL}s")
    print(f"  Prefix:   {ECHO_PREFIX}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # PT: Etapa 1 - Verificar conexao e permissoes
    # EN: Step 1 - Check connection and permissions
    # ES: Paso 1 - Verificar conexion y permisos
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
        else:
            print(f"  ERROR: HTTP {e.response.status_code if e.response else '?'}")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    if not status["found"]:
        print(f"  ERROR: Session '{SESSION_NAME}' not found in your permissions.")
        print("  Possible causes:")
        print("    - Session name is incorrect (check spelling and case)")
        print("    - Your API Key user does not have access to this session")
        print("    - The session has not been created yet")
        sys.exit(1)

    if not status["can_read"]:
        print(f"  ERROR: No read permission for session '{SESSION_NAME}'.")
        print("  Ask your administrator to grant read access.")
        sys.exit(1)

    can_send = status["can_send"]

    if not can_send:
        print(f"  WARNING: No send permission for session '{SESSION_NAME}'.")
        print("  The bot will log messages but will NOT echo them back.")
    else:
        print(f"  OK: Session '{SESSION_NAME}' - read and send permissions confirmed.")

    # ------------------------------------------------------------------
    # PT: Etapa 2 - Verificar se a sessao esta conectada ao WhatsApp
    # EN: Step 2 - Check if the session is connected to WhatsApp
    # ES: Paso 2 - Verificar si la sesion esta conectada a WhatsApp
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

        # PT: A resposta varia conforme a versao do WPPConnect Server
        # EN: The response varies depending on the WPPConnect Server version
        # ES: La respuesta varia segun la version del WPPConnect Server
        is_connected = conn_data.get("status") is True or conn_data.get("message") == "Connected"

        if is_connected:
            print("  OK: WhatsApp session is CONNECTED.")
        else:
            print("  WARNING: Session may not be connected.")
            print(f"  Server response: {conn_data}")
            print("  The bot will start anyway, but may not receive messages.")
    except Exception as e:
        print(f"  WARNING: Could not verify WhatsApp status: {e}")
        print("  The bot will start anyway.")

    # ------------------------------------------------------------------
    # PT: Etapa 3 - Iniciar loop de polling
    # EN: Step 3 - Start polling loop
    # ES: Paso 3 - Iniciar loop de polling
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Bot is running! Waiting for messages...")
    print("  Press Ctrl+C to stop.")
    print("=" * 60 + "\n")

    # PT: Conjunto para armazenar IDs de mensagens ja processadas.
    #     Evita que o bot responda a mesma mensagem mais de uma vez.
    # EN: Set to store IDs of already processed messages.
    #     Prevents the bot from responding to the same message more than once.
    # ES: Conjunto para almacenar IDs de mensajes ya procesados.
    #     Evita que el bot responda al mismo mensaje mas de una vez.
    seen_ids = set()

    try:
        while True:
            try:
                # PT: Buscar todos os chats com mensagens nao lidas
                # EN: Fetch all chats with unread messages
                # ES: Buscar todos los chats con mensajes no leidos
                chats = get_all_chats()

                for chat in chats:
                    unread = chat.get("unreadCount", 0)
                    if unread <= 0:
                        continue

                    # PT: Extrair o ID do chat (pode ser dict ou string)
                    # EN: Extract the chat ID (can be dict or string)
                    # ES: Extraer el ID del chat (puede ser dict o string)
                    chat_id = chat.get("id", {})
                    if isinstance(chat_id, dict):
                        phone = chat_id.get("_serialized", "")
                    else:
                        phone = str(chat_id)

                    # PT: Ignorar chats invalidos e status broadcasts
                    # EN: Skip invalid chats and status broadcasts
                    # ES: Ignorar chats invalidos y status broadcasts
                    if not phone or "status@broadcast" in phone:
                        continue

                    # PT: Detectar se e um grupo pelo sufixo @g.us
                    # EN: Detect if it's a group by the @g.us suffix
                    # ES: Detectar si es un grupo por el sufijo @g.us
                    is_group = "@g.us" in phone

                    # PT: Obter o nome do chat para exibicao no console
                    # EN: Get the chat name for console display
                    # ES: Obtener el nombre del chat para visualizacion en consola
                    contact = chat.get("contact") or {}
                    chat_name = (
                        chat.get("name")
                        or contact.get("pushname")
                        or contact.get("name")
                        or phone
                    )

                    # PT: Buscar mensagens recentes do chat
                    # EN: Fetch recent messages from the chat
                    # ES: Buscar mensajes recientes del chat
                    messages = get_messages(phone, count=min(unread + 5, 50))

                    for msg in messages:
                        # PT: Extrair o ID unico da mensagem
                        # EN: Extract the unique message ID
                        # ES: Extraer el ID unico del mensaje
                        mid = msg.get("id", "")
                        if isinstance(mid, dict):
                            mid = mid.get("_serialized", mid.get("id", ""))

                        # PT: Pular se ja foi processada
                        # EN: Skip if already processed
                        # ES: Saltar si ya fue procesado
                        if mid in seen_ids:
                            continue

                        # PT: Pular mensagens enviadas por mim (pelo bot/sessao)
                        # EN: Skip messages sent by me (by the bot/session)
                        # ES: Saltar mensajes enviados por mi (por el bot/sesion)
                        if msg.get("fromMe", False):
                            seen_ids.add(mid)
                            continue

                        # PT: Processar apenas mensagens de texto (type = "chat")
                        # EN: Process only text messages (type = "chat")
                        # ES: Procesar solo mensajes de texto (type = "chat")
                        if msg.get("type") != "chat":
                            seen_ids.add(mid)
                            continue

                        # PT: Ignorar mensagens vazias
                        # EN: Skip empty messages
                        # ES: Ignorar mensajes vacios
                        body = (msg.get("body") or "").strip()
                        if not body:
                            seen_ids.add(mid)
                            continue

                        # PT: Obter o nome do remetente
                        # EN: Get the sender's name
                        # ES: Obtener el nombre del remitente
                        sender_info = msg.get("sender") or {}
                        sender = sender_info.get("pushname") or sender_info.get("name") or "?"

                        print(f"  IN  [{chat_name}] {sender}: {body}")

                        # PT: Enviar eco se tiver permissao de envio
                        # EN: Send echo if has send permission
                        # ES: Enviar eco si tiene permiso de envio
                        if can_send:
                            echo_text = f"{ECHO_PREFIX}{body}"
                            try:
                                send_text(phone, echo_text, is_group=is_group)
                                print(f"  OUT [{chat_name}] Bot: {echo_text}")
                            except Exception as send_err:
                                print(f"  ERR [{chat_name}] Send failed: {send_err}")
                        else:
                            print(f"  --- [{chat_name}] (no send permission, echo skipped)")

                        seen_ids.add(mid)

                # PT: Limpar IDs antigos para evitar consumo excessivo de memoria
                # EN: Clean old IDs to avoid excessive memory consumption
                # ES: Limpiar IDs antiguos para evitar consumo excesivo de memoria
                if len(seen_ids) > 10000:
                    seen_ids = set(list(seen_ids)[-5000:])

            except KeyboardInterrupt:
                raise
            except Exception as loop_err:
                print(f"  WARN: {loop_err}")

            # PT: Aguardar antes da proxima verificacao
            # EN: Wait before the next check
            # ES: Esperar antes de la proxima verificacion
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n  Bot stopped by user (Ctrl+C).")
        print("  Goodbye!\n")


# =============================================================================
# PT: Ponto de entrada do script
# EN: Script entry point
# ES: Punto de entrada del script
# =============================================================================
if __name__ == "__main__":
    main()
