from database.conexion import Conexion

class Salon:
    """Modelo para gestionar salones"""
    
    def __init__(self, id_salon=None, nombre=None):
        self.id_salon = id_salon
        self.nombre = nombre
    
    @staticmethod
    def obtenerTodos():
        """Obtiene todos los salones de la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_salon, nombre 
            FROM salones 
            ORDER BY nombre
        """
        
        resultados = db.ejecutarSelect(query)
        db.desconectar()
        
        salones = []
        if resultados:
            for row in resultados:
                salon = Salon(
                    id_salon=row['id_salon'],
                    nombre=row['nombre']
                )
                salones.append(salon)
        
        return salones
    
    @staticmethod
    def obtenerPorId(id_salon):
        """Obtiene un salón específico por su ID"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_salon, nombre 
            FROM salones 
            WHERE id_salon = %s
        """
        
        resultado = db.obtenerUno(query, (id_salon,))
        db.desconectar()
        
        if resultado:
            return Salon(
                id_salon=resultado['id_salon'],
                nombre=resultado['nombre']
            )
        
        return None
    
    def guardar(self):
        """Guarda un nuevo salón en la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            INSERT INTO salones (nombre) 
            VALUES (%s)
        """
        
        self.id_salon = db.ejecutarQuery(query, (self.nombre,))
        
        db.desconectar()
        return self.id_salon
    
    def __str__(self):
        return self.nombre