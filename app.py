from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, RadioField
from wtforms.validators import DataRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
import os
import json
import csv
from datetime import datetime

# Obtener la ruta absoluta del directorio actual
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Crear directorios si no existen
os.makedirs(os.path.join(BASE_DIR, 'datos'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_para_formularios'  # Necesario para CSRF protection

# Configurar la base de datos con ruta absoluta
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database", "usuarios.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

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

# Crear la base de datos y tablas
with app.app_context():
    try:
        db.create_all()
        print(f"Base de datos creada en: {os.path.join(BASE_DIR, 'database', 'usuarios.db')}")
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

# Definición del formulario usando WTForms
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
            ('sqlite', 'Solo SQLite')
        ],
        default='todos'
    )
    
    # Campos adicionales para formatos secundarios
    guardar_txt = BooleanField('Guardar en TXT', default=False)
    guardar_json = BooleanField('Guardar en JSON', default=False)
    guardar_csv = BooleanField('Guardar en CSV', default=False)
    guardar_sqlite = BooleanField('Guardar en SQLite', default=False)
    
    submit = SubmitField('Enviar')

@app.route('/')
def inicio():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return render_template('usuario.html', title='Perfil', nombre=nombre)

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/formulario', methods=['GET', 'POST'])
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
            
            # Comprobar formatos secundarios
            if formato_principal != 'txt' and form.guardar_txt.data:
                guardar_en_txt(datos)
            if formato_principal != 'json' and form.guardar_json.data:
                guardar_en_json(datos)
            if formato_principal != 'csv' and form.guardar_csv.data:
                guardar_en_csv(datos)
            if formato_principal != 'sqlite' and form.guardar_sqlite.data:
                guardar_en_sqlite(datos)
            
            flash('¡Formulario enviado y guardado en los formatos seleccionados!', 'success')
        
        # Redireccionar a la página de resultados con los datos
        return render_template('resultado.html', title='Resultado', datos=datos,
                              formato_guardado=formato_principal, form=form)
    
    # Si es GET o si el formulario no es válido, mostrar la página del formulario
    return render_template('formulario.html', title='Formulario', form=form)

# Funciones para persistencia con archivos TXT
def guardar_en_txt(datos):
    archivo_txt = os.path.join(BASE_DIR, 'datos', 'datos.txt')
    with open(archivo_txt, 'a', encoding='utf-8') as file:
        file.write(f"\n--- Nuevo registro: {datos['fecha']} ---\n")
        for key, value in datos.items():
            file.write(f"{key}: {value}\n")
        file.write("--------------------------------\n")

@app.route('/ver_txt')
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

@app.route('/ver_json')
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

@app.route('/ver_csv')
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

@app.route('/ver_sqlite')
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

# API endpoints para acceso a datos
@app.route('/api/datos/json')
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
def api_datos_csv():
    archivo_csv = os.path.join(BASE_DIR, 'datos', 'datos.csv')
    datos = []
    
    if os.path.exists(archivo_csv):
        with open(archivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                datos.append(dict(row))
    
    return jsonify(datos)

@app.route('/api/datos/sqlite')
def api_datos_sqlite():
    try:
        contactos = Contacto.query.all()
        return jsonify([contacto.to_dict() for contacto in contactos])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Aplicación Flask iniciada. Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True)