# Roadmap de Evolución Arquitectónica - Descorcha.IA 🚀

Este documento detalla las mejoras y adaptaciones recomendadas para escalar el MVP de **Descorcha.IA** hacia una plataforma SaaS B2B multitenant robusta y de nivel de producción.

---

## 🗺️ Próximas Iteraciones de Arquitectura

### 1. Aislamiento de URL por Cliente (White-Label Estricto)
* **Situación Actual**: Las rutas `/c/<client_slug>/quiz` y `/c/<client_slug>/results` salvan el `client_id` en sesión y redirigen físicamente a `/quiz` y `/results`. Aunque funcional, rompe la estética de marca blanca al cambiar la URL.
* **Solución Propuesta**:
  - Eliminar los redireccionamientos.
  - Hacer que `/c/<client_slug>/quiz` y `/c/<client_slug>/results` manejen de forma nativa la lógica y rendericen `quiz.html` y `results.html` directamente.
  - Modificar los endpoints Ajax de llamadas dinámicas del quiz para enviar el parámetro `client_slug` en los headers o cuerpo del POST, manteniendo la barra de navegación del navegador bloqueada en el contexto del comercio (ej. `https://descorchaia.lat/c/demo_vinoteca/quiz`).

### 2. Migración de Base de Datos (SQLite a PostgreSQL/Neon)
* **Situación Actual**: SQLite se almacena de forma efímera en `/tmp/analytics.db` en el entorno serverless de Vercel. Esto borra las métricas del dashboard cada vez que la función serverless se inactiva.
* **Solución Propuesta**:
  - Conectar una base de datos relacional hosted (PostgreSQL en Neon, Supabase o Vercel Postgres).
  - Configurar las credenciales seguras mediante la variable de entorno `DATABASE_URL`.
  - Crear un pool de conexiones resiliente en `config/analytics.py`.

### 3. Caching y Carga de Catálogos
* **Situación Actual**: Los catálogos de los clientes se leen como archivos CSV locales mediante `pandas.read_csv`.
* **Solución Propuesta**:
  - Almacenar los catálogos en base de datos.
  - Implementar Redis en Vercel KV para cachear las recomendaciones de catálogos y vectores, optimizando la velocidad del quiz serverless.
