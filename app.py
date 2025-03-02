from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_para_formularios'  # Necesario para CSRF protection

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
            'categoria': form.categoria.data
        }
        
        # Redireccionar a la página de resultados con los datos
        return render_template('resultado.html', title='Resultado', datos=datos)
    
    # Si es GET o si el formulario no es válido, mostrar la página del formulario
    return render_template('formulario.html', title='Formulario', form=form)

if __name__ == '_main_':
    app.run(debug=True)