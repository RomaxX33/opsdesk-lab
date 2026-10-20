# OpsDesk Lab — Diagnóstico inicial

**Fecha del diagnóstico:** 19 de octubre de 2026
**Estado:** Auditoría inicial completada; CRUD todavía no implementado.

## Nota de seguimiento — 20 de octubre de 2026

Tras la auditoría se generó y verificó una copia de seguridad restaurable. Se creó el rol de ejecución `opsdesk_runtime` y se comprobó que no puede crear tablas ni roles ni conectarse a `opsdesk_restore_test`. La aplicación utiliza este rol; las comprobaciones de salud y disponibilidad continúan funcionando.

El rol `opsdesk_app` permanece como superusuario administrativo inicial del clúster local, porque no puede retirar su propio atributo `SUPERUSER`. Por tanto, la aplicación ya no utiliza esa cuenta para sus conexiones normales, pero el entorno local no debe considerarse completamente endurecido para producción.

Todavía no existe una tabla `incidents` ni una migración implementada. La siguiente fase deberá introducir el esquema mediante una migración revisada y conceder al rol de ejecución únicamente los permisos necesarios.

## 1. Estado del repositorio

- Rama: `main`.
- Último estado comprobado: limpio y sincronizado con `origin/main`.
- No se han realizado cambios de código ni de esquema de base de datos durante esta auditoría.
- Archivos principales: `app/main.py`, `requirements.txt`, `Dockerfile`, `compose.yaml`, `.env.example`, `README.md` y `docs/architecture.md`.

## 2. Dependencias y arquitectura comprobadas

Dependencias declaradas en `requirements.txt`:

- `fastapi>=0.115,<1.0`
- `uvicorn[standard]>=0.34,<1.0`
- `psycopg[binary]>=3.2,<4.0`

Infraestructura observada:

- Python 3.13 como imagen base de la aplicación.
- FastAPI servido por Uvicorn en el puerto 8000 del contenedor.
- PostgreSQL 17.11 en un contenedor independiente.
- Docker Compose gestiona ambos servicios.
- El puerto de la aplicación se publica en `127.0.0.1`, usando `APP_PORT` o 8000 por defecto.
- La base de datos utiliza el volumen Docker `opsdesk-lab_postgres_data`.
- `.env.example` declara `APP_PORT`, `POSTGRES_DB`, `POSTGRES_USER` y `POSTGRES_PASSWORD`.
- El archivo `.env` local no se ha leído ni incluido en este diagnóstico.

## 3. Aplicación existente

En `app/main.py` están implementados:

- `GET /`: información básica de la aplicación.
- `GET /health`: comprobación de que la aplicación responde.
- `GET /ready`: comprobación de conectividad con PostgreSQL mediante `SELECT 1`.

Las comprobaciones realizadas devolvieron la aplicación y la base de datos como saludables. `/ready` devolvió `status=ready`, `database=connected` y `check=1`.

Todavía no se ha implementado el CRUD de incidencias.

## 4. Estado de PostgreSQL

Resultados observados:

- Base de datos: `opsdesk`.
- Rol de conexión: `opsdesk_app`.
- Versión del servidor: PostgreSQL 17.11.
- Tablas de usuario encontradas: ninguna.
- Columnas de tablas de usuario encontradas: ninguna.
- El volumen `opsdesk-lab_postgres_data` existe.

La ausencia de tablas se limita a lo observado en la consulta realizada; no implica por sí sola pérdida de datos.

## 5. Bloqueo de seguridad

La consulta a `pg_roles` devolvió para `opsdesk_app`:

- `rolsuper = true`
- `rolcreaterole = true`
- `rolcreatedb = true`
- `rolcanlogin = true`

El rol también puede crear objetos en la base de datos actual.

**Bloqueo:** la cuenta utilizada por la aplicación tiene privilegios administrativos excesivos. Antes de desplegar el esquema CRUD, hay que preparar una copia de seguridad verificable, separar la cuenta administrativa de la cuenta de ejecución y comprobar los permisos mínimos de esta última.

No se han modificado privilegios ni tablas durante la auditoría.

## 6. Pruebas y herramientas pendientes

No se encontraron archivos rastreados por Git correspondientes a pruebas, pytest, migraciones, copias de seguridad o restauración.

Trabajo pendiente:

- Añadir pruebas automatizadas de los endpoints.
- Añadir pruebas de integración con PostgreSQL.
- Incorporar Alembic y una migración inicial versionada.
- Probar validación, respuestas HTTP y errores de base de datos.
- Documentar y verificar el procedimiento de copia de seguridad y restauración.
- Verificar la persistencia tras recrear contenedores en una prueba controlada, sin eliminar el volumen.

La ausencia de archivos rastreados no demuestra que no exista ningún archivo local sin seguimiento; no se ha hecho una afirmación más amplia.

## 7. Primer cambio previsto para el CRUD de incidencias

El primer cambio funcional previsto es introducir el esquema de incidencias mediante una migración versionada, seguido de los modelos y endpoints de creación y consulta.

Orden propuesto:

1. Crear y verificar una copia de seguridad.
2. Corregir la separación de roles y aplicar el principio de mínimo privilegio.
3. Añadir Alembic y una migración inicial.
4. Definir los campos, estados, prioridades y reglas de validación de una incidencia.
5. Implementar `POST /incidents` y `GET /incidents`.
6. Añadir pruebas automatizadas para creación, listado, validación y errores.
7. Continuar con consulta individual, actualización y cierre de incidencias.

Los campos definitivos y las reglas de negocio deben quedar definidos antes de generar la migración; no se consideran implementados en esta fase.

## 8. Restricciones de seguridad y conservación

- No leer ni publicar el contenido de `.env`.
- No ejecutar `docker compose down -v`.
- No borrar ni recrear el volumen de PostgreSQL.
- No modificar el esquema ni los permisos antes de preparar y verificar la estrategia de recuperación.
- No afirmar que existe una copia de seguridad verificada hasta haberla generado y comprobado.

## 9. Conclusión

La aplicación y PostgreSQL arrancan y se comunican correctamente, pero la base de datos no contiene tablas de usuario y la cuenta de la aplicación tiene privilegios excesivos. La prioridad previa al CRUD es asegurar la recuperación y corregir los permisos. Después se implementará el esquema mediante migraciones y se cubrirá con pruebas automatizadas.
