# 🛰️ G.I.D.E.O.N. — Módulos de Automatización Web (RPA)
### Especificación Técnica para Ingesta de IA y Desarrollo de TI

Este paquete contiene **exclusivamente la lógica de automatización robótica de procesos (RPA), scraping, manipulación de DOM y gestión de datos** de G.I.D.E.O.N. Se han eliminado todas las capas visuales de usuario (GUI CustomTkinter), binarios compilados, registros de historial y artefactos temporales, dejando el núcleo funcional listo para ser analizado, reentrenado o migrado por un agente de Inteligencia Artificial o equipo de TI.

---

## 📂 1. Estructura del Paquete

```text
SCRIPTS_AUTOMATIZACION_TI/
├── automation/                         # Capa de interacción web (Playwright)
│   ├── __init__.py                     # Exportaciones públicas de funciones de scraping
│   ├── crm_helpers.py                  # Utilidades DOM: eventos de React, menús Material-UI (MUI), clics robustos
│   ├── worker.py                       # Orquestador del Flujo FTTH CRM Evergent (Multihilo)
│   ├── worker_ftth_ecommerce.py        # Flujo FTTH eCommerce Tienda Pública (Manejo de Cloudflare/Turnstile)
│   ├── worker_ott.py                   # Flujo OTT Streaming (Monohilo estricto y pausa de pago)
│   └── steps/                          # Pasos atómicos secuenciales del CRM Evergent
│       ├── __init__.py
│       ├── paso0_login.py              # Autenticación, control de sesiones y bypass de modal
│       ├── paso1_datos.py              # Inyección de identidad: Cédula, RIF, Nombre y Teléfono VE
│       ├── paso2_direccion.py          # Selección jerárquica de geolocalización (Estado, Municipio, Parroquia)
│       ├── paso3_adicional.py          # Contacto de referencia y campos opcionales
│       ├── paso4_paquetes.py           # Selección del plan base de fibra (MB) y promociones
│       ├── paso4_addons.py             # Inclusión de decodificadores o servicios de valor agregado
│       └── paso5_otp.py                # Polling asíncrono Maildrop, extracción regex y confirmación
├── core/                               # Capa de negocio, reglas de datos y sincronización
│   ├── __init__.py                     # Exportaciones del core
│   ├── config.py                       # Endpoints URL, credenciales base y mutexes de concurrencia
│   ├── catalogos.py                    # Parsers y normalizadores de catálogos CSV
│   ├── correlativos.py                 # Generadores incrementales thread-safe para correos y cuentas
│   └── generadores.py                  # Sintetizador de identidades humanas limpias y teléfonos VE válidos
├── catalogo_direcciones.csv            # Catálogo catastral de cobertura FTTH
├── catalogo_direcciones_ott.csv        # Catálogo de ubicaciones habilitadas para OTT
├── catalogo_planes.csv                 # Catálogo de planes comerciales FTTH (Mbps, bundles, tarifas)
├── catalogo_ott.csv                    # Catálogo de suscripciones OTT (Gold, Platino, Diamante)
├── config_gideon.json                  # Plantilla de configuración de variables y credenciales
├── requirements.txt                    # Dependencias mínimas requeridas (Playwright)
├── ejecutar_cli.py                     # Runner de consola (CLI) para ejecución autónoma sin GUI
└── README_TECNICO_AUTOMATIZACION.md    # Este documento
```

---

## ⚙️ 2. Dependencias y Entorno de Ejecución

