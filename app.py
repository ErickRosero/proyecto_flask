from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, RadioField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
import csv
from datetime import datetime, timedelta
from Conexion.conexion import get_connection, test_connection
import mysql.connector
from mysql.connector import Error
from models import User
import secrets

# Obtener la ruta absoluta del directorio actual
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Crear directorios si no existen
os.makedirs(os.path.join(BASE_DIR, 'datos'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Genera una clave aleatoria para seguridad
app.config['JWT_SECRET'] = secrets.token_hex(32)  # Para generar tokens de sesión

# Configurar la base de datos SQLite para el modelo Contacto
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database", "contactos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Definir el modelo para la base de datos SQLite
class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'asunto': self.asunto,
            'mensaje': self.mensaje,
            'categoria': self.categoria,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None
        }

# Crear la base de datos y tablas SQLite
with app.app_context():
    try:
        db.create_all()
        print(f"Base de datos SQLite creada en: {os.path.join(BASE_DIR, 'database', 'contactos.db')}")
    except Exception as e:
        print(f"Error al crear la base de datos SQLite: {e}")

# Función para cargar usuario en Flask-Login
@login_manager.user_loader
def load_user(user_id):
    connection = get_connection()
    if connection:
        user = User.get_by_id(connection, user_id)
        connection.close()
        return user
    return None

# Definición del formulario de contacto usando WTForms
class ContactoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    asunto = StringField('Asunto', validators=[DataRequired()])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10)])
    categoria = SelectField('Categoría', choices=[
        ('consulta', 'Consulta'),
        ('sugerencia', 'Sugerencia'),
        ('problema', 'Problema')
    ])
    
    # Campos para seleccionar formatos de almacenamiento
    formato_almacenamiento = RadioField(
        'Formato principal de almacenamiento', 
        choices=[
            ('todos', 'Guardar en todos los formatos'),
            ('txt', 'Solo TXT'),
            ('json', 'Solo JSON'),
            ('csv', 'Solo CSV'),
            ('sqlite', 'Solo SQLite'),
            ('mysql', 'MySQL')
        ],
        default='todos'
    )
    
    # Campos adicionales para formatos secundarios
    guardar_txt = BooleanField('Guardar en TXT', default=False)
    guardar_json = BooleanField('Guardar en JSON', default=False)
    guardar_csv = BooleanField('Guardar en CSV', default=False)
    guardar_sqlite = BooleanField('Guardar en SQLite', default=False)
    guardar_mysql = BooleanField('Guardar en MySQL', default=False)
    
    submit = SubmitField('Enviar')

# Formulario de registro
class RegistroForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres.')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir.')
    ])
    submit = SubmitField('Registrarse')

# Formulario de inicio de sesión
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

@app.route('/')
@login_required  # Proteger vista de usuario

