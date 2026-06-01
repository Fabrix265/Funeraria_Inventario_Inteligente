from sqlmodel import Session, select
from passlib.context import CryptContext
from src.models.user import User, Role, Permission, UserRoleLink

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def ejecutar_seeding(db: Session):
    permisos_sistema = [
        {"nombre": "usuarios:crear",   "descripcion": "Crear y editar usuarios y roles"},
        {"nombre": "usuarios:listar",  "descripcion": "Ver la lista de usuarios y roles"},
        {"nombre": "usuarios:eliminar","descripcion": "Eliminar usuarios del sistema"},

        {"nombre": "ataudes:leer",           "descripcion": "Ver el inventario de ataúdes"},
        {"nombre": "ataudes:crear",          "descripcion": "Agregar ataúdes al inventario"},
        {"nombre": "ataudes:actualizar",     "descripcion": "Editar datos de un ataúd"},
        {"nombre": "ataudes:eliminar",       "descripcion": "Eliminar ataúdes del inventario"},
        {"nombre": "ataudes:actualizar_stock","descripcion": "Modificar el stock de un ataúd"},

        {"nombre": "capillas:leer",      "descripcion": "Ver capillas disponibles"},
        {"nombre": "capillas:crear",     "descripcion": "Registrar nuevas capillas"},
        {"nombre": "capillas:actualizar","descripcion": "Editar datos de capillas"},
        {"nombre": "capillas:eliminar",  "descripcion": "Eliminar capillas"},

        {"nombre": "vehiculos:leer",      "descripcion": "Ver vehículos disponibles"},
        {"nombre": "vehiculos:crear",     "descripcion": "Registrar nuevos vehículos"},
        {"nombre": "vehiculos:actualizar","descripcion": "Editar datos de vehículos"},
        {"nombre": "vehiculos:eliminar",  "descripcion": "Eliminar vehículos"},

        {"nombre": "servicios:leer",      "descripcion": "Ver servicios registrados"},
        {"nombre": "servicios:crear",     "descripcion": "Registrar nuevos servicios"},
        {"nombre": "servicios:actualizar","descripcion": "Editar servicios existentes"},
        {"nombre": "servicios:eliminar",  "descripcion": "Eliminar servicios"},

        {"nombre": "contratantes:leer",     "descripcion": "Ver registros de contratantes"},
        {"nombre": "contratantes:crear",     "descripcion": "Crear registros de contratantes"},
        {"nombre": "contratantes:actualizar","descripcion": "Editar registros de contratantes"},
        {"nombre": "contratantes:eliminar",  "descripcion": "Eliminar registros de contratantes"},
    ]

    permisos_db = []
    for p in permisos_sistema:
        existente = db.exec(select(Permission).where(Permission.nombre == p["nombre"])).first()
        if not existente:
            nuevo = Permission(nombre=p["nombre"], descripcion=p["descripcion"])
            db.add(nuevo)
            permisos_db.append(nuevo)
        else:
            permisos_db.append(existente)
    db.commit()
    permisos_db = [db.exec(select(Permission).where(Permission.nombre == p["nombre"])).first() for p in permisos_sistema]

    rol_admin = db.exec(select(Role).where(Role.nombre == "Administrador")).first()
    if not rol_admin:
        rol_admin = Role(nombre="Administrador")
        db.add(rol_admin)
        db.commit()
        db.refresh(rol_admin)
    rol_admin.permisos = permisos_db
    db.commit()
    db.refresh(rol_admin)

    permisos_trabajador_nombres = [
        "ataudes:leer",
        "capillas:leer",
        "vehiculos:leer",
        "servicios:leer",
        "servicios:crear",
        "servicios:actualizar",
        "contratantes:leer",
        "contratantes:crear",
        "contratantes:actualizar",
    ]
    permisos_trabajador = [
        db.exec(select(Permission).where(Permission.nombre == n)).first()
        for n in permisos_trabajador_nombres
    ]

    rol_trabajador = db.exec(select(Role).where(Role.nombre == "Trabajador")).first()
    if not rol_trabajador:
        rol_trabajador = Role(nombre="Trabajador")
        db.add(rol_trabajador)
        db.commit()
        db.refresh(rol_trabajador)
    rol_trabajador.permisos = permisos_trabajador
    db.commit()
    db.refresh(rol_trabajador)

    import os
    admin_username = os.getenv("ADMIN_USER", "fabAdmin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123456")

    if not db.exec(select(User).where(User.username == admin_username)).first():
        nuevo_admin = User(
            username=admin_username,
            password=pwd_context.hash(admin_password)
        )
        nuevo_admin.roles.append(rol_admin)
        db.add(nuevo_admin)
        db.commit()
        print(f" SEEDING: Usuario '{admin_username}' creado con rol Administrador.")
    else:
        print(f" SEEDING: Usuario '{admin_username}' ya existe. Sin cambios.")