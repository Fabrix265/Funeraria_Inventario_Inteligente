# ER and Class Diagram Analysis Report
Funeraria Aranzabal - Funeraria_Inventario_Inteligente
Date: 2026-10-17

## 1. Overall Project Structure


**Language/Framework:** Python 3.11, FastAPI, SQLModel/SQLAlchemy, PostgreSQL (psycopg2).


**Root structure:**
- src/ (API, routers, services, schemas, models, core, deps, utils, config, templates, static)
- tests/ (unit + integration)
- notebooks/ (extraction + prediction notebooks + models)
- data/, models_weights/, results/, venv/


**Entry point:** src/main.py


## 2. Entities/Models (Database Tables via SQLModel)


### User, Role, Permission (Authorization)


**File:** src/models/user.py


#### Permission (table: permission)
- id (int, PK, Optional)
- nombre (str, NOT NULL, unique, index)
- descripcion (str, NULL, default None)
- Relationships: roles -> M2M via RolePermissionLink


#### Role (table: role)
- id (int, PK, Optional)
- nombre (str, NOT NULL, unique, index)
- Relationships: usuarios (M2M via UserRoleLink), permisos (M2M via RolePermissionLink)


#### User (table: user)
- id (int, PK, Optional)
- username (str, NOT NULL, unique, index, max_length=30)
- email (str, NOT NULL, unique, index, max_length=255)
- password (str, NOT NULL)
- activo (bool, default True, index)
- token_version (int, default 0)
- Relationships: roles (M2M via UserRoleLink), servicios (1:N to Servicio, FK id_usuario)


#### Join Tables
- UserRoleLink: user_id (int, PK, FK->user.id), role_id (int, PK, FK->role.id)
- RolePermissionLink: role_id (int, PK, FK->role.id), permission_id (int, PK, FK->permission.id)


### Ataud (table: ataud)
**File:** src/models/ataud.py
- id (int, PK, Optional)
- modelo (str, NOT NULL, max_length=100, index)
- color (str, NOT NULL, max_length=50)
- stock (int, NOT NULL, default 0, ge=0)
- activo (bool, default True, index)
- 1:N: servicios (Ataud.servicios -> Servicio.ataud)
- 1:N: imagenes (AtaudImagen.ataud_id FK->ataud.id, cascade all delete-orphan)


### AtaudImagen (table: ataudimagen)
- id (int, PK, Optional)
- ataud_id (int, NOT NULL, FK->ataud.id)
- url (str, NOT NULL)
- storage_path (str, NOT NULL)
- N:1 to Ataud


### Capilla (table: capilla)
**File:** src/models/capilla.py
- id (int, PK, Optional)
- modelo (str, NOT NULL, max_length=100, index)
- stock (int, NOT NULL, default 0)
- activo (bool, default True, index)
- 1:N: servicios, 1:N: imagenes (cascade all delete-orphan)


### CapillaImagen (table: capillaimagen)
- id (int, PK, Optional)
- capilla_id (int, NOT NULL, FK->capilla.id)
- url (str, NOT NULL)
- public_id (str, NOT NULL)


### Vehiculo (table: vehiculo)
**File:** src/models/vehiculo.py
- id (int, PK, Optional)
- tipo (TipoVehiculo enum, NOT NULL, index) values: porta_ataud, porta_flores, mixto, auto, microbus
- activo (bool, default True, index)
- 1:N: servicios (via ServicioVehiculo.vehiculo), 1:N: imagenes (cascade)


### VehiculoImagen (table: vehiculoimagen)
- id (int, PK, Optional)
- vehiculo_id (int, NOT NULL, FK->vehiculo.id)
- url (str, NOT NULL)
- storage_path (str, NOT NULL)


### Fallecido (table: fallecido)
**File:** src/models/fallecido.py
- id (int, PK, Optional)
- nombre (str, NOT NULL, max_length=100)
- dni_fallecido (str, NOT NULL, max_length=8, index)
- activo (bool, default True, index)
- 1:1: servicio (Servicio.fallecido_id unique; Servicio.id_fallecido FK with unique)


### Contratante (table: contratante)
**File:** src/models/contratante.py
- id (int, PK, Optional)
- nombre (str, NOT NULL, max_length=100)
- dni (str, NOT NULL, max_length=8, unique, index)
- telefono (str, NOT NULL, max_length=9)
- activo (bool, default True, index)
- 1:N: servicios


