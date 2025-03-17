import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Establece una conexión con la base de datos MySQL.
    
    Returns:
        mysql.connector.connection: Objeto de conexión a MySQL
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='desarrollo_web',
            user='root',
            password='1234'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def test_connection():
    """
    Prueba la conexión a MySQL y devuelve información sobre la conexión.
    
    Returns:
        dict: Información sobre la conexión a MySQL
    """
    connection = get_connection()
    if connection is None:
        return {
            "status": "error",
            "message": "No se pudo conectar a la base de datos MySQL"
        }
    
    try:
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            
            return {
                "status": "success",
                "server_info": db_info,
                "database": record[0] if record else None,
                "message": "Conexión a MySQL establecida correctamente"
            }
    except Error as e:
        return {
            "status": "error",
            "message": f"Error al obtener información de MySQL: {e}"
        }
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()