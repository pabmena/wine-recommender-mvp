# Descorcha.IA 🍷

**Descorcha.IA** es una plataforma SaaS de recomendación personalizada de vinos impulsada por Inteligencia Artificial y Procesamiento de Lenguaje Natural (PLN). Ayuda a vinotecas locales y tiendas de e-commerce a mejorar la experiencia de compra de sus consumidores mediante un recomendador adaptativo inspirado en Tastry, optimizando la rotación del stock real y registrando métricas comerciales en tiempo real.

---

## 🚀 Rutas Principales

### 💼 Portal B2B / Comercial
* **Landing de Ventas B2B**: `/commercial`  
  Presentación comercial del servicio SaaS con formulario Ajax integrado de Formspree para captación de clientes.
* **Dashboard de Analíticas**: `/admin/demo_vinoteca/dashboard`  
  Métricas en tiempo real (conversión de quizzes, clics a WhatsApp, likes, dislikes, embudo de abandono).

### 🛒 Experiencia de Cliente (B2C)
* **Página de Inicio / Landing de Vinoteca**: `/c/demo_vinoteca`  
  Home del comercio adherido con su branding, logo y acceso al recomendador.
* **Quiz Adaptativo**: `/c/demo_vinoteca/quiz`  
  Cuestionario visual-emocional que calibra las preferencias del paladar y la intención de compra.
* **Resultados Personalizados**: `/c/demo_vinoteca/results`  
  Recomendaciones agrupadas en pestañas interactivas, explicaciones sensoriales y chatbot asistente integrado.

---

## 🛠️ Instalación Local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/pabmena/wine-recommender-mvp.git
   cd wine-recommender-mvp
   git checkout commercial-mvp
   ```

2. **Crear y activar un entorno virtual**:
   * **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias**:
   * Para desarrollo local completo:
     ```bash
     pip install -r requirements-dev.txt
     ```
   * Para entorno productivo liviano:
     ```bash
     pip install -r requirements.txt
     ```

4. **Configurar Variables de Entorno**:
   Copia el archivo de ejemplo y edítalo:
   ```bash
   cp .env.example .env
   ```

---

## ⚙️ Variables de Entorno (.env)

El proyecto lee variables del sistema mediante `python-dotenv`:
* `SECRET_KEY`: Clave de cifrado de sesiones de Flask (definir un valor complejo en producción).
* `FLASK_DEBUG`: `True` para desarrollo, `False` en producción.
* `PORT`: Puerto donde escucha la aplicación local (por defecto `5000`).
* `APP_ENV`: Define si corre en `development` o `production`.
* `DATA_DIR`: Directorio de fallback de datos (por defecto `demo_data`).

---

## 💻 Comandos de Ejecución y QA

### Ejecutar la Aplicación en Desarrollo
```bash
python app.py
```
Abre en tu navegador `http://127.0.0.1:5000/commercial`.

### Ejecutar las Pruebas de QA y Validación
El sistema posee scripts que certifican que el catálogo, el motor y las analíticas en SQLite operen de manera íntegra:

1. **Validación de la Experiencia del Quiz Adaptativo**:
   ```bash
   python scripts/validate_quiz_experience.py
   ```
   *Verifica las reglas de descarte de extremos en regalos, combinaciones de intenciones y la persistencia física de eventos en la base de datos.*

2. **Validación del MVP Comercial**:
   ```bash
   python scripts/validate_commercial_mvp.py
   ```
   *Audita las métricas e integración general del sistema.*

Los reportes en Markdown e informes en JSON se generarán en la carpeta `reports/`.

---

## ☁️ Deploy en Vercel (Serverless)

La aplicación está completamente optimizada para ejecutarse en la infraestructura Serverless de Vercel.

### Especificaciones Técnicas del Proyecto en Vercel
* **Rama recomendada**: `commercial-mvp`
* **Framework Preset**: `Other` (Vercel detectará el archivo `vercel.json` automáticamente)
* **Runtime**: `Python`
* **Entry Point (Función)**: `api/index.py` (Llama a la app de Flask en `app.py`)
* **Uso de Datos**: Si no encuentra la carpeta de desarrollo `data/`, realiza un fallback automático e íntegro a `demo_data/` versionada en el repositorio.
* **Nota sobre la Base de Datos**: *En Vercel, SQLite se usa solo en modo demo/no persistente escribiendo en la carpeta temporal `/tmp/analytics.db`. Para pilotos reales de producción se recomienda conectar una base de datos PostgreSQL mediante Supabase, Neon o Vercel Postgres.*

### Variables de Entorno Requeridas en Vercel
Configura en las **Settings** del proyecto en Vercel:
* `SECRET_KEY` = *[Clave secreta segura]*
* `FLASK_DEBUG` = `False`
* `APP_ENV` = `production`

### Método A: Deploy desde Vercel Dashboard (Recomendado)
1. Entrá a tu cuenta de Vercel y hacé clic en **Add New** > **Project**.
2. Importá el repositorio `pabmena/wine-recommender-mvp`.
3. Seleccioná la rama `commercial-mvp`.
4. Dejá el **Framework Preset** como `Other`.
5. Expandí **Environment Variables** y agregá `SECRET_KEY`, `FLASK_DEBUG` y `APP_ENV`.
6. Hacé clic en **Deploy**.

### Método B: Deploy desde Vercel CLI
1. Instalá Vercel globalmente si no lo tenés:
   ```bash
   npm i -g vercel
   ```
2. Logueate e iniciá el asistente interactivo en la raíz del proyecto:
   ```bash
   vercel login
   vercel
   ```
3. Para deployar a producción:
   ```bash
   vercel --prod
   ```

---

## 🌐 Configuración del Dominio en GoDaddy + Vercel

Para apuntar tu dominio **`descorchaia.lat`** a la aplicación en Vercel:

### Paso 1: Configurar el Dominio en Vercel
1. Ve al panel de tu proyecto en Vercel en **Settings** > **Domains**.
2. Agregá el dominio raíz: `descorchaia.lat`
3. Agregá el subdominio: `www.descorchaia.lat`
4. **URL Canónica**: Configurá en Vercel que `www.descorchaia.lat` redirija automáticamente al dominio raíz **`https://descorchaia.lat`** para mantener un SEO óptimo y limpio.

### Paso 2: Configurar los registros DNS en GoDaddy
Ingresá al administrador de DNS de tu dominio en GoDaddy y agregá/modificá los siguientes registros que te proporcionará Vercel:

1. **Para el dominio raíz (`descorchaia.lat`)**:
   * **Tipo**: `A`
   * **Nombre / Host**: `@`
   * **Valor / Destino**: `76.76.21.21` *(Confirmar valor exacto en el panel de Vercel)*
   * **TTL**: `600` (o por defecto)

2. **Para el subdominio (`www.descorchaia.lat`)**:
   * **Tipo**: `CNAME`
   * **Nombre / Host**: `www`
   * **Valor / Destino**: `cname.vercel-dns.com`
   * **TTL**: `600` (o por defecto)

Una vez aplicados, la propagación de DNS suele demorar entre 10 minutos y 24 horas. Vercel generará el certificado SSL/HTTPS automáticamente.

---

## 🔞 Consumo Responsable
Descorcha.IA promueve el consumo responsable de bebidas alcohólicas. Prohibida su venta a menores de 18 años. Beber con moderación.

---
**Desarrollado por**: Pablo Menardi  
**Email de Contacto**: pabmena@yahoo.com