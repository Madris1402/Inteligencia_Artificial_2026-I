from database.conexion import Conexion

class Profesor: 
    """Modelo para gestionar profesores"""
    
    def __init__(self, id_profesor=None, nombre=None, paterno=None, materno=None, correo=None):
        self.id_profesor = id_profesor
        self.nombre = nombre
        self.paterno = paterno
        self.materno = materno
        self.correo = correo
        
    @staticmethod
    def obtenerTodos():
        """Obtiene todos los profesores de la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_profesor, nombre, paterno, materno, correo
            FROM profesores
            ORDER BY paterno, nombre
        """
        
        resultados = db.ejecutarSelect(query)
        db.desconectar()
        
        profesores = []
        if resultados:
            for row in resultados:
                prof = Profesor(
                    id_profesor=row['id_profesor'],
                    nombre=row['nombre'],
                    paterno=row['paterno'],
                    materno=row['materno'],
                    correo=row['correo']
                )
                profesores.append(prof)
        
        return profesores
    
    @staticmethod
    def obtenerPorId(id_profesor):
        """Obtiene un profesor específico por su ID"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_profesor, nombre, paterno, materno, correo
            FROM profesores
            WHERE id_profesor = %s
        """
        
        resultado = db.obtenerUno(query, (id_profesor,))
        db.desconectar()
        
        if resultado:
            return Profesor(
                id_profesor=resultado['id_profesor'],
                nombre=resultado['nombre'],
                paterno=resultado['paterno'],
                materno=resultado['materno'],
                correo=resultado['correo']
            )
            
        return None
    
    def nombre_completo(self):
        """Devuelve el nombre completo del profesor"""
        if self.materno:
            return f"{self.nombre} {self.paterno} {self.materno}"
        return f"{self.nombre} {self.paterno}"
    
    def guardar(self):
        """Guarda un nuevo profesor en la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            INSERT INTO profesores (nombre, paterno, materno, correo) 
            VALUES (%s, %s, %s, %s)
        """
        
        params = (self.nombre, self.paterno, self.materno, self.correo)
        self.id_profesor = db.ejecutarQuery(query, params)
        
        db.desconectar()
        return self.id_profesor
    
    def __str__(self):
        return self.nombre_completo()