Los scripts operan sobre **Python 3.10+** y utilizan **Playwright Synchronous API**.

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar los binarios de Chromium de Playwright
playwright install chromium
```

---

## 🔄 3. Detalle Arquitectónico de los 3 Procesos

### 🔹 Proceso 1: FTTH CRM Evergent (`automation/worker.py` + `automation/steps/*`)
* **Objetivo:** Creación masiva de contratos de fibra óptica directamente sobre el CRM Evergent / Salesforce.
* **Concurrencia:** Permite ejecución **multihilo masiva** (ej. 2 a 8 hilos simultáneos).
* **Mecanismos de Sincronización:**
  * `lock_correlativo`: Protege el contador incremental del correo temporal para evitar colisiones entre workers.
  * `lock_login`: Evita que múltiples instancias colisionen durante la fase crítica de sesión inicial.
* **Secuencia de Pasos:**
  1. `paso0_login.py`: Navega a `URL_LOGIN`, inyecta credenciales del operador, maneja alertas y accede al formulario `createAccount`.
  2. `paso1_datos.py`: Genera cédula (V/E/J aleatoria no colisionante), nombre humano coherente y teléfono con código de área venezolano (`0414`, `0424`, `0412`, `0416`).
  3. `paso2_direccion.py`: Inyecta dirección del catálogo catastral resolviendo selects anidados y componentes dinámicos de Material-UI.
  4. `paso3_adicional.py`: Completa campos de contacto secundario requeridos por el backend de facturación.
  5. `paso4_paquetes.py`: Busca en el árbol de productos el plan seleccionado (ej. 400 Mbps), asocia router y promociones aplicables.
  6. `paso4_addons.py`: Procesa decodificadores o servicios adicionales si el plan lo requiere.
  7. `paso5_otp.py`: Detalla el flujo de verificación por código de un solo uso.

---

### 🔹 Proceso 2: FTTH eCommerce (`automation/worker_ftth_ecommerce.py`)
* **Objetivo:** Registro y compra de servicios de fibra a través de la tienda web pública (`https://tiendatesting.simple.com.ve/tienda`).
* **Retos Técnicos Resueltos:**
  * **Detección de Cloudflare Challenge / Turnstile:** Implementa `_detectar_captcha()` que evalúa iframes de Turnstile, tokens vacíos en `input[name='cf-turnstile-response']` y desafíos de pantalla completa `#challenge-stage`. Si se activa, pausa la ejecución y reanuda en cuanto el token es validado.
  * **React Synthetic Events:** Los inputs de React no detectan la asignación directa de valor; el script utiliza `_react_select()` y dispatchers nativos de eventos `input` y `change` para forzar la actualización del estado interno de la aplicación web.
  * **Validación de Cobertura Geográfica:** Interactúa con mapas y selectores de cobertura de la tienda para confirmar factibilidad técnica antes de proceder al checkout.

---

### 🔹 Proceso 3: OTT Streaming (`automation/worker_ott.py`)
* **Objetivo:** Suscripción de cuentas de streaming (Simpleplus OTT).
* **Concurrencia:** **Estrictamente 1 solo hilo a la vez** (`hilos_simultaneos_ott: 1`). Los servidores de streaming cuentan con filtros anti-spam más agresivos; el procesamiento en ráfaga genera bloqueos de IP o rate-limit.
* **Manejo de Pasarela de Pago:** El script navega el carrusel de planes OTT, completa la suscripción, valida el OTP y se detiene tácticamente al llegar a la pasarela bancaria/tarjeta, retornando el estado para procesamiento manual o automatización de token de pago.

---

## 🔐 4. Protocolo de Verificación OTP (Maildrop.cc)

Ambos flujos utilizan bandejas de correo desechables de Maildrop para recepción de contraseñas de un solo uso (OTP):

1. **Construcción del Buzón:** `f"{prefijo}{correlativo}"` (sin `@maildrop.cc` en la URL de consulta: `https://maildrop.cc/inbox/?mailbox={mailbox_name}`).
2. **Polling Asíncrono Resiliente:**
   * La entrega de correo no es instantánea (latencia promedio de 5 a 20 segundos).
   * Se ejecuta un ciclo de hasta 15 intentos con pausas de 3.5 a 5 segundos.
   * En cada ciclo se verifica si el usuario solicitó cancelación (`cancel_event.is_set()`).
3. **Extracción del Código:**
   * Se evalúa el primer elemento de la lista y se despliega su contenido.
   * Se aplica extracción mediante expresiones regulares con aislamiento de bordes:
     ```python
     re.search(r'(?<!\d)(\d{6})(?!\d)', texto_visible)
     ```
4. **Llenado en Formulario:**
   * Para interfaces de casilla única: escritura directa con evento `change`.
   * Para interfaces multicasilla (`otp.0` a `otp.5`): inyección dígito por dígito con ligera latencia y evento `blur()` en la última celda para activar el listener de validación de React.
   * Clic forzado (`force=True`) en el botón de confirmación para sobrepasar overlays o animaciones CSS.

---

## 📊 5. Contratos de Datos y Catálogos CSV

| Archivo | Propósito | Campos Clave |
| :--- | :--- | :--- |
| `catalogo_planes.csv` | Mapeo de planes FTTH comerciales | `Nombre_Plan`, `Paquete`, `Promocion`, `Tarifa`, `Router` |
| `catalogo_direcciones.csv` | Coordenadas y datos catastrales | `Ubicacion`, `Estado`, `Municipio`, `Parroquia`, `Sector`, `Direccion_Corta` |
| `catalogo_ott.csv` | Paquetes de streaming OTT | `Plan`, `Precio`, `Canales_Destacados` |
| `catalogo_direcciones_ott.csv` | Direcciones homologadas OTT | `Ubicacion`, `Ciudad`, `Codigo_Postal` |
| `config_gideon.json` | Parámetros operacionales | `prefijo_email`, `usuario_login`, `password_login`, `modo_headless` |

---

## 🚀 6. Ejecución Autónoma vía CLI (Sin Interfaz Gráfica)

Para probar, auditar o invocar los procesos directamente desde scripts externos, pipelines o agentes de IA:

```bash
# Ejecutar flujo FTTH CRM en modo visible (para depuración)
python ejecutar_cli.py --flujo ftth_crm

# Ejecutar flujo eCommerce en modo Headless (ideal para servidores/contenedores)
python ejecutar_cli.py --flujo ecommerce --headless

# Ejecutar flujo OTT Streaming
python ejecutar_cli.py --flujo ott
```
