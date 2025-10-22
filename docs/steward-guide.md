# Guía para Stewards (ES) / Kamachiypaq Qillqasqa (Quechua encabezados)

Objetivo
- Enviar alertas confiables por SMS a quienes se suscriben (SALUD, PRECIO, COMUNIDAD).
- Proteger la privacidad de las personas y la autodeterminación de la comunidad.

1) Consentimiento comunitario (FPIC)
- Realizar asamblea informada y libre.
- Registrar el acuerdo:
  yachay-wasi community-consent --status granted --reason "Asamblea 2025-10-25"
- Para pausar el servicio:
  yachay-wasi community-consent --status revoked --reason "Motivo"

2) Crear phonebook.csv (archivo sensible)
- Formato CSV con cabeceras: msisdn_hash,msisdn
- msisdn_hash: calcular con la misma "salt" de config.toml (usar script local).
- msisdn: número con prefijo país, ej. +51987654321
- Ubicación recomendada (config.toml): /opt/yachay-wasi/phonebook.csv

Seguridad del phonebook
- Guardar en USB cifrado (LUKS/veracrypt).
- Nunca enviarlo por correo ni mensajería.
- Rotar trimestralmente: generar un phonebook nuevo desde el padrón local; verificar que la "salt" no cambie sin plan de migración.
- Si se decide cambiar la "salt", se requiere procedimiento de re-consentimiento o migración técnica (ver ethics/threat-model).

3) Enviar alertas
- Salud:
  yachay-wasi broadcast --topic salud --text "Dra. Elena llega mañana, 8 a.m."
- Precios:
  yachay-wasi broadcast --topic precio --text "Papa S/.1.30 en feria K" 
- Comunidad:
  yachay-wasi broadcast --topic comunidad --text "Asamblea 6 pm en local comunal"

Resultados del comando
- Muestra un resumen: total, resueltos, enviados OK, fallas y no resueltos.
- Los detalles técnicos se guardan en el registro del sistema (no saturan la pantalla).

4) Impresión de tarjetas de código de usuario
- Cada persona recibe (opcional) una tarjeta con: Tópicos elegidos y su código de 4 dígitos.
- Sirve para revocar con confianza (STOP) y para auditoría local.

5) Mantenimiento
- Revisar SIM (PIN activado), energía y señal GSM.
- Respaldar la base de datos local cifrada.
- TTL y limpieza: mensajes viejos se purgan periódicamente (política local).
- Auditoría trimestral de accesos y del USB del phonebook.

6) Frases útiles (Quechua)
- Suscripción: “Kuti qillqay SALUD / PRECIO / COMUNIDAD.”
- Salir: “Qhipaman: STOP.”
- Aviso inactivo: “Llank'ayqa sayarimun, llapa runakunapa qillqasqayuq mana kanqa chaykama.”