### Servicio (table: servicio)
**File:** src/models/servicio.py
- id (int, PK, Optional)
- id_usuario (int, NOT NULL, FK->user.id)
- id_ataud (int, NULL, FK->ataud.id)
- id_capilla (int, NOT NULL, FK->capilla.id)
- id_contratante (int, NOT NULL, FK->contratante.id)
- id_fallecido (int, NOT NULL, FK->fallecido.id, unique)
- direccion_velacion (str, NOT NULL, max_length=200)
- tipo_pago (TipoPago enum, NOT NULL, index) values: directo, seguro, mixto
- costo (Decimal, default 0.0, decimal_places=2)
- fecha (date, NOT NULL, index)
- cantidad_cargadores (int, NULL)
- Relationships: usuario (N:1), ataud (N:1, optional), capilla (N:1), contratante (N:1), fallecido (1:1 via unique FK), vehiculos_asignados (1:N to ServicioVehiculo), archivos (1:N to ServicioArchivo)


### ServicioVehiculo (table: servicio_vehiculo)
**File:** src/models/servicio_vehiculo.py
- id (int, PK, Optional)
- id_servicio (int, NOT NULL, FK->servicio.id)
- id_vehiculo (int, NOT NULL, FK->vehiculo.id)
- Relationships: servicio (N:1), vehiculo (N:1) - M2M between Servicio and Vehiculo


### ServicioArchivo (table: servicio_archivo)
**File:** src/models/servicio_archivo.py
- id (int, PK, Optional)
- id_servicio (int, NOT NULL, FK->servicio.id, index)
- tipo (TipoArchivo enum, NOT NULL): certificado, acta, dni_contratante, dni_fallecido
- nombre_original (str, NOT NULL, max_length=255)
- drive_file_id (str, NOT NULL, max_length=255)
- drive_file_url (str, NOT NULL, max_length=500)
- mime_type (str, NOT NULL, max_length=100)
- subido_por (int, NULL, FK->user.id)
- created_at (datetime, default factory datetime.utcnow)
- updated_at (datetime, default factory datetime.utcnow)
- Relationships: servicio (N:1), usuario (N:1, optional)


### Bitacora (table: bitacora)
**File:** src/models/bitacora.py
- id (int, PK, Optional)
- usuario_id (int, NULL, FK->user.id)
- usuario_nombre (str, NOT NULL)
- accion (str, NOT NULL)
- modulo (str, NOT NULL)
- detalle (str, NULL)
- ip_address (str, NULL)
- created_at (datetime, default datetime.utcnow)


### PasswordResetToken (table: password_reset_token)
**File:** src/models/password_reset_token.py
- id (int, PK, Optional)
- user_id (int, NOT NULL, FK->user.id, index)
- token_hash (str, NOT NULL, unique, index)
- expira_en (datetime, NOT NULL)
- usado_en (datetime, NULL)
- created_at (datetime, default datetime.utcnow)


### OAuthToken (table: oauthtoken)
**File:** src/models/oauth_token.py
- id (int, PK, Optional)
- proveedor (str, default 'google_drive')
- access_token (str, NOT NULL)
- refresh_token (str, NOT NULL)
- token_expiry (datetime, NULL)
- usuario_id (int, NULL, FK->user.id)


### EmailChangeRequest (table: email_change_request)
**File:** src/models/email_change_request.py
- id (int, PK, Optional)
- user_id (int, NOT NULL, FK->user.id, index)
- email_anterior (str, NOT NULL, max_length=255)
- email_nuevo (str, NOT NULL, max_length=255)
- codigo_hash (str, NOT NULL, index)
- expira_en (datetime, NOT NULL)
- intentos (int, default 0)
- usado_en (datetime, NULL)
- created_at (datetime, default datetime.utcnow)


### Respaldo, RespaldoConfig, TokenRestauracion (Backup system)
**File:** src/models/respaldo.py


#### Respaldo (table: respaldo)
- id (int, PK, Optional)
- etiqueta (str, NOT NULL, max_length=255)
- fecha (datetime, default utcnow, index)
- nombre_archivo (str, NOT NULL, max_length=255)
- drive_file_id (str, NOT NULL, max_length=255)
- drive_manifesto_id (str, NULL, max_length=255)
- drive_folder_archivos_id (str, NULL, max_length=255)
- tamano_bytes (int, default 0)
- cantidad_archivos (int, default 0)
- sha256 (str, NULL, max_length=64)
- estado (str, default 'en_proceso', max_length=20, index) values in code: en_proceso, completado, fallido
- mensaje_error (str, NULL)
- tipo (str, default 'manual', max_length=20) values: manual, seguridad
- observacion (str, NULL, max_length=255)
- usuario_id (int, NULL)
- usuario_nombre (str, NULL, max_length=50)
- created_at (datetime, default utcnow)
- updated_at (datetime, default utcnow)


