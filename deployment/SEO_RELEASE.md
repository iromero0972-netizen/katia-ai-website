# KATIA — preparación de publicación SEO / IA

La revisión de Sites conserva acceso privado, `noindex,nofollow` y `Disallow: /`. La implementación de SEO no publica en katia.solutions ni solicita indexación.

## Lo que queda implementado

- 54 documentos bilingües: 12 páginas principales, 14 de servicios y 28 fichas para los 14 proyectos.
- Títulos, descripciones, canonical, hreflang recíproco y metadatos sociales.
- Entidad Organization con identificador estable, logo, fundador y perfiles oficiales; datos Service, CreativeWork, ItemList y BreadcrumbList donde corresponden.
- Catálogo y páginas de servicios enlazados mediante `<a href>`. Portadas originales y estados de desarrollo conservados.
- FAQs de integración, datos y alcance; información breve de la agencia y del fundador.
- Imagen social incluida en el paquete y eliminación de la precarga del hero de Inicio en páginas interiores.
- Eventos de intención de contacto y agenda separados de solicitudes recibidas, sujetos a consentimiento y solo en el dominio público.
- Sitemap de las 54 URLs canónicas. La preparación de producción lo combina con el sitemap existente.

## Preparar el candidato sin publicar

1. Ejecutar `python scripts/render-seo.py` y las validaciones descritas en README.
2. Revisar el HEAD del repositorio de producción. La base auditada está fijada en `deployment/migration.json`; si cambia, revisar los cambios antes de actualizar el valor.
3. Ejecutar `python scripts/prepare-production.py --baseline /ruta/checkout-produccion --output /ruta/nuevo-candidato`.
4. El candidato conserva las páginas anteriores, CNAME, verificaciones, activos y configuración del repositorio. Sobrescribe únicamente las rutas nuevas o actualizadas del diseño. No hace falta redirigir páginas que se conservan en su URL.
5. Ejecutar `python scripts/check-seo.py --root /ruta/nuevo-candidato --mode production` y `node scripts/check-site.js` desde el candidato.
6. La publicación debe usar el candidato completo; nunca reemplazar todo el repositorio del dominio con solo `dist/`.

`apps.html` mantiene su URL. `?lang=en` continúa funcionando en el cliente y lleva a la página inglesa equivalente. Se conservan los 301 existentes para HTTP y www. Las rutas antiguas de consulta, método, casos, recursos e industrias permanecen disponibles para conservar contenido y enlaces existentes. Si después se decide retirarlas, preparar redirecciones de servidor a destinos equivalentes y actualizar el sitemap en la misma entrega.

## Acciones externas que siguen pendientes antes o después de publicar

No están disponibles en esta sesión conexiones a Cloudflare, Search Console, Bing Webmaster Tools ni a los registros de reservas. No se simula que esos controles estén aplicados.

### Cloudflare / rastreo, antes de publicar

- Unificar la política del `robots.txt` servido con `deployment/robots.production.txt`. El archivo propone conservar las restricciones observadas en Cloudflare Managed Content y permitir los rastreadores de búsqueda.
- Revisar la opción de robots administrado: no añadir un bloque que contradiga el origen. Comprobar la respuesta final servida después de la publicación, no solo el archivo del repositorio.
- Mantener WAF y límites de solicitudes. Permitir tráfico legítimo de buscadores con los mecanismos de validación/IP de los proveedores; no fiarse solo del User-Agent.
- No exigir autenticación o desafíos a los documentos públicos destinados a búsqueda. Mantener autenticadas las apps, datos y endpoints privados.
- Las políticas de Google-Extended y otros rastreadores no equivalen al acceso de Googlebot. La decisión de entrenamiento/otros usos no es un requisito para Google Search ni para OAI-SearchBot.

### Google y Bing, después de publicar

- Verificar la propiedad existente sin sustituir tokens por valores inventados. Inspeccionar Inicio, Servicios, Apps y un proyecto ES/EN.
- Enviar `https://katia.solutions/sitemap.xml` tras comprobar 200 y ausencia de noindex en producción. Nunca enviar la URL privada.
- Revisar AI Performance de Bing y los informes de Search Console disponibles en la cuenta. Un acceso de un bot no prueba una cita o recomendación.
- La automatización IndexNow queda actualizada para leer el sitemap, en lugar de una lista fija. El candidato instala el workflow de `deployment/indexnow.yml`. El envío exige la rama main del repositorio correcto y comprueba que el sitemap público ya contiene las URLs. Si GitHub Pages aún no ha terminado, falla sin enviar: reejecutarlo después de publicar. El modo por defecto del script es dry-run.

### Medición comercial

| Evento | Qué significa | Qué no demuestra |
|---|---|---|
| `contact_intent` + channel=phone/whatsapp/email | Clic en un canal | Conversación, lead válido o venta |
| `booking_intent` + channel=calendar | Apertura de Calendly | Cita confirmada |
| `lead_form_submit` + service | Respuesta exitosa del endpoint al formulario | Calificación del lead o cita |
| Cita confirmada en agenda/CRM | Reserva real comprobada | Venta cerrada |

El código de medición no envía nombre, correo, teléfono, contenido del mensaje ni URLs de WhatsApp con texto. No crea `booking_confirmed`: ese dato necesita una integración autenticada de agenda o conciliación del registro de reservas. Los eventos no se emiten si se rechaza el consentimiento o si se visita la revisión privada.

## Validación al publicar

No se han enviado formularios, mensajes, correos, consultas a los agentes ni solicitudes de IndexNow durante esta preparación. Confirmar la entrega real, los controles de `SECURITY_OPERATIONS.md` del repositorio de producción y la medición de la agenda antes de dar la operación por validada. Medir Core Web Vitals en el dominio público; el tamaño de archivos no sustituye esa medición.

## Fuentes técnicas

- Google: https://developers.google.com/search/docs/appearance/ai-features
- OpenAI: https://developers.openai.com/api/docs/bots
- Anthropic: https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
- Perplexity: https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- Schema.org: https://schema.org/Service y https://schema.org/creativeWorkStatus

No se añaden licencias profesionales de Texas, certificaciones, alianzas oficiales, reseñas ni cifras de resultados no documentadas.
