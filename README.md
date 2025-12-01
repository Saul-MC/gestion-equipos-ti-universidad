## Gestión de Equipos de TI - Universidad Pública

Aplicación web modular para administrar proveedores, inventario de equipos, mantenimientos y reportes analíticos en una universidad pública. La solución utiliza microservicios en Python, Streamlit como frontend, PostgreSQL como base de datos y despliegue contenerizado con Docker Compose.

### Estructura del proyecto

- `frontend/`: Aplicación Streamlit que consume el API Gateway.
- `api_gateway/`: FastAPI que centraliza la comunicación con los microservicios.
- `services/`
  - `equipment_service/`
  - `provider_service/`
  - `maintenance_service/`
  - `report_service/`
- `common/`: Módulos compartidos (modelos, conexión a BD, utilidades).
- `db/schema.sql`: Definición del modelo relacional en PostgreSQL.
- `docs/architecture.md`: Diagramas de arquitectura, flujo de datos y ER.

### Requisitos previos

- Docker 24+
- Docker Compose 2.20+
- Make (opcional) o PowerShell

### Puesta en marcha

```powershell
docker compose up --build
```

Servicios clave:

- Streamlit: http://localhost:8501
- API Gateway: http://localhost:8000/docs
- Microservicios: puertos 8101-8104
- PostgreSQL: puerto 5432 (usuario `postgres`, contraseña `postgres`)

### Variables de entorno

Cada servicio acepta las siguientes variables (ver `docker-compose.yml`):

- `DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/it_assets`
- `SERVICE_URL_*` en el gateway (`EQUIPMENT_SERVICE_URL`, etc.)
- `NOTIFICATION_EMAIL` y `REMINDER_DAYS` en mantenimiento para configurar alertas.

### Migraciones / esquema

Ejecutar el contenido de `db/schema.sql` dentro del contenedor de PostgreSQL:

```powershell
docker compose exec postgres psql -U postgres -d it_assets -f /app/db/schema.sql
```

### Acceso a la base de datos

Para inspeccionar tablas y datos directamente, consulta el documento detallado:

📄 **[Ver guía completa de acceso a PostgreSQL](docs/ACCESO_BASE_DATOS.md)**

**Acceso rápido:**
```powershell
# Conectarse a PostgreSQL
docker compose exec postgres psql -U postgres -d it_assets

# Ver todas las tablas
\dt

# Ver datos de una tabla
SELECT * FROM suppliers;
SELECT * FROM equipment;
```

### Poblar datos de prueba

Para cargar datos ficticios en todas las tablas y probar el sistema completo:

```powershell
docker compose exec postgres psql -U postgres -d it_assets -f /app/db/seed_data.sql
```

Esto insertará:
- **3 usuarios** (admin, tecnico, usuario)
- 5 proveedores de ejemplo
- 5 contratos asociados
- 12 equipos de TI (laptops, servidores, switches, impresoras)
- 5 movimientos de equipos
- 8 tareas de mantenimiento programadas
- 4 bitácoras de mantenimiento completadas

### Inicio de sesión

El sistema incluye autenticación basada en base de datos. **Primero debes poblar los datos de prueba** (ver sección anterior).

Usuarios de prueba (después de poblar datos):
- **Admin**: `admin` / `admin123`
- **Técnico**: `tecnico` / `tecnico123`
- **Usuario**: `usuario` / `usuario123`

Accede en: http://localhost:8501

📄 **[Ver documentación completa de autenticación](docs/AUTENTICACION.md)**

### Pruebas rápidas

1. **Iniciar sesión** en http://localhost:8501
2. **Poblar datos de prueba** (ver sección anterior)
3. **Explorar el Dashboard** para ver métricas y gráficos
4. **Gestionar proveedores** y contratos
5. **Registrar y actualizar equipos**
6. **Programar mantenimientos** y registrar reparaciones
7. **Exportar reportes** en PDF y Excel

### Automatización inteligente

El microservicio de mantenimiento incorpora un agente basado en `APScheduler` que:

- Revisa mantenimientos próximos (cada 12 horas)
- Genera recordatorios para tareas dentro de `REMINDER_DAYS` (por defecto 7 días)
- Marca equipos obsoletos cuando superan su vida útil (`OBSOLETE_YEARS`)

📄 **[Ver guía completa para probar el agente](docs/PRUEBA_AGENTE_RECORDATORIOS.md)**

### Exportación de reportes

`report_service` expone `/reports/export` con parámetro `format=pdf|excel` para descargar archivos generados dinámicamente (usa `reportlab` y `pandas`).

### Solución de problemas

Si encuentras errores de Docker (I/O errors, problemas con containerd), consulta:

📄 **[Guía de solución de errores Docker](SOLUCION_ERROR_DOCKER.md)**

### Subir a GitHub

Para compartir este proyecto en GitHub:

📄 **[Guía completa para subir a GitHub](docs/GUIA_GITHUB.md)**

**Resumen rápido:**
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/nombre-repo.git
git push -u origin main
```

### Personalización

- Ajustar políticas de autenticación en el API Gateway.
- Extender agentes inteligentes conectándolos a colas (RabbitMQ) o bots (Teams/Slack).
- Añadir pruebas automáticas con `pytest`.

### Licencia

MIT. Uso académico permitido.