def inicio():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/<nombre>')
@login_required  # Proteger vista de usuario
def usuario(nombre):
    return render_template('usuario.html', title='Perfil', nombre=nombre)

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/formulario', methods=['GET', 'POST'])
@login_required  # Proteger formulario
def formulario():
    form = ContactoForm()
    
    # Validación del formulario cuando se envía con método POST
    if form.validate_on_submit():
        # Procesar los datos del formulario
        datos = {
            'nombre': form.nombre.data,
            'email': form.email.data,
            'asunto': form.asunto.data,
            'mensaje': form.mensaje.data,
            'categoria': form.categoria.data,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Determinar los formatos para guardar
        formato_principal = form.formato_almacenamiento.data
        
        if formato_principal == 'todos':
            # Guardar en todos los formatos
            guardar_en_txt(datos)
            guardar_en_json(datos)
            guardar_en_csv(datos)
            guardar_en_sqlite(datos)
            guardar_en_mysql(datos)
            
            flash('¡Formulario enviado y guardado en todos los formatos!', 'success')
        else:
            # Guardar en el formato principal
            if formato_principal == 'txt':
                guardar_en_txt(datos)
            elif formato_principal == 'json':
                guardar_en_json(datos)
            elif formato_principal == 'csv':
                guardar_en_csv(datos)
            elif formato_principal == 'sqlite':
                guardar_en_sqlite(datos)
            elif formato_principal == 'mysql':
                guardar_en_mysql(datos)
            
            # Comprobar formatos secundarios
            if formato_principal != 'txt' and form.guardar_txt.data:
                guardar_en_txt(datos)
            if formato_principal != 'json' and form.guardar_json.data:
                guardar_en_json(datos)
            if formato_principal != 'csv' and form.guardar_csv.data:
                guardar_en_csv(datos)
            if formato_principal != 'sqlite' and form.guardar_sqlite.data:
                guardar_en_sqlite(datos)
            if formato_principal != 'mysql' and form.guardar_mysql.data:
                guardar_en_mysql(datos)
            
            flash('¡Formulario enviado y guardado en los formatos seleccionados!', 'success')
        
        # Redireccionar a la página de resultados con los datos
        return render_template('resultado.html', title='Resultado', datos=datos,
                              formato_guardado=formato_principal, form=form)
    
    # Si es GET o si el formulario no es válido, mostrar la página del formulario
    return render_template('formulario.html', title='Formulario', form=form)

# Rutas para el sistema de autenticación
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        connection = get_connection()
        if not connection:
            flash('Error de conexión a la base de datos', 'danger')
            return render_template('registro.html', title='Registro', form=form)
        
        # Verificar si el correo ya está registrado
        existing_user = User.get_by_email(connection, form.email.data)
        if existing_user:
            connection.close()
            flash('El email ya está registrado. Por favor utilice otro.', 'warning')
            return render_template('registro.html', title='Registro', form=form)
        
        # Crear nuevo usuario
        user, error = User.create_user(
            connection,
            form.nombre.data,
            form.email.data,
            form.password.data
        )
        
        connection.close()
        
        if user:
            flash('¡Registro exitoso! Ahora puede iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Error al registrar usuario: {error}', 'danger')
    
    return render_template('registro.html', title='Registro', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        connection = get_connection()
        if not connection:
            flash('Error de conexión a la base de datos', 'danger')
            return render_template('login.html', title='Iniciar Sesión', form=form)
        
        # Buscar usuario por email
        user = User.get_by_email(connection, form.email.data)
        
        if user and user.check_password(form.password.data):
            # Iniciar sesión
            login_user(user, remember=form.remember.data)
            connection.close()
            
            # Redirigir a la página solicitada originalmente o al inicio
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('inicio'))
        else:
            connection.close()
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html', title='Iniciar Sesión', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('inicio'))

# Vistas protegidas para acceder a los datos
@app.route('/ver_txt')
@login_required
def ver_txt():
    archivo_txt = os.path.join(BASE_DIR, 'datos', 'datos.txt')
    contenido = "No hay datos almacenados en TXT."
    
    if os.path.exists(archivo_txt):
        with open(archivo_txt, 'r', encoding='utf-8') as file:
            contenido = file.read()
    
    return render_template('resultado.html', title='Datos TXT', 
                          vista_datos=True, 
                          tipo_datos='txt',
                          contenido_txt=contenido)

@app.route('/ver_json')
@login_required
def ver_json():
    archivo_json = os.path.join(BASE_DIR, 'datos', 'datos.json')
    datos = []
    
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r', encoding='utf-8') as file:
            try:
                datos = json.load(file)
            except json.JSONDecodeError:
                flash('Error al leer el archivo JSON', 'danger')
    
    return render_template('resultado.html', title='Datos JSON', 
                          vista_datos=True, 
                          tipo_datos='json',
                          datos_json=datos)

@app.route('/ver_csv')
@login_required
def ver_csv():
    archivo_csv = os.path.join(BASE_DIR, 'datos', 'datos.csv')
    datos = []
    
    if os.path.exists(archivo_csv):
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Leer líneas ignorando la primera si es un encabezado
                lines = file.readlines()
                
                # Verificar si la primera línea es un encabezado
                start_line = 1 if (lines and 'nombre' in lines[0].lower()) else 0
                
                # Procesar cada línea de datos
                for line in lines[start_line:]:
                    if line.strip():  # Ignorar líneas vacías
                        # Inicialmente dividir la línea en 6 partes 
                        # (nombre, email, asunto, mensaje, categoria, fecha)
                        parts = []
                        current_part = ""
                        in_quotes = False
                        
                        # Manejar el caso simple especificado en el ejemplo
                        segments = line.strip().split(',')
                        if len(segments) >= 6:
                            dato = {
                                'nombre': segments[0].replace('&#44;', ','),
                                'email': segments[1].replace('&#44;', ','),
                                'asunto': segments[2].replace('&#44;', ','),
                                'mensaje': segments[3].replace('&#44;', ','),
                                'categoria': segments[4].replace('&#44;', ','),
                                'fecha': segments[5].replace('&#44;', ',')
                            }
                            datos.append(dato)
                        else:
                            print(f"Línea con formato incorrecto: {line.strip()}")
            
            print(f"Se han leído {len(datos)} registros del archivo CSV")
        except Exception as e:
            flash(f'Error al leer el archivo CSV: {e}', 'danger')
            print(f"Error detallado: {e}")
            import traceback
            print(traceback.format_exc())
    else:
        print(f"El archivo CSV no existe en: {archivo_csv}")
    
    return render_template('resultado.html', title='Datos CSV', 
                          vista_datos=True, 
                          tipo_datos='csv',
                          datos_csv=datos)

@app.route('/ver_sqlite')
@login_required
def ver_sqlite():
    try:
        contactos = Contacto.query.all()
        return render_template('resultado.html', title='Datos SQLite', 
                            vista_datos=True, 
                            tipo_datos='sqlite',
                            contactos_sqlite=contactos)
    except Exception as e:
        flash(f'Error al acceder a la base de datos: {e}', 'danger')
        return render_template('resultado.html', title='Datos SQLite', 
                            vista_datos=True, 
                            tipo_datos='sqlite',
                            contactos_sqlite=[])

@app.route('/ver_mysql')
@login_required
def ver_mysql():
    connection = get_connection()
    if connection is None:
        flash("No se pudo conectar a MySQL", "danger")
        return render_template('resultado.html', title='Datos MySQL', 
                            vista_datos=True, 
                            tipo_datos='mysql',
                            usuarios_mysql=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        
        return render_template('resultado.html', title='Datos MySQL', 
                            vista_datos=True, 
                            tipo_datos='mysql',
                            usuarios_mysql=usuarios)
    except Error as e:
        flash(f"Error al leer datos de MySQL: {e}", "danger")
        return render_template('resultado.html', title='Datos MySQL', 
                            vista_datos=True, 
                            tipo_datos='mysql',
                            usuarios_mysql=[])
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API para la autenticación (para uso con React)
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    # Verificar que se proporcionaron email y password
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Datos incompletos'}), 400
    
    connection = get_connection()
    if not connection:
        return jsonify({'message': 'Error de conexión a la base de datos'}), 500
    
    # Buscar usuario por email
    user = User.get_by_email(connection, data.get('email'))
    
    if user and user.check_password(data.get('password')):
        # Generar token JWT válido por 1 hora
        expiration = datetime.utcnow() + timedelta(hours=1)
        
        # Crear payload del token con información del usuario
        payload = {
            'user_id': user.id,
            'email': user.email,
            'nombre': user.nombre,
            'exp': expiration
        }
        
        # Generar token con la clave secreta de la aplicación
        import jwt
        token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
        
        connection.close()
        
        # Retornar token y datos básicos del usuario
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'nombre': user.nombre,
                'email': user.email
            },
            'message': 'Inicio de sesión exitoso'
        })
    
    connection.close()
    return jsonify({'message': 'Email o contraseña incorrectos'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    # Verificar que se proporcionaron todos los datos necesarios
    if not data or not data.get('nombre') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Datos incompletos'}), 400
    
    connection = get_connection()
    if not connection:
        return jsonify({'message': 'Error de conexión a la base de datos'}), 500
    
    # Verificar que el email no esté ya registrado
    existing_user = User.get_by_email(connection, data.get('email'))
    if existing_user:
        connection.close()
        return jsonify({'message': 'El email ya está registrado'}), 409
    
    # Crear nuevo usuario
    user, error = User.create_user(
        connection,
        data.get('nombre'),
        data.get('email'),
        data.get('password')
    )
    
    connection.close()
    
    if user:
        return jsonify({
            'message': 'Usuario registrado con éxito',
            'user': {
                'id': user.id,
                'nombre': user.nombre,
                'email': user.email
            }
        }), 201
    else:
        return jsonify({'message': f'Error al registrar usuario: {error}'}), 500

# API endpoints para acceso a datos (protegidos mediante token JWT)
@app.route('/api/datos/json')
@login_required
def api_datos_json():
    archivo_json = os.path.join(BASE_DIR, 'datos', 'datos.json')
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r', encoding='utf-8') as file:
            try:
                datos = json.load(file)
                return jsonify(datos)
            except json.JSONDecodeError:
                return jsonify({"error": "Error al leer el archivo JSON"}), 500
    else:
        return jsonify([])

@app.route('/api/datos/csv')
@login_required
def api_datos_csv():
    archivo_csv = os.path.join(BASE_DIR, 'datos', 'datos.csv')
    datos = []
    
    if os.path.exists(archivo_csv):
        with open(archivo_csv, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            # Ignorar la primera línea si es encabezado
            start_line = 1 if (lines and 'nombre' in lines[0].lower()) else 0
            
            for line in lines[start_line:]:
                if line.strip():
                    segments = line.strip().split(',')
                    if len(segments) >= 6:
                        dato = {
                            'nombre': segments[0].replace('&#44;', ','),
                            'email': segments[1].replace('&#44;', ','),
                            'asunto': segments[2].replace('&#44;', ','),
                            'mensaje': segments[3].replace('&#44;', ','),
                            'categoria': segments[4].replace('&#44;', ','),
                            'fecha': segments[5].replace('&#44;', ',')
                        }
                        datos.append(dato)
    
    return jsonify(datos)

@app.route('/api/datos/sqlite')
@login_required
def api_datos_sqlite():
    try:
        contactos = Contacto.query.all()
        return jsonify([contacto.to_dict() for contacto in contactos])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/datos/mysql')
@login_required
def api_datos_mysql():
    connection = get_connection()
    if connection is None:
        return jsonify({"error": "No se pudo conectar a MySQL"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        
        # Convertir los resultados a formato JSON serializable
        serializable_users = []
        for user in usuarios:
            # Convertir datetime a string si es necesario
            serialized_user = {k: (v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else v) 
                              for k, v in user.items()}
            serializable_users.append(serialized_user)
        
        return jsonify(serializable_users)
    except Error as e:
        return jsonify({"error": f"Error al leer datos de MySQL: {e}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Funciones para persistencia con archivos TXT
def guardar_en_txt(datos):
    archivo_txt = os.path.join(BASE_DIR, 'datos', 'datos.txt')
    with open(archivo_txt, 'a', encoding='utf-8') as file:
        file.write(f"\n--- Nuevo registro: {datos['fecha']} ---\n")
        for key, value in datos.items():
            file.write(f"{key}: {value}\n")
        file.write("--------------------------------\n")

# Funciones para persistencia con archivos JSON
def guardar_en_json(datos):
    archivo_json = os.path.join(BASE_DIR, 'datos', 'datos.json')
    all_data = []
    
    # Comprobar si existe el archivo
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r', encoding='utf-8') as file:
            try:
                all_data = json.load(file)
            except json.JSONDecodeError:
                all_data = []
    
    # Añadir los nuevos datos
    all_data.append(datos)
    
    # Guardar todos los datos en el archivo
    with open(archivo_json, 'w', encoding='utf-8') as file:
        json.dump(all_data, file, indent=4, ensure_ascii=False)

# Funciones para persistencia con archivos CSV
def guardar_en_csv(datos):
    archivo_csv = os.path.join(BASE_DIR, 'datos', 'datos.csv')
    is_new_file = not os.path.exists(archivo_csv) or os.path.getsize(archivo_csv) == 0
    
    # Escapar comas en los datos para evitar problemas de formato
    datos_escaped = {
        'nombre': datos['nombre'].replace(',', '&#44;'),
        'email': datos['email'].replace(',', '&#44;'),
        'asunto': datos['asunto'].replace(',', '&#44;'),
        'mensaje': datos['mensaje'].replace(',', '&#44;'),
        'categoria': datos['categoria'].replace(',', '&#44;'),
        'fecha': datos['fecha'].replace(',', '&#44;')
    }
    
    try:
        with open(archivo_csv, 'a', newline='', encoding='utf-8') as file:
            # Si es un archivo nuevo, escribir el encabezado
            if is_new_file:
                file.write('nombre,email,asunto,mensaje,categoria,fecha\n')
            
            # Escribir los datos directamente
            file.write(f"{datos_escaped['nombre']},{datos_escaped['email']},{datos_escaped['asunto']},{datos_escaped['mensaje']},{datos_escaped['categoria']},{datos_escaped['fecha']}\n")
            
            print(f"Datos guardados en CSV para: {datos['nombre']}")
    except Exception as e:
        print(f"Error al guardar en CSV: {e}")

# Funciones para persistencia con SQLite
def guardar_en_sqlite(datos):
    try:
        contacto = Contacto(
            nombre=datos['nombre'],
            email=datos['email'],
            asunto=datos['asunto'],
            mensaje=datos['mensaje'],
            categoria=datos['categoria']
        )
        
        db.session.add(contacto)
        db.session.commit()
        print("Datos guardados correctamente en SQLite")
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar en SQLite: {e}")

# Funciones para persistencia con MySQL
def guardar_en_mysql(datos):
    connection = get_connection()
    if connection is None:
        print("No se pudo conectar a MySQL para guardar los datos")
        return
    
    try:
        cursor = connection.cursor()
        # Insertar un nuevo registro en la tabla usuarios
        query = """
        INSERT INTO usuarios (nombre, email) 
        VALUES (%s, %s)
        """
        values = (datos['nombre'], datos['email'])
        cursor.execute(query, values)
        connection.commit()
        print(f"Datos guardados correctamente en MySQL. ID: {cursor.lastrowid}")
    except Error as e:
        print(f"Error al guardar en MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Ruta para probar la conexión a MySQL
@app.route('/test_db')
def test_db():
    result = test_connection()
    return jsonify(result)

if __name__ == '__main__':
    print(f"Aplicación Flask iniciada. Base de datos SQLite: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Verificando conexión a MySQL...")
    mysql_info = test_connection()
    if mysql_info['status'] == 'success':
        print(f"MySQL: {mysql_info['message']}")
    else:
        print(f"MySQL: {mysql_info['message']}")
    
    app.run(debug=True)