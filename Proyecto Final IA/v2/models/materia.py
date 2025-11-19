from database.conexion import Conexion

class Materia:
    """Modelo para gestionar materias"""
    
    def __init__(self, id_materia=None, clave=None, nombre=None, semestre=None):
        self.id_materia = id_materia
        self.clave = clave
        self.nombre = nombre
        self.semestre = semestre
        
    @staticmethod
    def obtenerTodas():
        """Obtiene todas las materias de la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_materia, clave, nombre, semestre
            FROM materias
            ORDER BY semestre, nombre
        """
        
        resultados = db.ejecutarSelect(query)
        db.desconectar()
        
        materias = []
        if resultados:
            for row in resultados:
                mat = Materia(
                    id_materia=row['id_materia'],
                    clave=row['clave'],
                    nombre=row['nombre'],
                    semestre=row['semestre']
                )
                materias.append(mat)
        
        return materias
    
    @staticmethod
    def obtenerPorSemestre(semestre):
        """Obtiene las materias de un semestre específico"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_materia, clave, nombre, semestre
            FROM materias
            WHERE semestre = %s
            ORDER BY nombre
        """
        
        resultados = db.ejecutarSelect(query, (semestre,))
        db.desconectar()
        
        materias = []
        if resultados:
            for row in resultados:
                mat = Materia(
                    id_materia=row['id_materia'],
                    clave=row['clave'],
                    nombre=row['nombre'],
                    semestre=row['semestre']
                )
                materias.append(mat)
        
        return materias
    
    @staticmethod
    def obtenerPorId(id_materia):
        """Obtiene una materia específica por su ID"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_materia, clave, nombre, semestre 
            FROM materias 
            WHERE id_materia = %s
        """
        
        resultado = db.obtenerUno(query, (id_materia,))
        db.desconectar()
        
        if resultado:
            return Materia(
                id_materia=resultado['id_materia'],
                clave=resultado['clave'],
                nombre=resultado['nombre'],
                semestre=resultado['semestre']
            )
        
        return None
    
    def guardar(self):
        """Guarda una nueva materia en la base de datos"""
        db = Conexion()
        db.conectar()
        
        query = """
            INSERT INTO materias (clave, nombre, semestre) 
            VALUES (%s, %s, %s)
        """
        
        params = (self.clave, self.nombre, self.semestre)
        self.id_materia = db.ejecutar_insert(query, params)
        
        db.desconectar()
        return self.id_materia

    @staticmethod
    def obtenerOptativas():
        """Obtiene todas las materias optativas (semestre 10)"""
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT id_materia, clave, nombre, semestre 
            FROM materias 
            WHERE semestre = 10
            ORDER BY nombre
        """
        
        resultados = db.ejecutarSelect(query)
        db.desconectar()
        
        materias = []
        if resultados:
            for row in resultados:
                mat = Materia(
                    id_materia=row['id_materia'],
                    clave=row['clave'],
                    nombre=row['nombre'],
                    semestre=row['semestre']
                )
                materias.append(mat)
        
        return materias
    
    @staticmethod
    def obtenerSemestreOptativa(semestre):
        """
        Obtiene materias de un semestre específico.
        Si es semestre >= 6, incluye también las optativas.
        
        Args:
            semestre (int): Número de semestre (1-10)
            
        Returns:
            dict: {'regulares': [...], 'optativas': [...]}
        """
        # Obtener materias regulares del semestre
        materias_regulares = Materia.obtenerPorSemestre(semestre)
        
        resultado = {
            'regulares': materias_regulares,
            'optativas': []
        }
        
        # Si es semestre 6 o mayor, agregar optativas
        if semestre >= 6:
            resultado['optativas'] = Materia.obtenerOptativas()
        
        return resultado
    
    def __str__(self):
        return f"{self.clave} - {self.nombre}"