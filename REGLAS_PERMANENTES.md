# REGLAS PERMANENTES — Proyecto KATIA.ai Website
# Este archivo NUNCA se borra. Se mantiene en la raíz del proyecto.
# Claude Code DEBE leer este archivo antes de hacer CUALQUIER cambio.

---

## IDENTIDAD

- Nombre: KATIA.ai
- Tipo: AI Automation Agency
- Ubicación: Katy, Texas
- Audiencia: Comunidad latina de Houston / PYMEs en Texas
- Fundador: Ignacio Romero, CPA (+30 años experiencia)

---

## REGLAS INQUEBRANTABLES

### 1. IDIOMA
- TODO el contenido visible debe estar en ESPAÑOL
- Excepciones permitidas: términos técnicos (workflow, dashboard, CTA, build, testing, go-live)
- Si un cambio introduce texto en inglés, ESTÁ MAL. Revertir.

### 2. CONTACTO
- Email: iromero0972@gmail.com
- WhatsApp: https://wa.me/19546997514?text=Hola%2C%20quiero%20un%20diagn%C3%B3stico%20gratuito%20para%20mi%20negocio
- NUNCA usar ignacio@katia.ai (no existe)
- NUNCA cambiar el número de WhatsApp
- NUNCA cambiar el mensaje de WhatsApp a inglés

### 3. ASSETS
- Todas las imágenes van en: assets/img/
- Paths SIEMPRE relativos: assets/img/nombre.ext
- NUNCA usar paths absolutos con URL de GitHub
- NUNCA borrar imágenes existentes al hacer updates
- Antes de hacer push, verificar: ls assets/img/ | wc -l (debe ser > 10)

### 4. ESTRUCTURA
- UN SOLO ARCHIVO: index.html con CSS y JS inline
- NO crear archivos CSS separados
- NO crear archivos JS separados
- NO usar frameworks (React, Vue, etc.)
- Google Fonts via CDN es lo único externo permitido

### 5. DISEÑO
- Paleta: Navy #0B1220, Blue #4A9ED6, Gold #C9A84C
- Font display: Syne (Google Fonts)
- Font body: DM Sans (Google Fonts)
- H1: mínimo clamp(2.8rem, 6.5vw, 4.8rem)
- Los colores deben tener PRESENCIA — nada pálido ni fantasma

### 6. CONTENIDO QUE NO SE TOCA
- Andy's Bakery es un caso de éxito REAL — no inventar otros
- La bio de Ignacio Romero: "+30 años como CPA" — no cambiar
- Los 6 servicios están definidos — no reducir a 4
- Las 3 secciones de historia (Visión, Infraestructura, Casos) — no eliminar

### 7. PROCESO DE CAMBIOS
- SIEMPRE leer este archivo antes de editar
- NUNCA parchar — si hay que cambiar estructura, reescribir la sección completa
- Después de cada cambio, verificar:
  ```bash
  # Sin inglés en el contenido visible
  grep -i "services\|about us\|how we work\|contact us\|free demo\|learn more" index.html | grep -v "<!--" | wc -l
  # Debe ser 0

  # Email correcto
  grep -c "iromero0972@gmail.com" index.html
  # Debe ser > 0

  # Sin email viejo
  grep -c "ignacio@katia.ai" index.html
  # Debe ser 0

  # Assets intactos
  ls assets/img/ | wc -l
  # Debe ser > 10
  ```

### 8. GIT
- Commits en español: "Actualizar sección X", "Agregar imagen Y"
- NUNCA force push sin confirmación del usuario
- NUNCA eliminar el repositorio sin confirmación
- Este archivo (REGLAS_PERMANENTES.md) SIEMPRE debe estar en el commit

---

## ERRORES PASADOS QUE NO SE REPITEN

| Error | Nunca más |
|---|---|
| Dejar la página en inglés | TODO en español siempre |
| Usar ignacio@katia.ai | Solo iromero0972@gmail.com |
| Borrar imágenes al actualizar HTML | Verificar assets/ antes de push |
| Reducir servicios de 6 a 4 | Siempre 6 servicios |
| No integrar fotos del usuario | Verificar que las imágenes carguen |
| Paleta pálida/fantasma | Colores con presencia visible |
| No poner video en hero | Video autoplay muted loop |
| Parchar en vez de reescribir | Si la instrucción dice reescribir, se reescribe |

---

## METODOLOGÍA IRVSG (aplica a este proyecto)

- INVESTIGACIÓN antes de actuar
- PLANEACIÓN completa antes de build
- TESTEO antes de deploy
- RETROALIMENTACIÓN después de cada iteración
- Zero improvisación
- N8N es la plataforma exclusiva de workflows
