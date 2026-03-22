# WPPConnect Admin - Echo Bot (Webhook)

---

**Idiomas / Languages / Idiomas:**
[Português](#portugues) | [English](#english) | [Español](#espanol)

---

<a name="portugues"></a>

# Português

## O que é este bot?

O **Echo Bot** é um exemplo de integração via **Webhooks** com a plataforma **WPPConnect Admin**. Em vez de consultar a API continuamente (polling), este bot abre um servidor local (`Flask`) e "escuta" ativamente por novas mensagens vindas do WhatsApp. Ao receber uma mensagem de texto, ele a repete (ecoa) de volta ao rementente.

Este exemplo demonstra como:
- Criar um servidor **Flask** para receber Webhooks do WPPConnect.
- Identificar e ler eventos no formato JSON recebidos via requisições POST.
- Tratar o formato de identificadores de múltiplos dispositivos (`@lid`).
- Autenticar requisições de resposta usando a **API Key** (`X-API-Key`) através do proxy seguro da plataforma SaaS.

## Arquitetura

```
Celular WhatsApp  --(Webhook)-->  WPPConnect Server  --(Ngrok)-->  Echo Bot (Flask local)
(seu dispositivo)                 (motor WhatsApp)                 (escutando na 5001)
                                                                            |
                                Backend SaaS  <--(send-message)-------------+
                                (zapi.vilios.com.br)
```

## Pré-requisitos

- **Python 3.8+**
- Ferramenta **ngrok** instalada (para testes locais expostos à internet)
- Uma **API Key** e uma **Sessão ativa** no WPPConnect Admin

## Guia Passo a Passo

### Passo 1: Configurar a API Key e Sessão
No painel do WPPConnect Admin, crie uma Sessão WhatsApp (ex: `echobot`) e conecte o QR Code com seu smartphone. Em seguida, crie uma **API Key** com permissões para "Enviar Mensagens" e "Ler Sessões". Não se esqueça de guardá-la em segurança.

### Passo 2: Instalar Dependências
Abra o seu terminal (Prompt de Comando, PowerShell ou Linux) e execute:
```bash
pip install flask requests
```

### Passo 3: Configurar o Bot
Edite o arquivo `echobot.py` alterando as seguintes variáveis lá no topo:
- `SAAS_API_URL`: A URL do backend SaaS (geralmente não precisa alterar).
- `API_KEY`: A sua chave criada no Passo 1 (formato `sk_live_...`).
- `SESSION_NAME`: O nome da sessão exata que você usou no painel admin (ex: `echobot`).

### Passo 4: Executar o Bot e o Ngrok
Abra um terminal na pasta do arquivo e inicie o bot:
```bash
python echobot.py
```
*(O script começará a escutar na porta 5001 do seu computador)*

Deixe este terminal aberto. Abra um **segundo terminal** e exponha a porta 5001 para a internet usando o ngrok:
```bash
ngrok http 5001
```
O ngrok vai fornecer um link público, algo como `https://1234abcd.ngrok-free.app`.
O link completo final para o servidor do bot será: `https://1234abcd.ngrok-free.app/webhook`

### Passo 5: Cadastrar o Webhook no Painel
Pegue a URL completa fornecida pelo ngrok e instale-a como configuração de Webhook nativo na sua sessão lá no WPPConnect Server. Toda mensagem recebida vai bater diretamente no bot agora!

> **Nota sobre o formato @lid**: Com a chegada da arquitetura Multi-Device no WhatsApp, algumas mensagens são trafegadas através dos webhooks identificando o painel emissor com um identificador finalhado em `@lid` (Linked Device ID) em vez do seu número de telefone natural (`@c.us`). O `echobot.py` é esperto: ele intercepta o `@lid` e consulta a rota nativa secreta `/contact/pn-lid/` para descobrir o telefone real que está por trás do dispositivo e direciona a resposta para o lugar certo sem gerar erros (como *404 Not Found*).

---

<a name="english"></a>

# English

## What is this bot?

The **Echo Bot** is a **Webhook-based** integration example for the **WPPConnect Admin** platform. Instead of continuously polling the API, it opens a local server and "listens" for new messages coming from WhatsApp in real time.

This example demonstrates how to:
- Create a **Flask** server to receive WPPConnect Webhooks.
- Handle multi-device identifiers (`@lid`).
- Authenticate response requests using the **API Key** (`X-API-Key`) via the SaaS proxy.

## Architecture

```
WhatsApp Phone   --(Webhook)-->  WPPConnect Server  --(Ngrok)-->  Echo Bot (Local Flask)
(your device)                    (WhatsApp engine)                (listening on 5001)
                                                                            |
                                 SaaS Backend  <--(send-message)------------+
                                 (zapi.vilios.com.br)
```

## Step-by-Step Guide

### Step 1: Install Dependencies
```bash
pip install flask requests
```

### Step 2: Configure the Bot
Edit the `echobot.py` file to include your `SAAS_API_URL`, `API_KEY`, and `SESSION_NAME`.

### Step 3: Run the Bot & Ngrok
Open a terminal and run the bot:
```bash
python echobot.py
```
Leave it running. Open a **second terminal** and expose the listening port temporarily using ngrok:
```bash
ngrok http 5001
```
Ngrok will generate a secure link like `https://1234abcd.ngrok-free.app`. Your final URL will be: `https://1234abcd.ngrok-free.app/webhook`. Register this webhook URL to your existing WhatsApp connection configured in the WPPConnect Server panel.

> **Note on @lid identifiers**: In WhatsApp's Multi-Device architecture, incoming Webhooks often use the `@lid` format for specifying the sender instead of the actual phone number. If we hit the API to reply directly to an `@lid`, the system will yield a 404 error. Standardly, `echobot.py` automatically detects and maps these `@lid` linked-device numbers into actual `@c.us` real phone numbers by querying `/contact/pn-lid/` before issuing the API post request.

---

<a name="espanol"></a>

# Español

## ¿Qué es este bot?

El **Echo Bot** es un ejemplo de integración basada en **Webhooks** para la plataforma **WPPConnect Admin**. En lugar de consultar continuamente la API como un *long-polling*, levanta un servidor local (`Flask`) que intercepta mensajes entrantes desde WhatsApp inmediatamente.

Este ejemplo demuestra cómo:
- Crear un servidor **Flask** para recibir webhooks nativos.
- Manejar los identificadores de dispositivos múltiples encubiertos (`@lid`).
- Autenticar solicitudes enviadas mediante tu **API Key** (`X-API-Key`) a través del proxy SaaS inteligente.

## Guía Paso a Paso

### Paso 1: Instalar Dependencias del Entorno
```bash
pip install flask requests
```

### Paso 2: Configurar el Bot
Abre el archivo de código, `echobot.py`, y en su encabezado cambia el correspondiente `SAAS_API_URL`, tu propio `API_KEY` (otorgado en el panel administrativo), y el `SESSION_NAME` de forma adecuada.

### Paso 3: Ejecutar el Script y Ngrok
Abre una ventana de terminal y posicionate en el directorio pertinente, finalmente lanza el bot:
```bash
python echobot.py
```
Abre otra **segunda terminal** en paralelo y expone el puerto 5001 externamente al internet usando *ngrok*:
```bash
ngrok http 5001
```
Ngrok generará un enlace aleatorio tal que así: `https://1234abcd.ngrok-free.app`. Entonces, su URL de Webhook terminada será: `https://1234abcd.ngrok-free.app/webhook`. Anexe esta URL en las configuraciones de Webhook del WPPConnect Server.

> **Consejo sobre la resolución de identificadores @lid**: En el ecosistema Multi-Dispositivo de WhatsApp de hoy día, los webhooks frecuentemente envían al emisor en este formato ofuscado (`@lid`) en lugar de mostrar los números de celular nativos. Este bot inteligente previene un fracaso de respuesta (clásico código HTTP 404) resolviendo automáticamente dicho parámetro a través de la ruta nativa oculta `/contact/pn-lid/` previamente a efectuar la contestación hacia allí.

---

## License / Licença / Licencia

This example is part of the **WPPConnect Admin** project and is available as an integration reference.
