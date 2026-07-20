# Runbook de producción: KATIA.AI, Cloudflare y n8n

Este repositorio no contiene secretos. Guarde contraseñas, tokens y claves solo en el vault de n8n o en variables protegidas del servidor.

## Aplicación inicial

1. Haga backup cifrado de la base de datos y exporte los workflows. Registre la versión mediante `n8n --version`.
2. Ejecute `n8n audit`. Resuelva cualquier webhook crítico sin protección, nodo riesgoso, credencial inactiva y versión desactualizada antes de seguir.
3. Actualice n8n a una versión corregida vigente. Pruebe primero en staging y no mezcle versiones entre main, worker y runner.
4. Rote credenciales antiguas, expuestas o compartidas; cada integración usa una credencial de mínimo privilegio.

## Cloudflare

Aplique estos controles a `katia.solutions` y al hostname público que sirva los webhooks.

- TLS Full (strict), TLS mínimo 1.2 y redirección HTTP a HTTPS.
- WAF Managed Rules y Bot Fight Mode activados.
- Rate limit de `/webhook/katia2-lead-capture`: cinco solicitudes por IP cada diez minutos; acción Managed Challenge.
- Rate limit del endpoint de chat: veinte solicitudes por IP cada diez minutos; acción Managed Challenge.
- Bloquee `/rest/*`, `/api/*` y el editor de n8n salvo VPN o allowlist administrativa.
- Revise cada día durante una semana los picos 4xx/5xx y las reglas activadas.

## Turnstile y n8n

1. Cree el widget Turnstile para `katia.solutions`.
2. El secret key se queda únicamente en n8n/servidor, nunca en HTML, JavaScript ni GitHub.
3. El primer nodo del workflow valida el token en `https://challenges.cloudflare.com/turnstile/v0/siteverify`.
4. Sin token válido, responda 400 y no ejecute Gmail, CRM ni Sheets.
5. Valide payload, longitudes y campos permitidos; rechace SSN/ITIN, tarjetas, datos bancarios y campos inesperados.
6. Deduzca una clave de idempotencia con email normalizado, empresa y ventana temporal; descarte duplicados.

## Controles de n8n

- Mantenga `N8N_ENCRYPTION_KEY` persistente fuera del repositorio.
- Editor con MFA/SSO cuando aplique; administrador único y acceso por VPN o allowlist.
- No instale community nodes sin revisión; bloquee nodos de comandos/archivos si no son necesarios.
- Restrinja la API pública y no exponga puertos internos del editor.
- Configure retención mínima de ejecuciones y no conserve PII más tiempo del necesario.
- Backups cifrados y prueba de restauración trimestral.

## Criterios de aceptación

- [ ] Una solicitud válida crea un solo lead.
- [ ] Sin Turnstile, n8n responde 400 y no crea lead.
- [ ] Seis solicitudes repetidas activan challenge o bloqueo.
- [ ] Un payload con SSN o tarjeta se rechaza y no se registra.
- [ ] El editor n8n no abre desde una red pública.
- [ ] `n8n audit` no muestra un webhook crítico sin protección.
- [ ] Restauración de backup validada en entorno aislado.
