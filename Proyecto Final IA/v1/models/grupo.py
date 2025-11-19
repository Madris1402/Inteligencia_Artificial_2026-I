from database.conexion import Conexion
from models.materia import Materia
from models.profesor import Profesor
from models.salon import Salon

class Grupo:
    """Modelo para gestionar grupos con sus horarios"""
    
    def __init__(self, id_grupo=None, id_materia=None, id_profesor=None, 
                 id_salon=None, turno=None, grupo=None):
        self.id_grupo = id_grupo
        self.id_materia = id_materia
        self.id_profesor = id_profesor
        self.id_salon = id_salon
        self.turno = turno
        self.grupo = grupo
        
        self.materia = None
        self.profesor = None
        self.salon = None
        self.horarios = []
    
    @staticmethod
    def obtenerGruposPorMateriaTurno(id_materia, turno):
        """
        Obtiene todos los grupos de una materia en un turno específico
        con sus horarios agrupados
        """
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT 
                g.id_grupo,
                g.id_materia,
                g.id_profesor,
                g.id_salon,
                g.turno,
                g.grupo,
                m.clave,
                m.nombre AS materia_nombre,
                CONCAT(p.nombre, ' ', p.paterno, ' ', IFNULL(p.materno, '')) AS profesor_nombre,
                s.nombre AS salon_nombre,
                GROUP_CONCAT(
                    h.dia_semana 
                    ORDER BY FIELD(h.dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')
                    SEPARATOR ', '
                ) AS dias,
                TIME_FORMAT(h.hora_inicio, '%H:%i') AS hora_inicio,
                TIME_FORMAT(h.hora_fin, '%H:%i') AS hora_fin
            FROM grupos g
            JOIN materias m ON g.id_materia = m.id_materia
            JOIN profesores p ON g.id_profesor = p.id_profesor
            JOIN salones s ON g.id_salon = s.id_salon
            JOIN horarios_grupo h ON g.id_grupo = h.id_grupo
            WHERE g.id_materia = %s AND g.turno = %s
            GROUP BY g.id_grupo, h.hora_inicio, h.hora_fin
            ORDER BY g.grupo, h.hora_inicio
        """
        
        resultados = db.ejecutarSelect(query, (id_materia, turno))
        db.desconectar()
        
        # Agrupar por id_grupo
        grupos_dict = {}
        
        if resultados:
            for row in resultados:
                id_grupo = row['id_grupo']
                
                # Si es la primera vez que vemos este grupo, crearlo
                if id_grupo not in grupos_dict:
                    grupo = Grupo(
                        id_grupo=id_grupo,
                        id_materia=row['id_materia'],
                        id_profesor=row['id_profesor'],
                        id_salon=row['id_salon'],
                        turno=row['turno'],
                        grupo=row['grupo']
                    )
                    
                    # Llenar objetos relacionados
                    grupo.materia = {
                        'clave': row['clave'],
                        'nombre': row['materia_nombre']
                    }
                    grupo.profesor = row['profesor_nombre']
                    grupo.salon = row['salon_nombre']
                    grupo.horarios = []
                    
                    grupos_dict[id_grupo] = grupo
                
                # Agregar este horario al grupo
                grupos_dict[id_grupo].horarios.append({
                    'dias': row['dias'],
                    'hora_inicio': row['hora_inicio'],
                    'hora_fin': row['hora_fin']
                })
        
        return list(grupos_dict.values())
    
    @staticmethod
    def obtenerHorariosDetallados(id_grupo):
        """
        Obtiene todos los horarios individuales de un grupo
        (día por día, no agrupados)
        """
        db = Conexion()
        db.conectar()
        
        query = """
            SELECT 
                dia_semana,
                hora_inicio,
                hora_fin
            FROM horarios_grupo
            WHERE id_grupo = %s
            ORDER BY FIELD(dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'),
                     hora_inicio
        """
        
        resultados = db.ejecutarSelect(query, (id_grupo,))
        db.desconectar()
        
        return resultados if resultados else []
    
    def obtenerInformacionCompleta(self):
        """
        Devuelve un string con toda la información del grupo
        formateado para mostrar en la interfaz
        """
        info = f"{self.materia['clave']} - {self.materia['nombre']}\n"
        info += f"Prof. {self.profesor} | Grupo {self.grupo}\n"
        info += f"Salón: {self.salon}\n"
        
        for horario in self.horarios:
            info += f"{horario['dias']} {horario['hora_inicio']}-{horario['hora_fin']}\n"
        
        return info.strip()
    
    def __str__(self):
        return f"Grupo {self.grupo} - {self.materia['nombre'] if self.materia else 'N/A'}"