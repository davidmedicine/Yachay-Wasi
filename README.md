Yachay-Wasi — Mensajero de IA Offline Gobernado por la Comunidad (SMS)

Vista previa de investigación (v0.1)

Yachay-Wasi es un sistema de conocimiento y alertas por SMS, diseñado como offline-first, pensado para contextos rurales donde el acceso a internet es poco confiable. Funciona de manera local (por ejemplo, en una Raspberry Pi) y, de forma opcional, puede ofrecer respuestas asistidas por IA usando un LLM local, siempre con consentimiento y gobernanza comunitaria.

Este repositorio forma parte de Qori Labs (Laboratorio de Tecnología de Interés Público): construimos “Capas Soberanas” donde la conectividad, la cognición (IA local) y la gobernanza están diseñadas para el control local.

Qué hace
1) Consultas de conocimiento por SMS (offline)

Ejemplos:

PRECIO papa → precios de referencia locales (desde una base de conocimiento curada por custodios)

CLIMA → consejos agronómicos locales (no es un pronóstico del tiempo)

HISTORIA pachamama → relatos culturales aprobados (si está habilitado)

2) Alertas comunitarias (difusión por SMS)

Los temas pueden incluir:

SALUD, COMUNIDAD, PRECIO (configurable)

3) Respuestas opcionales con IA local (solo si está habilitado y autorizado)

Ejecuta un modelo local pequeño mediante llama.cpp (sin nube)

Mantiene las respuestas cortas (aptas para SMS)

Gobernanza y consentimiento (requisito central)

Yachay-Wasi está diseñado para operar bajo autoridad local:

Consentimientos separados:

Consentimiento del servicio (sistema SMS)

Consentimiento de IA (funciones de inferencia local)

STOP revoca suscripciones (y puede extenderse para revocar el acceso a IA).

La gobernanza es aplicable localmente (herramientas de custodia + control offline).

Privacidad por diseño (offline-first)

Sin nube por defecto.

No se requiere telemetría externa.

El almacenamiento puede configurarse para minimizar la retención de datos.

Los identificadores telefónicos pueden ser hasheados; el mapeo offline puede quedar en manos de los custodios.

Cómo funciona (arquitectura)

Gammu SMSD escribe los SMS entrantes en un spool local.

sms_bridge analiza los mensajes, aplica las reglas de consentimiento y enruta las solicitudes.

La base de conocimiento local proporciona contenido de referencia aprobado (archivos CSV/YAML).

Si la IA está habilitada y autorizada, el puente llama al LLM local para generar una respuesta corta.

Las respuestas se devuelven por SMS.

Todo se ejecuta en el dispositivo local.

Requisitos

Raspberry Pi 4 (4GB recomendado; 2GB mínimo)

Módem GSM compatible con Gammu

Linux, Python 3, SQLite, Gammu/SMSD

llama.cpp + un modelo pequeño cuantizado (por ejemplo, TinyLlama q4) si se usa el modo IA

Inicio rápido (alto nivel)
Configurar

Copiar config.toml.example → config.toml y definir:

rutas (sqlite, directorio de entrada)

ubicación del mapeo de la agenda telefónica (opcional)

configuración de IA (desactivada por defecto)

Inicializar
python3 -m src.cli init-db


Configurar consentimiento (ejemplo):

yachay-wasi consent --status granted --reason "Asamblea YYYY-MM-DD"


(Opcional) Habilitar IA solo después de un consentimiento separado:

yachay-wasi ai-consent --status granted --reason "Acta IA YYYY-MM-DD"
yachay-wasi ai --enable


Ejecutar:

python3 -m src.sms_bridge

Notas de seguridad

Usar conjuntos de datos públicos, permitidos o sintéticos para demostraciones.

Evitar contenido personal sensible.

Los mensajes de salud deben ser educativos y derivar a trabajadores de salud locales.

Este es un prototipo de investigación; validar localmente antes de su uso en campo.

Licencia

MIT. (La custodia comunitaria es una norma de gobernanza incluso cuando el código es abierto.)
