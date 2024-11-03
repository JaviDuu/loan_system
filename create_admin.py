# create_admin.py

from loan_system.app import create_app, db
from loan_system.models import Usuario
from werkzeug.security import generate_password_hash
import getpass


def crear_admin():
    """
    Crea un usuario administrador si no existe.
    """
    # Configurar la aplicación y el contexto
    app = create_app()
    with app.app_context():
        # Verificar si ya existe un usuario administrador
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            print("El usuario administrador ya existe.")
            return

        # Solicitar detalles del administrador
        print("Creación de Usuario Administrador:")
        nombre = 'Administrador'
        direccion = 'Dirección del Admin'
        telefono = '1234567890'
        correo = 'admin@prestamos.com'
        username = 'admin'
        # Solicitar la contraseña de forma segura
        while True:
            password = getpass.getpass("Introduce la contraseña para el administrador: ")
            password_confirm = getpass.getpass("Confirma la contraseña: ")
            if password != password_confirm:
                print("Las contraseñas no coinciden. Intenta de nuevo.")
            elif len(password) < 6:
                print("La contraseña debe tener al menos 6 caracteres. Intenta de nuevo.")
            else:
                break

        # Crear un nuevo usuario administrador
        nuevo_admin = Usuario(
            nombre=nombre,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            rol='admin'
        )

        # Añadir y guardar el nuevo administrador en la base de datos
        db.session.add(nuevo_admin)
        db.session.commit()

        print("Usuario administrador creado exitosamente.")


if __name__ == '__main__':
    crear_admin()
