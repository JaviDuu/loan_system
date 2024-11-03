# loan_system/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='cliente')

    # Relación con Prestamo
    prestamos = db.relationship('Prestamo', backref='usuario', lazy=True)


class Prestamo(db.Model):
    __tablename__ = 'prestamos'

    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    meses = db.Column(db.Integer, nullable=False)
    interes = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # Nuevo campo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relación con Amortizacion
    amortizaciones = db.relationship('Amortizacion', backref='prestamo', lazy=True)


class Amortizacion(db.Model):
    __tablename__ = 'amortizaciones'

    id = db.Column(db.Integer, primary_key=True)
    periodo = db.Column(db.Integer, nullable=False)
    cuota = db.Column(db.Float, nullable=False)
    interes = db.Column(db.Float, nullable=False)
    capital = db.Column(db.Float, nullable=False)
    saldo = db.Column(db.Float, nullable=False)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.id'), nullable=False)
