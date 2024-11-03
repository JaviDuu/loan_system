# loan_system/app.py

import os  # Importar os para manejar rutas
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .models import db, Usuario, Prestamo, Amortizacion
from .forms import RegistrationForm, LoginForm, PrestamoForm
from .amortizacion.generar_amortizacion import generar_tabla_amortizacion
from flask_migrate import Migrate  # Importar Flask-Migrate


def admin_required(f):
    """
    Decorador para restringir el acceso a rutas solo a usuarios con rol 'admin'.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            abort(403)  # Error 403 Forbidden
        return f(*args, **kwargs)

    return decorated_function


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_secreto_aqui'  # Reemplaza con una clave secreta segura

    # Definir la ruta absoluta para la base de datos en la raíz del proyecto
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # Subir un nivel desde app.py
    db_path = os.path.join(basedir, 'loan_system.db')  # Colocar en la raíz del proyecto
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)  # Configurar Flask-Migrate

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Redirige a 'login' si no está autenticado

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Manejo de errores personalizados
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    # Rutas y lógica
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        Ruta para que los usuarios se registren como clientes.
        """
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            nuevo_usuario = Usuario(
                nombre=form.nombre.data,
                direccion=form.direccion.data,
                telefono=form.telefono.data,
                correo=form.correo.data,
                username=form.username.data,
                password=hashed_password,
                rol='cliente'  # Asegurar que el rol es 'cliente'
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Ruta para que los usuarios inicien sesión.
        """
        form = LoginForm()
        if form.validate_on_submit():
            usuario = Usuario.query.filter_by(username=form.username.data).first()
            if usuario and check_password_hash(usuario.password, form.password.data):
                login_user(usuario)
                flash('Inicio de sesión exitoso.', 'success')
                if usuario.rol == 'admin':
                    # Si es admin, redirigir a 'all_prestamos'
                    return redirect(url_for('all_prestamos'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """
        Ruta del dashboard donde los clientes pueden ver sus préstamos y realizar nuevas solicitudes.
        Los administradores no tienen acceso a esta ruta.
        """
        if current_user.rol == 'admin':
            abort(403)  # Administradores no acceden al dashboard

        # Cliente: mostrar sus propios préstamos
        prestamos = Prestamo.query.filter_by(usuario_id=current_user.id).all()
        return render_template('dashboard.html', prestamos=prestamos)

    @app.route('/solicitar_prestamo', methods=['GET', 'POST'])
    @login_required
    def solicitar_prestamo():
        """
        Ruta para que los usuarios soliciten un nuevo préstamo.
        Los administradores no pueden solicitar préstamos.
        """
        if current_user.rol == 'admin':
            flash('Los administradores no pueden solicitar préstamos.', 'warning')
            return redirect(url_for('all_prestamos'))  # Redirigir a 'all_prestamos' o a otra página apropiada

        form = PrestamoForm()
        if form.validate_on_submit():
            monto = form.monto.data
            meses = form.meses.data
            interes = form.interes.data
            total = monto + (monto * interes / 100)
            nuevo_prestamo = Prestamo(
                monto=monto,
                meses=meses,
                interes=interes,
                total=total,
                usuario_id=current_user.id,
                estado='pendiente'  # Establecer el estado como 'pendiente'
            )
            db.session.add(nuevo_prestamo)
            db.session.commit()

            flash('Préstamo solicitado exitosamente y está pendiente de aprobación.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('solicitar_prestamo.html', form=form)

    @app.route('/historial')
    @login_required
    def historial():
        """
        Ruta para que los usuarios vean su historial de préstamos con las tablas de amortización.
        """
        if current_user.rol == 'admin':
            abort(403)  # Administradores no acceden al historial

        prestamos = Prestamo.query.filter_by(usuario_id=current_user.id).all()
        return render_template('historial.html', prestamos=prestamos)

    @app.route('/logout')
    @login_required
    def logout():
        """
        Ruta para que los usuarios cierren sesión.
        """
        logout_user()
        flash('Has cerrado sesión.', 'info')
        return redirect(url_for('index'))

    # Nueva Ruta para Administradores: Ver Todos los Préstamos
    @app.route('/all_prestamos')
    @login_required
    @admin_required
    def all_prestamos():
        """
        Ruta para que los administradores vean todos los préstamos de todos los usuarios,
        incluyendo el nombre del usuario al que pertenece cada préstamo.
        """
        # Consulta para obtener todos los préstamos junto con el nombre del usuario
        prestamos = Prestamo.query.join(Usuario).add_columns(
            Prestamo.id,
            Prestamo.monto,
            Prestamo.meses,
            Prestamo.interes,
            Prestamo.total,
            Prestamo.estado,
            Usuario.nombre.label('nombre_usuario')
        ).all()

        return render_template('all_prestamos.html', prestamos=prestamos)

    @app.route('/aprobar_prestamo/<int:prestamo_id>', methods=['POST'])
    @login_required
    @admin_required
    def aprobar_prestamo(prestamo_id):
        """
        Ruta para que el administrador apruebe una solicitud de préstamo.
        """
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        if prestamo.estado != 'pendiente':
            flash('Esta solicitud ya ha sido procesada.', 'warning')
            return redirect(url_for('all_prestamos'))

        # Actualizar el estado a 'aprobado'
        prestamo.estado = 'aprobado'
        db.session.commit()

        # Generar tabla de amortización
        tabla = generar_tabla_amortizacion(prestamo.monto, prestamo.meses, prestamo.interes)
        for fila in tabla:
            amortizacion = Amortizacion(
                periodo=fila['Periodo'],
                cuota=fila['Cuota'],
                interes=fila['Interés'],
                capital=fila['Capital'],
                saldo=fila['Saldo'],
                prestamo_id=prestamo.id
            )
            db.session.add(amortizacion)
        db.session.commit()

        flash(f'Préstamo ID {prestamo.id} aprobado exitosamente.', 'success')
        return redirect(url_for('all_prestamos'))

    @app.route('/rechazar_prestamo/<int:prestamo_id>', methods=['POST'])
    @login_required
    @admin_required
    def rechazar_prestamo(prestamo_id):
        """
        Ruta para que el administrador rechace una solicitud de préstamo.
        """
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        if prestamo.estado != 'pendiente':
            flash('Esta solicitud ya ha sido procesada.', 'warning')
            return redirect(url_for('all_prestamos'))

        # Actualizar el estado a 'rechazado'
        prestamo.estado = 'rechazado'
        db.session.commit()

        flash(f'Préstamo ID {prestamo.id} rechazado.', 'danger')
        return redirect(url_for('all_prestamos'))

    # Añadir un contexto de shell para facilitar el acceso a modelos
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Usuario': Usuario,
            'Prestamo': Prestamo,
            'Amortizacion': Amortizacion
        }

    # Crear todas las tablas dentro del contexto de la aplicación
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas creadas exitosamente.")
        print("Base de datos creada en:", db_path)  # Imprimir la ruta absoluta

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)