# Guía de Despliegue (DevOps) - Descorcha.IA 🍷

Este documento detalla los pasos de configuración, parámetros y el estado del despliegue de **Descorcha.IA** en Vercel (Serverless), conectando el dominio **descorchaia.lat** gestionado en GoDaddy.

---

## 📋 Ficha Técnica del Proyecto

* **Estado del Deploy**: **`EXITOSO (READY)`**
* **URL de Producción Activa**: [https://wine-recommender-mvp.vercel.app](https://wine-recommender-mvp.vercel.app)
* **Rama de Producción**: `commercial-mvp`
* **Etiqueta de Deploy Estable**: `vercel-deploy-ready-v0.1`
* **Entry Point (Vercel)**: `api/index.py`
* **Especificaciones Vercel**: `vercel.json` configurado para enrutamiento Flask + Static Assets.
* **Manifiesto de Dependencias**: `requirements.txt` (liviano para acelerar builds serverless).

---

## ☁️ Estado de Configuración en Vercel

### ⚙️ Variables de Entorno Configuradas
Las siguientes variables han sido cargadas exitosamente en el entorno de producción de Vercel para gestionar las sesiones, el modo debug y el fallback de datos:

* `SECRET_KEY`: `somm_ai_secret_key_2026_vercel`
* `FLASK_DEBUG`: `False`
* `APP_ENV`: `production`
* `DATA_DIR`: `demo_data`

### 💻 Lanzamiento de Despliegues desde Vercel CLI
El proyecto está vinculado al workspace de Vercel de la cuenta `pabmena` bajo el proyecto `wine-recommender-mvp`. Para subir actualizaciones futuras en caliente desde la consola, ejecuta:

1. **Despliegue de prueba (Preview)**:
   ```bash
   npx vercel
   ```
2. **Promoción a producción final**:
   ```bash
   npx vercel --prod
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
