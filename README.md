<!--
ANPR-v7
Proyecto ANPR (Automatic Number Plate Recognition)
-->

# ANPR-v7

**Reconocimiento Automático de Placas (ANPR)** — Sistema completo para detección, lectura y gestión de placas vehiculares con integración hardware (servo + LEDs) y backend web para control y facturación.

**Estado:** En desarrollo

## Descripción

`ANPR-v7` es una solución integral que detecta matrículas en tiempo real usando un modelo YOLO personalizado, extrae texto con OCR (PaddleOCR), gestiona el ciclo de vida del vehículo (entrada → slot → pago) y coordina hardware (barrera/servo y LEDs de slots) mediante comandos serial.

El sistema incluye:
- Detección y reconocimiento en video (`main.py`).
- Lógica de negocio y persistencia en `backend` (Flask + SQLAlchemy).
- Interfaz para búsquedas y facturación (`/buscar`, `/factura`).
- Integración con hardware vía puerto serial (COM).

## Características principales

- Detección de placas en zonas predefinidas (ROIs) por slot.
- Validación de placas (filtros de detección fallida).
- Registro de eventos: `entrada`, `slotX` (1..6), `pagado`.
- Interfaz web para buscar y facturar placas.
- Control de barrera (abrir/cerrar) y control de LEDs por slot.
- Fácilmente extensible: más slots, reglas tarifarias, autenticación.

## Estructura del proyecto

Raíz del repo (resumen):

```
.
├── backend/
│   ├── server.py           # API server (Flask)
│   ├── models.py           # Modelos SQLAlchemy
│   └── routes/             # Rutas/handlers: buscar, factura, tabla, update_plate, etc.
├── models/                 # Pesos del modelo YOLO (e.g., best.pt)
├── utils/                  # Helpers: processor.py, client_update.py
├── main.py                 # Captura de video, detección y envío al backend
├── requirements.txt
└── README.md
```

Rutas HTTP relevantes (resumen):
- `GET /buscar` — Interfaz de búsqueda.
- `GET /sugerencias?query=...` — Sugerencias de placas.
- `GET/POST /factura` — Genera factura y marca `pagado`.
- `POST /update_plate` — Endpoint que recibe lecturas desde el cliente (main) y actualiza DB + hardware.

## Instalación (rápida)

1. Crear/activar entorno virtual (recomendado):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Ajustar rutas y puertos si aplica (`backend/server.py`, `main.py`) y configurar el puerto serial (`update_plate.py`, p. ej. `COM8`).

## Uso (desarrollo)

- Iniciar backend (desde la raíz):

```powershell
python backend/server.py
```

- Iniciar el cliente de detección (webcam + YOLO):

```powershell
python main.py
```

El cliente detecta placas, las valida y envía `POST` a `/update_plate` con JSON: `{"plate": "ABC123", "slot": "entrada"}` o `{"plate":"ABC123","slot":"slot3"}`.

Para facturar una placa usar la interfaz: abrir `http://<host>:<port>/buscar`, buscar la placa y pagar (esto crea un registro `pagado`).

## Cómo funciona (internals)

- `main.py`: captura frames, aplica `process_frame()` (detección con YOLO) y OCR con PaddleOCR, determina `slot_detectado` según ROIs y envía lecturas al backend.
- `backend/routes/update_plate.py`: valida placa, registra `entrada`, asigna `slotX` o marca `pagado`. Controla el hardware enviando bytes específicos por serial para abrir/ cerrar barrera y encender/apagar LEDs.
- `backend/models.py`: modelo `PlateRecord` almacena `plate`, `slot`, `timestamp`.

## Hardware (integración)

- Puerto serial (ej. `COM8`) usado para enviar comandos simples:
	- `V` / `R` — abrir / cerrar barrera (ejemplo).
	- `A`..`F` — encender LEDs de `slot1`..`slot6`.
	- `G`..`L` — apagar LEDs de `slot1`..`slot6`.

Asegúrate de ajustar el puerto serial, nivel lógico y tiempos (`time.sleep`) según tu electrónica.

## Escalabilidad y posibilidades

- Mejoras de rendimiento:
	- Pasar detección a un hilo/proceso separado o a un servicio dedicado para no bloquear el IO.
	- Batch o cola (RabbitMQ / Redis) entre el detector y el backend para resiliencia.

- Modelo y OCR:
	- Reentrenar/afinar el modelo YOLO para más precisión o más formatos de placa.
	- Probar otros OCR o pipelines (Tesseract, modelos basados en Transformers) para mejorar lectura.

- Infraestructura:
	- Escalar el backend con contenedores (Docker) y desplegar en Kubernetes o en instancias separadas.
	- Usar base de datos central (Postgres) y almacenamiento de logs/telemetría.

- Funcionalidades adicionales:
	- Panel administrativo con autenticación y auditoría.
	- Facturación automática y integración con pasarelas de pago.
	- Integración con cámaras IP y múltiples entradas/slots dinámicos.

## Seguridad y privacidad

- Limita acceso al backend con autenticación (JWT, OAuth) antes de exponer APIs.
- Cifra el transporte (TLS) si se usa red.
- Considera retención y anonimización de datos por cumplimiento de privacidad
## Próximos pasos recomendados

- Añadir pruebas unitarias e2e para la lógica de `update_plate`.
- Extraer la capa de hardware a un adaptador que pueda simularse en tests.
- Documentar la API con `OpenAPI`/`Swagger` para facilitar integración.

## Contacto

Autores: Lizeth Carmona Davila, Anabell Ramirez, Miguel Angel Barrera, Maria Paulina Arenas, Luciana Chaverra, Salome Rios, Cristina Cardona
Repositorio: `ANPR-v7`

---
