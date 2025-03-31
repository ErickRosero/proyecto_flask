from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from mysql.connector import Error
import json

class User(UserMixin):
    def __init__(self, id_usuario, nombre, email, password=None, fecha_creacion=None):
        self.id = id_usuario  # Importante: debe ser "id" para Flask-Login
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.password_hash = password
        self.fecha_creacion = fecha_creacion

    def set_password(self, password):
        """Genera hash de la contraseña proporcionada."""
        self.password_hash = generate_password_hash(password)
        return self.password_hash

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convierte el usuario a un diccionario para respuestas JSON."""
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'fecha_creacion': self.fecha_creacion
        }

    @staticmethod
    def get_by_id(connection, user_id):
        """Obtiene un usuario por su ID."""
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE id_usuario = %s"
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    id_usuario=user_data['id_usuario'],
                    nombre=user_data['nombre'],
                    email=user_data['email'],
                    password=user_data.get('password_hash'),
                    fecha_creacion=user_data.get('fecha_creacion')
                )
            return None
        except Error as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None

    @staticmethod
    def get_by_email(connection, email):
        """Obtiene un usuario por su email."""
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    id_usuario=user_data['id_usuario'],
                    nombre=user_data['nombre'],
                    email=user_data['email'],
                    password=user_data.get('password_hash'),
                    fecha_creacion=user_data.get('fecha_creacion')
                )
            return None
        except Error as e:
            print(f"Error al obtener usuario por email: {e}")
            return None

    @staticmethod
    def create_user(connection, nombre, email, password):
        """Crea un nuevo usuario en la base de datos."""
        try:
            # Crear un objeto de usuario temporal para generar el hash
            temp_user = User(None, nombre, email)
            password_hash = temp_user.set_password(password)
            
            cursor = connection.cursor()
            
            # Verificar si el usuario ya existe
            check_query = "SELECT * FROM usuarios WHERE email = %s"
            cursor.execute(check_query, (email,))
            if cursor.fetchone():
                cursor.close()
                return None, "El email ya está registrado"
            
            # Insertar el nuevo usuario
            query = """
            INSERT INTO usuarios (nombre, email, password_hash) 
            VALUES (%s, %s, %s)
            """
            values = (nombre, email, password_hash)
            cursor.execute(query, values)
            connection.commit()
            
            # Obtener el ID del usuario recién creado
            user_id = cursor.lastrowid
            cursor.close()
            
            # Devolver el usuario creado
            return User(user_id, nombre, email, password_hash), None
        except Error as e:
            if connection.is_connected():
                connection.rollback()
            print(f"Error al crear usuario: {e}")
            return None, f"Error en la base de datos: {str(e)}"