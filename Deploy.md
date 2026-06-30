# Guía de Despliegue (DevOps) - Descorcha.IA 🍷

Este documento detalla los pasos críticos, configuraciones y parámetros para realizar un despliegue limpio y exitoso de **Descorcha.IA** en Vercel (Serverless), conectando el dominio **descorchaia.lat** gestionado en GoDaddy.

---

## 📋 Ficha Técnica del Proyecto

* **Rama de Producción**: `commercial-mvp`
* **Etiqueta de Deploy Estable**: `vercel-deploy-ready-v0.1`
* **Entry Point (Vercel)**: `api/index.py`
* **Especificaciones Vercel**: `vercel.json` configurado para enrutamiento Flask + Static Assets.
* **Manifiesto de Dependencias**: `requirements.txt` (liviano para acelerar builds serverless).

---

## ☁️ Paso 1: Deploy en Vercel (Serverless Functions)

### ⚙️ Variables de Entorno Requeridas
Configura estas variables en **Settings** > **Environment Variables** del proyecto en Vercel antes del despliegue:

* `SECRET_KEY`: Clave de cifrado de sesiones de Flask (definir un valor complejo en producción).
* `FLASK_DEBUG`: `False`
* `APP_ENV`: `production`

### 💻 Método A: Despliegue desde Vercel Dashboard
1. Ingresa a [Vercel](https://vercel.com) y haz clic en **Add New** > **Project**.
2. Vincula e importa tu repositorio `pabmena/wine-recommender-mvp`.
3. Selecciona la rama **`commercial-mvp`**.
4. **Framework Preset**: Configúralo como **`Other`** (Vercel leerá automáticamente el archivo `vercel.json`).
5. Agrega las Variables de Entorno mencionadas arriba.
6. Haz clic en **Deploy**.

### 🛠️ Método B: Despliegue desde Vercel CLI
1. Instala el CLI de Vercel e inicia sesión:
   ```bash
   npm i -g vercel
   vercel login
   ```
2. Inicializa y vincula el proyecto en la raíz local:
   ```bash
   vercel
   ```
3. Realiza el despliegue final a producción:
   ```bash
   vercel --prod
   ```

---

## 🌐 Paso 2: Configuración del Dominio en GoDaddy + Vercel

### 1. Vincular el Dominio en Vercel
1. En el panel de tu proyecto en Vercel, ve a **Settings** > **Domains**.
2. Añade `descorchaia.lat`.
3. Añade `www.descorchaia.lat`.
4. **Redirección Canónica**: Configura que `www.descorchaia.lat` redirija automáticamente a la URL canónica sin www: **`https://descorchaia.lat`**.

### 2. Configurar los DNS en GoDaddy
Ingresa al administrador de DNS de GoDaddy para tu dominio `descorchaia.lat` y crea/modifica los siguientes registros indicados por Vercel:

| Tipo | Host / Nombre | Valor / Destino | TTL |
|---|---|---|---|
| **A** | `@` | `76.76.21.21` *(Confirmar valor exacto indicado en tu panel de Vercel)* | `600` (o default) |
| **CNAME** | `www` | `cname.vercel-dns.com` | `600` (o default) |

Una vez aplicados, la propagación de DNS suele demorar entre 10 minutos y 24 horas. Vercel autogenerará los certificados SSL/HTTPS de forma automática.

---

## 💾 Paso 3: Estrategia de Persistencia Efímera (SQLite)

Debido a que Vercel opera bajo una arquitectura serverless con sistema de archivos de solo lectura y efímero:
* **Tolerancia a fallos**: `config/analytics.py` conmuta de forma automática el DATABASE_PATH hacia `/tmp/analytics.db` si detecta el entorno Vercel.
* **Degradación Segura**: Si por alguna razón de entorno el filesystem no es accesible, los eventos se registran en memoria o se descartan sin interrumpir la ejecución de la app (no arroja error 500 al cliente). El dashboard de administración cargará con métricas en cero o datos demostrativos.
* **Recomendación para Producción**: *Para pilotos comerciales reales, se aconseja reemplazar SQLite por PostgreSQL (ej. Neon o Supabase) configurando el backend correspondientemente.*

---

## 🔞 Consumo Responsable
Descorcha.IA promueve el consumo responsable de bebidas alcohólicas. Prohibida su venta a menores de 18 años. Beber con moderación.
