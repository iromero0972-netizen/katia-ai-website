# Seguridad de producción: controles externos obligatorios

Este repositorio reduce superficie de ataque en el navegador, pero **no puede sustituir los controles del servidor**. Antes de publicar esta rama se deben activar estos controles:

1. **Cloudflare delante de katia.solutions y de los webhooks públicos**: WAF administrado, rate limit por IP/ruta, Bot Fight Mode y TLS mínimo 1.2.
2. **n8n**: actualizar a una versión corregida vigente, deshabilitar editor público, MFA/SSO donde aplique, credenciales solo en el vault, logs sin datos sensibles y backups cifrados.
3. **Webhooks de lead y chat**: validar origen y esquema del payload en n8n, limitar solicitudes, rechazar SSN/ITIN/tarjetas, deduplicar leads y alertar ante picos de error.
4. **Cloudflare Turnstile**: crear las claves en Cloudflare, verificar el token en n8n/Worker y nunca guardar el secret en HTML ni en GitHub.
5. **GitHub**: activar MFA, Secret Scanning, Dependabot alerts, protección de main con la verificación Site quality gate obligatoria y revisión antes de merge.
6. **Operación**: rotar credenciales comprometidas o antiguas, usar 1Password/Bitwarden, MFA con llave física y acceso mínimo necesario.

El navegador aplica límites de volumen y bloquea datos de alto riesgo como capa de experiencia; la validación decisiva debe ocurrir en el servidor.