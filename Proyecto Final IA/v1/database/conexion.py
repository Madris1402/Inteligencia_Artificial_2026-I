import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Conexion:
    """Clase para manejar la conexión a la base de datos"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'horarios')
        self.port = os.getenv('DB_PORT', '3306')
        self.conexion = None
        self.cursor = None
        
    def conectar(self):
        """Establece la conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                port = self.port
            )
            
            if self.conexion.is_connected():
                self.cursor = self.conexion.cursor(dictionary=True)
                return True
            
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return False
        
    def desconectar(self):
        """Cierra la conexión a la base de datos"""
        if self.conexion and self.conexion.is_connected():
            if self.cursor:
                self.cursor.close()
            self.conexion.close()
            
    def ejecutarSelect(self, query, params=None):
        """Ejecuta una consulta SELECT y devuelve los resultados"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            resultados = self.cursor.fetchall()
            return resultados
        
        except Exception as e:
            print(f"Error al ejecutar query: {e}")
            return None
    
    def ejecutarQuery(self, query, params=None):
        """Ejecuta INSERT, UPDATE o DELETE y devuelve el ID insertado"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            self.conexion.commit()
            return self.cursor.lastrowid
        
        except Error as e:
            self.conexion.rollback()
            print(f"Error al ejecutar operación: {e}")
            return None
        
    def obtenerUno(self, query, params=None):
        """Ejecuta una consulta y devuelve solo el primer resultado"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            resultado = self.cursor.fetchone()
            return resultado
        
        except Error as e:
            print(f"Error al ejecutar operación: {e}")
            return None