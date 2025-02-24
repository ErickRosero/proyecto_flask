# app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return render_template('usuario.html', title='Perfil', nombre=nombre)

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

if __name__ == '__main__':
    app.run(debug=True)