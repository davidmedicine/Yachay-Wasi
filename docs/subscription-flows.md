# Flujo de Suscripción (SMS)

1) La comunidad otorga consentimiento (FPIC) en asamblea.
   El steward registra:
   yachay-wasi community-consent --status granted --reason "Asamblea 2025-10-25"

2) Personas se suscriben por SMS:
   Usuario: SALUD
   Sistema: Gracias. Recibirás alertas de [SALUD]. Tu código es 8392. Di STOP para salir.

   Usuario: PRECIO
   Sistema: Gracias. Recibirás alertas de [PRECIO]. Tu código es 2741. Di STOP para salir.

   Usuario: COMUNIDAD
   Sistema: Gracias. Recibirás alertas de [COMUNIDAD]. Tu código es 5160. Di STOP para salir.

3) Revocación (individual):
   Usuario: STOP
   Sistema: Has salido de SALUD, PRECIO y COMUNIDAD. Gracias por usar Yachay Wasi.

Notas:
- Si la comunidad aún no otorga consentimiento, el sistema responde: “El servicio está inactivo hasta el consentimiento de la comunidad. Consulta con la persona encargada.”
- Códigos de usuario: 4 dígitos (fáciles de recordar) en Fase 1. En el futuro se pueden usar 6 dígitos o alfanuméricos.
