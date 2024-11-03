# loan_system/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired(), Length(min=2, max=150)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(min=5, max=200)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(min=7, max=20)])
    correo = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class PrestamoForm(FlaskForm):
    monto = FloatField('Monto a Prestar', validators=[DataRequired(), NumberRange(min=1)])
    meses = IntegerField('Plazo (meses)', validators=[DataRequired(), NumberRange(min=1)])
    interes = FloatField('Porcentaje de Interés (%)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Solicitar Préstamo')
