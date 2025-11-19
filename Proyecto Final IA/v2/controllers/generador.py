from itertools import product
from models.grupo import Grupo
from datetime import datetime, timedelta

class GeneradorHorarios:
    """Clase para generar combinaciones de horarios sin conflictos"""
    
    def __init__(self):
        self.materiasSeleccionadas = []
        self.turnos = []
        self.opcionesMateria = {}
        self.horariosGenerados = []
        self.margenError = 0
        
    def generar(self, ids_materias, turnos='Ambos', limite=20, margen_error=0):
        """
        Genera horarios válidos sin conflictos (o con margen de error permitido)
        
        Args:
            ids_materias (list): Lista de IDs de materias seleccionadas
            turnos (str): 'Matutino', 'Vespertino' o 'Ambos'
            limite (int): Número máximo de opciones a devolver
            margen_error (int): Minutos de empalme permitidos (default 0)
            
        Returns: 
            list: Lista de combinaciones válidas de grupos
        """
        
        self.materiasSeleccionadas = ids_materias
        self.horariosGenerados = []
        self.margenError = margen_error
        
        # Determinar qué turnos buscar
        if turnos == 'Ambos':
            self.turnos = ['Matutino', 'Vespertino']
            print(f"\nGenerando horarios para {len(ids_materias)} materias (AMBOS TURNOS)...")
        else:
            self.turnos = [turnos]
            print(f"\nGenerando horarios para {len(ids_materias)} materias (turno {turnos})...")
        
        if margen_error > 0:
            print(f"Margen de error permitido: {margen_error} minutos")
        
        # Grupos disponibles por materia (considerando los turnos seleccionados)
        self.opcionesMateria = {}
        
        for id_materia in ids_materias:
            grupos_materia = []
            
            # Obtener grupos de cada turno seleccionado
            for turno in self.turnos:
                grupos = Grupo.obtenerGruposPorMateriaTurno(id_materia, turno)
                grupos_materia.extend(grupos)
            
            if not grupos_materia:
                print(f"No hay grupos disponibles para la materia ID {id_materia}")
                return []
            
            self.opcionesMateria[id_materia] = grupos_materia
            print(f"    Materia {id_materia}: {len(grupos_materia)} grupo(s) disponible(s)")
        
        # Generar combinaciones posibles
        combinaciones = self._generarCombinaciones()
        print(f"\nTotal de combinaciones posibles: {len(combinaciones)}")
        
        # Filtrar solo las válidas (sin conflictos o dentro del margen)
        horariosValidos = []
        horariosConAdvertencias = []
        
        for i, combinacion in enumerate(combinaciones, 1):
            tiene_conflicto, minutos_conflicto = self._tieneConflictos(combinacion)
            
            if not tiene_conflicto:
                # Sin conflictos
                horariosValidos.append({
                    'combinacion': combinacion,
                    'tiene_advertencia': False,
                    'minutos_empalme': 0
                })
            elif minutos_conflicto <= margen_error:
                # Con conflicto pero dentro del margen permitido
                horariosConAdvertencias.append({
                    'combinacion': combinacion,
                    'tiene_advertencia': True,
                    'minutos_empalme': minutos_conflicto
                })
            
            # Limitar el número de opciones
            if len(horariosValidos) + len(horariosConAdvertencias) >= limite:
                break

        print(f"Horarios sin conflictos: {len(horariosValidos)}")
        
        if margen_error > 0 and horariosConAdvertencias:
            print(f"Horarios con empalme dentro del margen: {len(horariosConAdvertencias)}")
        
        # Combinar ambas listas: primero los sin conflictos, luego los con advertencia
        self.horariosGenerados = horariosValidos + horariosConAdvertencias
        
        return self.horariosGenerados
    
    def _generarCombinaciones(self):
        """
        Genera todas las combinaciones posibles usando producto cartesiano
        
        Return: 
            list: Lista de tuplas, cada una es una combinación de grupos
        """
        
        # Listas de grupos por materia en orden
        listasGrupos = [
            self.opcionesMateria[id_materia] for id_materia in self.materiasSeleccionadas
        ]
        
        # Producto cartesiano: todas las posibles combinaciones
        combinaciones = list(product(*listasGrupos))
        
        return combinaciones
    
    def _tieneConflictos(self, combinacion):
        """
        Verifica si una combinación de grupos tiene conflictos de horario
        
        Args:
            combinacion (tuple): Tupla de objetos Grupo
            
        Return:
            tuple: (bool, int) - (tiene conflicto, minutos máximos de empalme)
        """
        
        max_minutos_empalme = 0
        
        # Comparar cada grupo con los demás
        for i, grupo1 in enumerate(combinacion):
            for grupo2 in combinacion[i + 1:]:
                tiene_empalme, minutos = self._gruposEmpalman(grupo1, grupo2)
                
                if tiene_empalme:
                    max_minutos_empalme = max(max_minutos_empalme, minutos)

        # Tiene conflicto si el empalme es mayor al margen permitido
        tiene_conflicto = max_minutos_empalme > self.margenError
        
        return tiene_conflicto, max_minutos_empalme
    
    def _gruposEmpalman(self, grupo1, grupo2):
        """
        Verifica si dos grupos tienen conflicto de horario y cuántos minutos
        
        Args:
            grupo1, grupo2: Objetos Grupo a comparar
            
        Returns:
            tuple: (bool, int) - (se empalman, minutos de empalme máximo)
        """
        
        # Obtener horarios detallados (dia por dia) de ambos grupos
        horarios1 = Grupo.obtenerHorariosDetallados(grupo1.id_grupo)
        horarios2 = Grupo.obtenerHorariosDetallados(grupo2.id_grupo)
        
        max_minutos_empalme = 0
        
        # Comparar cada horario de grupo 1 con cada horario de grupo 2
        for h1 in horarios1:
            for h2 in horarios2:
                if h1['dia_semana'] == h2['dia_semana']:
                    se_empalman, minutos = self._horasEmpalmadas(
                        h1['hora_inicio'], h1['hora_fin'],
                        h2['hora_inicio'], h2['hora_fin']
                    )
                    
                    if se_empalman:
                        max_minutos_empalme = max(max_minutos_empalme, minutos)
        
        return max_minutos_empalme > 0, max_minutos_empalme
    
    def _horasEmpalmadas(self, inicio1, fin1, inicio2, fin2):
        """
        Verifica si dos rangos de tiempo se empalman y calcula los minutos
        
        Args:
            inicio1, fin1: timedelta - Horario del primer grupo
            inicio2, fin2: timedelta - Horario del segundo grupo
            
        Returns:
            tuple: (bool, int) - (se empalman, minutos de empalme)
        """
        
        # Convertir timedelta a minutos para facilitar la comparación
        inicio1_mins = inicio1.total_seconds() / 60
        fin1_mins = fin1.total_seconds() / 60
        inicio2_mins = inicio2.total_seconds() / 60
        fin2_mins = fin2.total_seconds() / 60
        
        # Verificar si hay empalme
        if not (inicio1_mins < fin2_mins and fin1_mins > inicio2_mins):
            return False, 0
        
        # Calcular minutos de empalme
        inicio_empalme = max(inicio1_mins, inicio2_mins)
        fin_empalme = min(fin1_mins, fin2_mins)
        minutos_empalme = int(fin_empalme - inicio_empalme)
        
        return True, minutos_empalme
    
    def obtenerResumenHorario(self, opcion_horario):
        """
        Genera un resumen legible de una opción de horario
        
        Args:
            opcion_horario (dict): Diccionario con 'combinacion', 'tiene_advertencia', 'minutos_empalme'
            
        Returns:
            str: texto formateado con el horario completo
        """
        
        combinacion = opcion_horario['combinacion']
        tiene_advertencia = opcion_horario['tiene_advertencia']
        minutos_empalme = opcion_horario['minutos_empalme']
        
        resumen = ""
        resumen += "="*60 + "\n"
        resumen += "OPCIÓN DE HORARIO"
        
        if tiene_advertencia:
            resumen += f"(empalme de {minutos_empalme} min)\n"
        else:
            resumen += " ✓\n"
        
        resumen += "="*60 + "\n\n"
        
        for grupo in combinacion:
            # Indicador de turno
            icono_turno = "MAÑANA" if grupo.turno == "Matutino" else "TARDE"
            
            resumen += f"{grupo.materia['clave']} - {grupo.materia['nombre']}\n"
            resumen += f"   Profesor: {grupo.profesor}\n"
            resumen += f"   Salón: {grupo.salon}\n"
            resumen += f"   Grupo: {grupo.grupo}\n"
            resumen += f"   {icono_turno} Turno: {grupo.turno}\n"
            
            for horario in grupo.horarios:
                resumen += f"   {horario['dias']} | {horario['hora_inicio']} - {horario['hora_fin']}\n"
            
            resumen += "\n"
        
        if tiene_advertencia:
            resumen += "ADVERTENCIA: Este horario tiene clases empalmadas\n"
            resumen += f"    empalme máximo: {minutos_empalme} minutos\n"
        
        resumen += "="*60 + "\n"
        
        return resumen
    
    def obtenerHorarioDia(self, opcion_horario):
        """
        Organiza un horario por días de la semana
        
        Args:
            opcion_horario (dict): Diccionario con 'combinacion', 'tiene_advertencia', 'minutos_empalme'
            
        Returns:
            dict: Diccionario con días como llaves y lista de clases como valores
        """
        combinacion = opcion_horario['combinacion']
        
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        horario_por_dia = {dia: [] for dia in dias_semana}
        
        for grupo in combinacion:
            # Obtener horarios detallados (día por día)
            horarios = Grupo.obtenerHorariosDetallados(grupo.id_grupo)
            
            for horario in horarios:
                dia = horario['dia_semana']
                
                clase_info = {
                    'materia': f"{grupo.materia['clave']} - {grupo.materia['nombre']}",
                    'profesor': grupo.profesor,
                    'salon': grupo.salon,
                    'grupo': grupo.grupo,
                    'turno': grupo.turno,
                    'hora_inicio': horario['hora_inicio'],
                    'hora_fin': horario['hora_fin']
                }
                
                horario_por_dia[dia].append(clase_info)
        
        # Ordenar cada día por hora de inicio
        for dia in dias_semana:
            horario_por_dia[dia].sort(key=lambda x: x['hora_inicio'])
        
        return horario_por_dia
    
    def imprimirHorarioDia(self, opcion_horario):
        """
        Imprime un horario organizado por días (vista de tabla)
        
        Args:
            opcion_horario (dict): Diccionario con información del horario
        """
        horario = self.obtenerHorarioDia(opcion_horario)
        tiene_advertencia = opcion_horario['tiene_advertencia']
        minutos_empalme = opcion_horario['minutos_empalme']
        
        print("\n" + "="*80)
        print("HORARIO SEMANAL")
        
        if tiene_advertencia:
            print(f" (empalme de {minutos_empalme} minutos)")
        
        print("="*80 + "\n")
        
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        
        for dia in dias_semana:
            clases = horario[dia]
            
            if clases:
                print(f"{dia.upper()}")
                print("-" * 80)
                
                for clase in clases:
                    icono_turno = "MAÑANA" if clase['turno'] == "Matutino" else "TARDE"
                    print(f"  {clase['hora_inicio']} - {clase['hora_fin']} | {clase['materia']} {icono_turno}")
                    print(f"   {clase['profesor']} | {clase['salon']} | Grupo {clase['grupo']}")
                    print()
            else:
                print(f"{dia.upper()}")
                print("-" * 80)
                print("  Sin clases\n")
        
        print("="*80 + "\n")