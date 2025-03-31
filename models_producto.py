from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from mysql.connector import Error

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[DataRequired(message='El nombre es obligatorio')])
    precio = DecimalField('Precio', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0.01, message='El precio debe ser mayor que 0')
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message='El stock es obligatorio'),
        NumberRange(min=0, message='El stock no puede ser negativo')
    ])
    submit = SubmitField('Guardar')

class Producto:
    def __init__(self, id_producto=None, nombre=None, precio=None, stock=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
    
    @staticmethod
    def obtener_todos(connection):
        """Obtiene todos los productos de la base de datos."""
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM productos ORDER BY id_producto"
            cursor.execute(query)
            productos = cursor.fetchall()
            cursor.close()
            return productos
        except Error as e:
            print(f"Error al obtener productos: {e}")
            return []
    
    @staticmethod
    def obtener_por_id(connection, id_producto):
        """Obtiene un producto por su ID."""
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM productos WHERE id_producto = %s"
            cursor.execute(query, (id_producto,))
            producto = cursor.fetchone()
            cursor.close()
            return producto
        except Error as e:
            print(f"Error al obtener producto por ID: {e}")
            return None
    
    @staticmethod
    def crear(connection, nombre, precio, stock):
        """Crea un nuevo producto en la base de datos."""
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO productos (nombre, precio, stock) 
            VALUES (%s, %s, %s)
            """
            values = (nombre, precio, stock)
            cursor.execute(query, values)
            connection.commit()
            id_producto = cursor.lastrowid
            cursor.close()
            return id_producto, None
        except Error as e:
            if connection.is_connected():
                connection.rollback()
            return None, f"Error al crear producto: {str(e)}"
    
    @staticmethod
    def actualizar(connection, id_producto, nombre, precio, stock):
        """Actualiza un producto existente."""
        try:
            cursor = connection.cursor()
            query = """
            UPDATE productos 
            SET nombre = %s, precio = %s, stock = %s 
            WHERE id_producto = %s
            """
            values = (nombre, precio, stock, id_producto)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            return True, None
        except Error as e:
            if connection.is_connected():
                connection.rollback()
            return False, f"Error al actualizar producto: {str(e)}"
    
    @staticmethod
    def eliminar(connection, id_producto):
        """Elimina un producto de la base de datos."""
        try:
            cursor = connection.cursor()
            query = "DELETE FROM productos WHERE id_producto = %s"
            cursor.execute(query, (id_producto,))
            connection.commit()
            cursor.close()
            return True, None
        except Error as e:
            if connection.is_connected():
                connection.rollback()
            return False, f"Error al eliminar producto: {str(e)}"