#### RespaldoConfig (table: respaldo_config)
- id (int, PK, Optional)
- frecuencia_dias (int, default 1, ge=1, le=90)
- dias_advertencia (int, default 2, ge=1, le=90)
- maximo_respaldos (int, default 15, ge=2, le=200)
- updated_at (datetime, default utcnow)


#### TokenRestauracion (table: token_restauracion)
- id (int, PK, Optional)
- respaldo_id (int, NOT NULL, FK->respaldo.id, index)
- usuario_id (int, NULL)
- token_hash (str, NOT NULL, max_length=64, unique, index)
- expira_en (datetime, NOT NULL, index)
- intentos (int, default 0)
- usado_en (datetime, NULL)
- created_at (datetime, default utcnow)


## 3. Enums/Notable Types
- TipoPago (str Enum): directo, seguro, mixto (src/models/servicio.py)
- TipoVehiculo (str Enum): porta_ataud, porta_flores, mixto, auto, microbus (src/models/vehiculo.py)
- TipoArchivo (str Enum): certificado, acta, dni_contratante, dni_fallecido (src/models/servicio_archivo.py)
- Backup constants: ESTADOS_RESPALDO=('en_proceso','completado','fallido'), TIPOS_RESPALDO=('manual','seguridad') (src/models/respaldo.py)


## 4. Complete Field Summary (All Entities)
See detailed entity sections above.


## 5. File Paths for All Entities/Classes


**Models (SQLModel ORM):**
- src/models/user.py (User, Role, Permission, UserRoleLink, RolePermissionLink)
- src/models/ataud.py (Ataud, AtaudImagen)
- src/models/capilla.py (Capilla, CapillaImagen)
- src/models/vehiculo.py (Vehiculo, VehiculoImagen)
- src/models/fallecido.py (Fallecido)
- src/models/contratante.py (Contratante)
- src/models/servicio.py (Servicio, TipoPago)
- src/models/servicio_vehiculo.py (ServicioVehiculo)
- src/models/servicio_archivo.py (ServicioArchivo, TipoArchivo)
- src/models/bitacora.py (Bitacora)
- src/models/password_reset_token.py (PasswordResetToken)
- src/models/oauth_token.py (OAuthToken)
- src/models/email_change_request.py (EmailChangeRequest)
- src/models/respaldo.py (Respaldo, RespaldoConfig, TokenRestauracion)
- src/models/__init__.py


**Pydantic Schemas:**
- src/schemas/user.py, auth.py, ataud.py, capilla.py, vehiculo.py, fallecido.py, contratante.py, servicio.py, servicio_archivo.py, bitacora.py, respaldo.py, drive.py, estado.py, stock.py, __init__.py


**Services (OOP Classes/Functions):**
- src/services/user_service.py, auth_service.py, ataud_service.py, capilla_service.py, vehiculo_service.py, fallecido_service.py, contratante_service.py, servicio_service.py, archivo_service.py, bitacora_service.py, role_service.py, respaldo_service.py, drive_service.py, email_service.py, email_change_service.py, reniec_service.py, pg_service.py, backup_jobs.py, __init__.py


**Routers:**
- src/routers/*.py (user_router, auth_router, ataud_router, capilla_router, vehiculo_router, fallecido_router, contratante_router, servicio_router, archivo_router, bitacora_router, role_router, respaldo_router, drive_router, reniec_router, __init__.py)


**Core/Config/Deps/Utils:**
- src/config/db.py, src/core/security.py, crypto.py, schema_bootstrap.py, lifespan.py, seed.py, fechas.py, cloudinary_config.py, supabase_config.py, src/deps/db_session.py, role_check.py, pagination.py, limiter.py, servicio_filters.py, src/utils/http_error_handler.py


## 6. ER Relationships (Summary for Mermaid)
- User 1:N Servicio (FK id_usuario)
- Ataud 1:N Servicio (FK id_ataud, nullable)
- Capilla 1:N Servicio (FK id_capilla)
- Contratante 1:N Servicio (FK id_contratante)
- Fallecido 1:1 Servicio (FK id_fallecido unique)
- Servicio M2M Vehiculo via ServicioVehiculo (composite FK pair)
- Servicio 1:N ServicioArchivo (FK id_servicio)
- Servicio 1:N ServicioVehiculo (FK id_servicio)
- Ataud 1:N AtaudImagen (FK ataud_id, cascade)
- Capilla 1:N CapillaImagen (FK capilla_id, cascade)
- Vehiculo 1:N VehiculoImagen (FK vehiculo_id, cascade)
- User M2M Role via UserRoleLink
- Role M2M Permission via RolePermissionLink
- User 1:N PasswordResetToken, EmailChangeRequest (optional)
- ServicioArchivo N:1 User (subido_por)
- Respaldo 1:N TokenRestauracion (FK respaldo_id)

