# WPPConnect Admin - Echo Bot

---

**Idiomas / Languages / Idiomas:**
[Portugues](#portugues) | [English](#english) | [Espanol](#espanol)

---

`<a name="portugues"></a>`

# Portugues

## O que e este bot?

O **Echo Bot** e um exemplo simples de integracao com a plataforma **WPPConnect Admin** [(clique aqui)](https://zapadmin.vilios.com.br "Zapadmin"). Ele repete (ecoa) automaticamente todas as mensagens de texto recebidas em uma sessao WhatsApp conectada.

Este exemplo demonstra como:

- Autenticar via **API Key** no backend SaaS
- Listar e verificar sessoes WhatsApp
- Receber mensagens via **polling** (consulta periodica)
- Enviar mensagens de volta usando a API

## Arquitetura

```
Celular WhatsApp  <-->  WPPConnect Server  <-->  Backend SaaS  <-->  Echo Bot
(seu dispositivo)       (motor WhatsApp)         (autenticacao)      (este script)
                        zapi.monitor.eco.br      zapi.vilios.com.br
```

O **Backend SaaS** (`zapi.vilios.com.br`) atua como proxy inteligente:

1. Recebe sua requisicao autenticada com **API Key** (`X-API-Key`)
2. Verifica permissoes do usuario e limites de uso
3. Encaminha a requisicao para o **WPPConnect Server** (`zapi.monitor.eco.br`)
4. O WPPConnect Server se comunica diretamente com o WhatsApp

Voce **nunca precisa** se comunicar diretamente com o WPPConnect Server. O backend SaaS cuida de toda a autenticacao e autorizacao.

## Pre-requisitos

- **Python 3.8+** instalado no seu computador
- **Conexao com internet**
- Uma **conta na plataforma WPPConnect Admin**
- Uma **sessao WhatsApp conectada** na plataforma
- Uma **API Key** gerada na plataforma

## Guia Passo a Passo

### Passo 1: Criar uma Conta na Plataforma

1. Abra o navegador e acesse a plataforma WPPConnect Admin
   - URL de exemplo: `https://zapadmin.vilios.com.br` (ou a URL fornecida pelo seu administrador)
2. Na tela de login, clique em **"Criar conta"** (ou peca ao administrador para criar sua conta)
3. Preencha os campos:
   - **Usuario**: escolha um nome de usuario unico (ex: `meubot`)
   - **E-mail**: seu endereco de e-mail valido
   - **Senha**: crie uma senha segura
   - **Nome Completo**: seu nome
4. Clique em **"Registrar"**
5. Faca login com as credenciais criadas

### Passo 2: Criar e Conectar uma Sessao WhatsApp

Uma **sessao** e a conexao do seu dispositivo WhatsApp com a plataforma. Sem uma sessao ativa, o bot nao funciona.

1. No menu lateral esquerdo, clique em **"Sessoes"**
2. Clique no botao **"+ Nova Sessao"** (canto superior direito)
3. Preencha o **Nome da Sessao** (ex: `MeuBot`, `Suporte`, `Vendas`)
   - Este nome sera usado na configuracao do bot (`SESSION_NAME`)
4. Clique em **"Criar"**
5. Um **codigo QR** sera exibido na tela
6. No seu celular:
   - Abra o **WhatsApp**
   - Va em **Configuracoes > Dispositivos Vinculados > Vincular um Dispositivo**
   - Aponte a camera para o QR Code na tela
7. Aguarde ate o status da sessao mudar para **"CONECTADO"** (icone verde)

> **Importante**: O celular precisa estar com internet ativa para manter a sessao conectada.

### Passo 3: Gerar uma API Key

A **API Key** e sua credencial de acesso programatico a plataforma.

1. No menu lateral, clique em **"API Keys"** (icone de escudo)
2. Clique em **"+ Gerar Nova Chave"**
3. Preencha:
   - **Nome**: identifique a chave (ex: `Echo Bot`, `Bot Producao`)
   - **Descricao** (opcional): para que sera usada
   - **Permissoes**: marque pelo menos:
     - Ler Sessoes
     - Enviar Mensagens
4. Clique em **"Criar Chave"**
5. **COPIE A CHAVE IMEDIATAMENTE** - ela so sera exibida uma vez!

- A chave deve ser usada apenas em variável de ambiente (exemplo: WPP_API_KEY)

6. Guarde em local seguro

> **Seguranca**: Nunca compartilhe sua API Key. Se suspeitar que foi comprometida, delete-a e crie uma nova.

### Passo 4: Baixar e Configurar o Bot

1. Baixe o arquivo `echobot.py` (o link de download sera fornecido)
2. Salve em uma pasta no seu computador (ex: `C:\MeuBot\` ou `~/meubot/`)
3. Abra o arquivo `echobot.py` em um editor de texto
4. Altere as configuracoes no inicio do arquivo:

```python
import os
# URL do backend SaaS (normalmente nao precisa alterar)
SAAS_API_URL = "https://zapi.vilios.com.br"

# Sua API Key (use variável de ambiente WPP_API_KEY)
API_KEY = os.getenv("WPP_API_KEY", "")

# Nome da sessao (exatamente como criou no Passo 2)
SESSION_NAME = "Nome da Sua Sessao"

# Intervalo de verificacao em segundos (3-10 recomendado)
POLL_INTERVAL = 5
```

5. Salve o arquivo

### Passo 5: Instalar Dependencias

Abra o terminal (Prompt de Comando, PowerShell ou Terminal) e execute:

```bash
pip install requests
```

Ou, se tiver o arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Passo 6: Executar o Bot

No terminal, navegue ate a pasta onde salvou o arquivo e execute:

```bash
python echobot.py
```

Saida esperada:

```
============================================================
  WPPConnect Admin - Echo Bot
============================================================
  API:      https://zapi.vilios.com.br
  Session:  Minha Sessao
  Interval: 5s
  Prefix:   Echo:
============================================================

[1/2] Checking connection and permissions...
  OK: Session 'Minha Sessao' - read and send permissions confirmed.

[2/2] Checking WhatsApp connection status...
  OK: WhatsApp session is CONNECTED.

============================================================
  Bot is running! Waiting for messages...
  Press Ctrl+C to stop.
============================================================

  IN  [Joao] Joao Silva: Ola, tudo bem?
  OUT [Joao] Bot: Echo: Ola, tudo bem?
  IN  [Maria] Maria: Quanto custa?
  OUT [Maria] Bot: Echo: Quanto custa?
```

### Passo 7: Parar o Bot

Pressione **Ctrl+C** no terminal para encerrar o bot.

## Como o Bot Funciona

```
                    Loop de Polling (a cada 5 segundos)
                    +---------------------------------+
                    |                                 |
                    v                                 |
          +------------------+                        |
          | Buscar todos os  |                        |
          | chats (all-chats)|                        |
          +--------+---------+                        |
                   |                                  |
                   v                                  |
          +------------------+                        |
          | Tem mensagens    |  Nao                   |
          | nao lidas?       +------> Aguardar -------+
          +--------+---------+        (sleep)
                   | Sim
                   v
          +------------------+
          | Buscar mensagens |
          | do chat          |
          +--------+---------+
                   |
                   v
          +------------------+
          | Para cada msg:   |
          | - E nova?        |
          | - Nao e minha?   |
          | - E texto?       |
          +--------+---------+
                   | Sim
                   v
          +------------------+
          | Enviar eco:      |
          | "Echo: <msg>"    |
          +------------------+
```

1. O bot consulta a API a cada N segundos (definido em `POLL_INTERVAL`)
2. Busca todos os chats e filtra os que tem `unreadCount > 0`
3. Para cada chat com mensagens nao lidas, busca as mensagens recentes
4. Filtra apenas mensagens de texto (`type = "chat"`) que nao foram enviadas pelo bot
5. Envia a mesma mensagem de volta com o prefixo `Echo: `
6. Armazena o ID da mensagem processada para nao responder duas vezes

## Solucao de Problemas

| Erro                              | Causa                            | Solucao                                                              |
| --------------------------------- | -------------------------------- | -------------------------------------------------------------------- |
| `Could not connect to...`       | Servidor offline ou URL errada   | Verifique se `SAAS_API_URL` esta correto                           |
| `Invalid API Key (401)`         | Chave invalida ou expirada       | Gere uma nova API Key na plataforma                                  |
| `Session not found`             | Nome da sessao incorreto         | Verifique o `SESSION_NAME` (letras maiusculas/minusculas importam) |
| `No read permission`            | API Key sem permissao de leitura | Edite a API Key e marque "Ler Sessoes"                               |
| `No send permission`            | API Key sem permissao de envio   | Edite a API Key e marque "Enviar Mensagens"                          |
| `Session not connected`         | WhatsApp desconectado            | Reconecte a sessao escaneando o QR Code novamente                    |
| `ModuleNotFoundError: requests` | Biblioteca nao instalada         | Execute `pip install requests`                                     |

## Dicas de Seguranca

- **Nunca compartilhe sua API Key** em repositorios publicos, chats ou e-mails
- **Em producao**, use variaveis de ambiente em vez de hardcode:
  ```python
  import os
  API_KEY = os.getenv("WPPCONNECT_API_KEY")
  ```
- **Gere chaves especificas** para cada bot/integracao
- **Rotacione suas chaves** regularmente (a cada 3-6 meses)
- **Revogue chaves nao utilizadas** na pagina de API Keys

---

`<a name="english"></a>`

# English

## What is this bot?

The **Echo Bot** is a simple integration example with the **WPPConnect Admin** platform. It automatically repeats (echoes) all text messages received on a connected WhatsApp session.

This example demonstrates how to:

- Authenticate via **API Key** on the SaaS backend
- List and verify WhatsApp sessions
- Receive messages via **polling** (periodic queries)
- Send messages back using the API

## Architecture

```
WhatsApp Phone  <-->  WPPConnect Server  <-->  SaaS Backend  <-->  Echo Bot
(your device)         (WhatsApp engine)        (authentication)    (this script)
                      zapi.monitor.eco.br      zapi.vilios.com.br
```

The **SaaS Backend** (`zapi.vilios.com.br`) acts as a smart proxy:

1. Receives your request authenticated with an **API Key** (`X-API-Key`)
2. Checks user permissions and usage limits
3. Forwards the request to the **WPPConnect Server** (`zapi.monitor.eco.br`)
4. The WPPConnect Server communicates directly with WhatsApp

You **never need** to communicate directly with the WPPConnect Server. The SaaS backend handles all authentication and authorization.

## Prerequisites

- **Python 3.8+** installed on your computer
- **Internet connection**
- An **account on the WPPConnect Admin platform**
- An **active WhatsApp session** on the platform
- An **API Key** generated on the platform

## Step-by-Step Guide

### Step 1: Create an Account on the Platform

1. Open your browser and go to the WPPConnect Admin platform
   - Example URL: `https://zapi-admin.vilios.com.br` (or the URL provided by your administrator)
2. On the login screen, click **"Create account"** (or ask the administrator to create your account)
3. Fill in the fields:
   - **Username**: choose a unique username (e.g., `mybot`)
   - **Email**: your valid email address
   - **Password**: create a secure password
   - **Full Name**: your name
4. Click **"Register"**
5. Log in with the created credentials

### Step 2: Create and Connect a WhatsApp Session

A **session** is the connection between your WhatsApp device and the platform. Without an active session, the bot won't work.

1. On the left sidebar, click **"Sessions"**
2. Click the **"+ New Session"** button (upper right corner)
3. Enter the **Session Name** (e.g., `MyBot`, `Support`, `Sales`)
   - This name will be used in the bot configuration (`SESSION_NAME`)
4. Click **"Create"**
5. A **QR code** will be displayed on the screen
6. On your phone:
   - Open **WhatsApp**
   - Go to **Settings > Linked Devices > Link a Device**
   - Point the camera at the QR Code on screen
7. Wait until the session status changes to **"CONNECTED"** (green icon)

> **Important**: Your phone must have an active internet connection to keep the session connected.

### Step 3: Generate an API Key

The **API Key** is your programmatic access credential to the platform.

1. On the sidebar, click **"API Keys"** (shield icon)
2. Click **"+ Generate New Key"**
3. Fill in:
   - **Name**: identify the key (e.g., `Echo Bot`, `Production Bot`)
   - **Description** (optional): what it will be used for
   - **Permissions**: check at least:
     - Read Sessions
     - Send Messages
4. Click **"Create Key"**
5. **COPY THE KEY IMMEDIATELY** - it will only be shown once!

- The key must be used only in an environment variable (example: WPP_API_KEY)

6. Store it in a safe place

> **Security**: Never share your API Key. If you suspect it has been compromised, delete it and create a new one.

### Step 4: Download and Configure the Bot

1. Download the `echobot.py` file (download link will be provided)
2. Save it in a folder on your computer (e.g., `C:\MyBot\` or `~/mybot/`)
3. Open the `echobot.py` file in a text editor
4. Change the settings at the beginning of the file:

```python
import os
# SaaS backend URL (usually no need to change)
SAAS_API_URL = "https://zapi.vilios.com.br"

# Your API Key (use environment variable WPP_API_KEY)
API_KEY = os.getenv("WPP_API_KEY", "")

# Session name (exactly as created in Step 2)
SESSION_NAME = "Your Session Name"

# Check interval in seconds (3-10 recommended)
POLL_INTERVAL = 5
```

5. Save the file

### Step 5: Install Dependencies

Open the terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
pip install requests
```

Or, if you have the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Step 6: Run the Bot

In the terminal, navigate to the folder where you saved the file and run:

```bash
python echobot.py
```

Expected output:

```
============================================================
  WPPConnect Admin - Echo Bot
============================================================
  API:      https://zapi.vilios.com.br
  Session:  My Session
  Interval: 5s
  Prefix:   Echo:
============================================================

[1/2] Checking connection and permissions...
  OK: Session 'My Session' - read and send permissions confirmed.

[2/2] Checking WhatsApp connection status...
  OK: WhatsApp session is CONNECTED.

============================================================
  Bot is running! Waiting for messages...
  Press Ctrl+C to stop.
============================================================

  IN  [John] John Smith: Hello, how are you?
  OUT [John] Bot: Echo: Hello, how are you?
  IN  [Mary] Mary: How much does it cost?
  OUT [Mary] Bot: Echo: How much does it cost?
```

### Step 7: Stop the Bot

Press **Ctrl+C** in the terminal to stop the bot.

## How the Bot Works

```
                    Polling Loop (every 5 seconds)
                    +---------------------------------+
                    |                                 |
                    v                                 |
          +------------------+                        |
          | Fetch all chats  |                        |
          | (all-chats)      |                        |
          +--------+---------+                        |
                   |                                  |
                   v                                  |
          +------------------+                        |
          | Has unread       |  No                    |
          | messages?        +------> Wait -----------+
          +--------+---------+        (sleep)
                   | Yes
                   v
          +------------------+
          | Fetch messages   |
          | from the chat    |
          +--------+---------+
                   |
                   v
          +------------------+
          | For each msg:    |
          | - Is it new?     |
          | - Not from me?   |
          | - Is it text?    |
          +--------+---------+
                   | Yes
                   v
          +------------------+
          | Send echo:       |
          | "Echo: <msg>"    |
          +------------------+
```

1. The bot queries the API every N seconds (defined in `POLL_INTERVAL`)
2. Fetches all chats and filters those with `unreadCount > 0`
3. For each chat with unread messages, fetches recent messages
4. Filters only text messages (`type = "chat"`) not sent by the bot
5. Sends the same message back with the `Echo: ` prefix
6. Stores the processed message ID to avoid responding twice

## Troubleshooting

| Error                             | Cause                           | Solution                                            |
| --------------------------------- | ------------------------------- | --------------------------------------------------- |
| `Could not connect to...`       | Server offline or wrong URL     | Check if `SAAS_API_URL` is correct                |
| `Invalid API Key (401)`         | Key invalid or expired          | Generate a new API Key on the platform              |
| `Session not found`             | Incorrect session name          | Check `SESSION_NAME` (case-sensitive)             |
| `No read permission`            | API Key without read permission | Edit the API Key and check "Read Sessions"          |
| `No send permission`            | API Key without send permission | Edit the API Key and check "Send Messages"          |
| `Session not connected`         | WhatsApp disconnected           | Reconnect the session by scanning the QR Code again |
| `ModuleNotFoundError: requests` | Library not installed           | Run `pip install requests`                        |

## Security Tips

- **Never share your API Key** in public repositories, chats, or emails
- **In production**, use environment variables instead of hardcoding:
  ```python
  import os
  API_KEY = os.getenv("WPPCONNECT_API_KEY")
  ```
- **Generate specific keys** for each bot/integration
- **Rotate your keys** regularly (every 3-6 months)
- **Revoke unused keys** on the API Keys page

---

`<a name="espanol"></a>`

# Espanol

## Que es este bot?

El **Echo Bot** es un ejemplo simple de integracion con la plataforma **WPPConnect Admin**. Repite (hace eco) automaticamente todos los mensajes de texto recibidos en una sesion de WhatsApp conectada.

Este ejemplo demuestra como:

- Autenticar via **API Key** en el backend SaaS
- Listar y verificar sesiones de WhatsApp
- Recibir mensajes via **polling** (consultas periodicas)
- Enviar mensajes de vuelta usando la API

## Arquitectura

```
Celular WhatsApp  <-->  WPPConnect Server  <-->  Backend SaaS  <-->  Echo Bot
(su dispositivo)        (motor WhatsApp)         (autenticacion)     (este script)
                        zapi.monitor.eco.br      zapi.vilios.com.br
```

El **Backend SaaS** (`zapi.vilios.com.br`) actua como proxy inteligente:

1. Recibe su solicitud autenticada con **API Key** (`X-API-Key`)
2. Verifica permisos del usuario y limites de uso
3. Redirige la solicitud al **WPPConnect Server** (`zapi.monitor.eco.br`)
4. El WPPConnect Server se comunica directamente con WhatsApp

Usted **nunca necesita** comunicarse directamente con el WPPConnect Server. El backend SaaS se encarga de toda la autenticacion y autorizacion.

## Requisitos Previos

- **Python 3.8+** instalado en su computadora
- **Conexion a internet**
- Una **cuenta en la plataforma WPPConnect Admin**
- Una **sesion de WhatsApp conectada** en la plataforma
- Una **API Key** generada en la plataforma

## Guia Paso a Paso

### Paso 1: Crear una Cuenta en la Plataforma

1. Abra el navegador y acceda a la plataforma WPPConnect Admin
   - URL de ejemplo: `https://zapi-admin.vilios.com.br` (o la URL proporcionada por su administrador)
2. En la pantalla de login, haga clic en **"Crear cuenta"** (o pida al administrador que cree su cuenta)
3. Complete los campos:
   - **Usuario**: elija un nombre de usuario unico (ej: `mibot`)
   - **E-mail**: su direccion de correo electronico valida
   - **Contrasena**: cree una contrasena segura
   - **Nombre Completo**: su nombre
4. Haga clic en **"Registrar"**
5. Inicie sesion con las credenciales creadas

### Paso 2: Crear y Conectar una Sesion de WhatsApp

Una **sesion** es la conexion de su dispositivo WhatsApp con la plataforma. Sin una sesion activa, el bot no funciona.

1. En el menu lateral izquierdo, haga clic en **"Sesiones"**
2. Haga clic en el boton **"+ Nueva Sesion"** (esquina superior derecha)
3. Ingrese el **Nombre de la Sesion** (ej: `MiBot`, `Soporte`, `Ventas`)
   - Este nombre se usara en la configuracion del bot (`SESSION_NAME`)
4. Haga clic en **"Crear"**
5. Se mostrara un **codigo QR** en la pantalla
6. En su celular:
   - Abra **WhatsApp**
   - Vaya a **Configuracion > Dispositivos Vinculados > Vincular un Dispositivo**
   - Apunte la camara al codigo QR en la pantalla
7. Espere hasta que el estado de la sesion cambie a **"CONECTADO"** (icono verde)

> **Importante**: El celular debe tener conexion a internet activa para mantener la sesion conectada.

### Paso 3: Generar una API Key

La **API Key** es su credencial de acceso programatico a la plataforma.

1. En el menu lateral, haga clic en **"API Keys"** (icono de escudo)
2. Haga clic en **"+ Generar Nueva Clave"**
3. Complete:
   - **Nombre**: identifique la clave (ej: `Echo Bot`, `Bot Produccion`)
   - **Descripcion** (opcional): para que se usara
   - **Permisos**: marque al menos:
     - Leer Sesiones
     - Enviar Mensajes
4. Haga clic en **"Crear Clave"**
5. **COPIE LA CLAVE INMEDIATAMENTE** - solo se mostrara una vez!

- La clave debe usarse solo en variable de entorno (ejemplo: WPP_API_KEY)

6. Guardela en un lugar seguro

> **Seguridad**: Nunca comparta su API Key. Si sospecha que fue comprometida, eliminela y cree una nueva.

### Paso 4: Descargar y Configurar el Bot

1. Descargue el archivo `echobot.py` (el enlace de descarga sera proporcionado)
2. Guardelo en una carpeta en su computadora (ej: `C:\MiBot\` o `~/mibot/`)
3. Abra el archivo `echobot.py` en un editor de texto
4. Cambie las configuraciones al inicio del archivo:

```python
# URL del backend SaaS (normalmente no necesita cambiar)
SAAS_API_URL = "https://zapi.vilios.com.br"

# Su API Key (pegue la clave generada en el Paso 3)
API_KEY = os.getenv("WPP_API_KEY", "")  # Nunca deixe segredo no código, use variável de entorno

# Nombre de la sesion (exactamente como la creo en el Paso 2)
SESSION_NAME = "Nombre de Su Sesion"

# Intervalo de verificacion en segundos (3-10 recomendado)
POLL_INTERVAL = 5
```

5. Guarde el archivo

### Paso 5: Instalar Dependencias

Abra la terminal (Simbolo del Sistema, PowerShell o Terminal) y ejecute:

```bash
pip install requests
```

O, si tiene el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Paso 6: Ejecutar el Bot

En la terminal, navegue hasta la carpeta donde guardo el archivo y ejecute:

```bash
python echobot.py
```

Salida esperada:

```
============================================================
  WPPConnect Admin - Echo Bot
============================================================
  API:      https://zapi.vilios.com.br
  Session:  Mi Sesion
  Interval: 5s
  Prefix:   Echo:
============================================================

[1/2] Checking connection and permissions...
  OK: Session 'Mi Sesion' - read and send permissions confirmed.

[2/2] Checking WhatsApp connection status...
  OK: WhatsApp session is CONNECTED.

============================================================
  Bot is running! Waiting for messages...
  Press Ctrl+C to stop.
============================================================

  IN  [Juan] Juan Garcia: Hola, como estas?
  OUT [Juan] Bot: Echo: Hola, como estas?
  IN  [Ana] Ana: Cuanto cuesta?
  OUT [Ana] Bot: Echo: Cuanto cuesta?
```

### Paso 7: Detener el Bot

Presione **Ctrl+C** en la terminal para detener el bot.

## Como Funciona el Bot

```
                    Loop de Polling (cada 5 segundos)
                    +---------------------------------+
                    |                                 |
                    v                                 |
          +------------------+                        |
          | Buscar todos los |                        |
          | chats (all-chats)|                        |
          +--------+---------+                        |
                   |                                  |
                   v                                  |
          +------------------+                        |
          | Tiene mensajes   |  No                    |
          | no leidos?       +------> Esperar --------+
          +--------+---------+        (sleep)
                   | Si
                   v
          +------------------+
          | Buscar mensajes  |
          | del chat         |
          +--------+---------+
                   |
                   v
          +------------------+
          | Para cada msg:   |
          | - Es nueva?      |
          | - No es mia?     |
          | - Es texto?      |
          +--------+---------+
                   | Si
                   v
          +------------------+
          | Enviar eco:      |
          | "Echo: <msg>"    |
          +------------------+
```

1. El bot consulta la API cada N segundos (definido en `POLL_INTERVAL`)
2. Busca todos los chats y filtra los que tienen `unreadCount > 0`
3. Para cada chat con mensajes no leidos, busca los mensajes recientes
4. Filtra solo mensajes de texto (`type = "chat"`) no enviados por el bot
5. Envia el mismo mensaje de vuelta con el prefijo `Echo: `
6. Almacena el ID del mensaje procesado para no responder dos veces

## Solucion de Problemas

| Error                             | Causa                             | Solucion                                                       |
| --------------------------------- | --------------------------------- | -------------------------------------------------------------- |
| `Could not connect to...`       | Servidor offline o URL incorrecta | Verifique si `SAAS_API_URL` es correcto                      |
| `Invalid API Key (401)`         | Clave invalida o expirada         | Genere una nueva API Key en la plataforma                      |
| `Session not found`             | Nombre de sesion incorrecto       | Verifique el `SESSION_NAME` (mayusculas/minusculas importan) |
| `No read permission`            | API Key sin permiso de lectura    | Edite la API Key y marque "Leer Sesiones"                      |
| `No send permission`            | API Key sin permiso de envio      | Edite la API Key y marque "Enviar Mensajes"                    |
| `Session not connected`         | WhatsApp desconectado             | Reconecte la sesion escaneando el codigo QR nuevamente         |
| `ModuleNotFoundError: requests` | Biblioteca no instalada           | Ejecute `pip install requests`                               |

## Consejos de Seguridad

- **Nunca comparta su API Key** en repositorios publicos, chats o correos electronicos
- **En produccion**, use variables de entorno en vez de hardcode:
  ```python
  import os
  API_KEY = os.getenv("WPPCONNECT_API_KEY")
  ```
- **Genere claves especificas** para cada bot/integracion
- **Rote sus claves** regularmente (cada 3-6 meses)
- **Revoque claves no utilizadas** en la pagina de API Keys

---

## Licencia / License / Licencia

Este exemplo e parte do projeto **WPPConnect Admin** e esta disponivel como referencia para integracao.

This example is part of the **WPPConnect Admin** project and is available as an integration reference.

Este ejemplo es parte del proyecto **WPPConnect Admin** y esta disponible como referencia para integracion.
