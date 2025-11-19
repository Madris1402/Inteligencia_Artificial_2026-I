from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

class ExportadorPDF:
    """Clase para exportar horarios a PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.configurar_estilos()
    
    def configurar_estilos(self):
        """Configura estilos personalizados"""
        
        # Estilo para el título
        self.styles.add(ParagraphStyle(
            name='TituloPersonalizado',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulo
        self.styles.add(ParagraphStyle(
            name='SubtituloPersonalizado',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Estilo para información
        self.styles.add(ParagraphStyle(
            name='InfoPersonalizado',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
    
    def exportar_horario(self, combinacion, numero_opcion, tiene_advertencia, minutos_empalme, 
                        turno, semestre, nombre_archivo=None):
        """
        Exporta un horario a PDF
        
        Args:
            combinacion: Tupla de grupos del horario
            numero_opcion: Número de la opción de horario
            tiene_advertencia: Si tiene conflictos
            minutos_empalme: Minutos de empalme
            turno: Turno seleccionado
            semestre: Semestre
            nombre_archivo: Nombre del archivo (opcional)
        """
        
        # Crear nombre de archivo si no se proporciona
        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"Horario Final - Opcion {numero_opcion} ({timestamp}).pdf"
        
        # Asegurar que termine en .pdf
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf'
        
        # Crear el PDF en orientación horizontal
        doc = SimpleDocTemplate(nombre_archivo, pagesize=landscape(letter),
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=30)
        
        # Contenedor para los elementos del PDF
        elements = []
        
        # ===== ENCABEZADO =====
        titulo = Paragraph("HORARIO FINAL", self.styles['TituloPersonalizado'])
        elements.append(titulo)
        
        subtitulo = Paragraph("Ingeniería en Computación", self.styles['SubtituloPersonalizado'])
        elements.append(subtitulo)
        
        # Información general
        info_general = f"""
        <b>Semestre:</b> {semestre} | 
        <b>Turno:</b> {turno} | 
        <b>Opción:</b> {numero_opcion} | 
        <b>Generado:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}
        """
        
        if tiene_advertencia:
            info_general += f" | <b><font color='red'>Empalme: {minutos_empalme} min</font></b>"
        
        info = Paragraph(info_general, self.styles['InfoPersonalizado'])
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        # ===== TABLA DE HORARIOS =====
        
        # Organizar datos por materia
        datos_tabla = []
        
        # Encabezados
        encabezados = ['Materia', 'Grupo', 'Profesor', 'Lunes', 'Martes', 'Miércoles', 
                      'Jueves', 'Viernes', 'Sábado']
        datos_tabla.append(encabezados)
        
        # Obtener horarios detallados
        from models.grupo import Grupo
        
        for grupo in combinacion:
            horarios = Grupo.obtenerHorariosDetallados(grupo.id_grupo)
            
            # Organizar por día
            dias_info = {
                'Lunes': '',
                'Martes': '',
                'Miércoles': '',
                'Jueves': '',
                'Viernes': '',
                'Sábado': ''
            }
            
            for h in horarios:
                dia = h['dia_semana']
                hora_inicio = str(h['hora_inicio'])[:5] if hasattr(h['hora_inicio'], 'total_seconds') else h['hora_inicio']
                hora_fin = str(h['hora_fin'])[:5] if hasattr(h['hora_fin'], 'total_seconds') else h['hora_fin']
                
                info_dia = f"{hora_inicio}-{hora_fin}\n{grupo.salon}"
                dias_info[dia] = info_dia
            
            # Formatear datos
            materia_texto = f"{grupo.materia['clave']} - {grupo.materia['nombre']}"
            
            # Obtener correo del profesor
            from models.profesor import Profesor
            profesor_obj = Profesor.obtenerPorId(grupo.id_profesor)
            profesor_texto = grupo.profesor
            if profesor_obj and profesor_obj.correo:
                profesor_texto += f"\n{profesor_obj.correo}"
            
            # Agregar fila
            fila = [
                materia_texto,
                str(grupo.grupo),
                profesor_texto,
                dias_info['Lunes'],
                dias_info['Martes'],
                dias_info['Miércoles'],
                dias_info['Jueves'],
                dias_info['Viernes'],
                dias_info['Sábado']
            ]
            
            datos_tabla.append(fila)
        
        # Crear tabla con anchos ajustados
        tabla = Table(datos_tabla, colWidths=[2.4*inch,    # Materia (más ancho)
                                              0.6*inch,    # Grupo
                                              2.2*inch,    # Profesor (más ancho)
                                              0.95*inch,   # Lunes
                                              0.95*inch,   # Martes
                                              0.95*inch,   # Miércoles
                                              0.95*inch,   # Jueves
                                              0.95*inch,   # Viernes
                                              0.95*inch])  # Sábado
        
        # Estilo de la tabla
        estilo_tabla = TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5BA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Materia - izquierda
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Grupo - centro
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),      # Profesor - izquierda
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'),   # Días - centro
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, -1), 6.5),      # Materia - más pequeña
            ('FONTSIZE', (1, 1), (1, -1), 9),        # Grupo
            ('FONTSIZE', (2, 1), (2, -1), 7),        # Profesor - más pequeña
            ('FONTSIZE', (3, 1), (-1, -1), 8),       # Días - más pequeña
            ('TOPPADDING', (0, 1), (-1, -1), 10),    # Más padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10), # Más padding
            ('LEFTPADDING', (0, 1), (-1, -1), 6),    # Padding izquierdo
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),   # Padding derecho
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#34495e')),
        ])
        
        # Agregar colores alternados
        for i in range(1, len(datos_tabla)):
            if i % 2 == 0:
                estilo_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ecf0f1'))
        
        tabla.setStyle(estilo_tabla)
        elements.append(tabla)
        
        # ===== PIE DE PÁGINA =====
        elements.append(Spacer(1, 30))
        
        # Leyenda
        leyenda_texto = """
        <b>Leyenda:</b><br/>
        • El horario muestra la hora de inicio y fin de cada clase.<br/>
        • Debajo de cada horario se indica el salón.<br/>
        • Verifica la disponibilidad de salones antes del inicio del semestre.
        """
        
        if tiene_advertencia:
            leyenda_texto += f"<br/><b><font color='red'>ADVERTENCIA: Este horario tiene un empalme de {minutos_empalme} minutos entre clases.</font></b>"
        
        leyenda = Paragraph(leyenda_texto, self.styles['InfoPersonalizado'])
        elements.append(leyenda)
        
        # Construir PDF
        doc.build(elements)
        
        return nombre_archivo
    
    def exportar_multiples_horarios(self, horarios_generados, turno, semestre, nombre_base):
        """
        Exporta múltiples horarios a un solo PDF
        
        Args:
            horarios_generados: Lista de opciones de horarios
            turno: Turno seleccionado
            semestre: Semestre
            nombre_base: Nombre base del archivo
        """
        
        nombre_archivo = f"{nombre_base}.pdf"
        
        # Crear el PDF en orientación horizontal
        doc = SimpleDocTemplate(nombre_archivo, pagesize=landscape(letter),
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=30)
        
        elements = []
        
        # Para cada horario
        for idx, opcion in enumerate(horarios_generados, 1):
            
            # Título de la opción
            titulo = Paragraph(f"OPCIÓN {idx} DE {len(horarios_generados)}", 
                             self.styles['TituloPersonalizado'])
            elements.append(titulo)
            
            subtitulo = Paragraph("Ingeniería en Computación", self.styles['SubtituloPersonalizado'])
            elements.append(subtitulo)
            
            # Información
            tiene_advertencia = opcion['tiene_advertencia']
            minutos_empalme = opcion['minutos_empalme']
            
            info_general = f"""
            <b>Semestre:</b> {semestre} | 
            <b>Turno:</b> {turno} | 
            <b>Generado:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}
            """
            
            if tiene_advertencia:
                info_general += f" | <b><font color='red'>empalme: {minutos_empalme} min</font></b>"
            else:
                info_general += " | <b><font color='green'>Sin conflictos</font></b>"
            
            info = Paragraph(info_general, self.styles['InfoPersonalizado'])
            elements.append(info)
            elements.append(Spacer(1, 20))
            
            # Tabla
            datos_tabla = []
            encabezados = ['Materia', 'Grupo', 'Profesor', 'Lunes', 'Martes', 'Miércoles', 
                          'Jueves', 'Viernes', 'Sábado']
            datos_tabla.append(encabezados)
            
            from models.grupo import Grupo
            
            for grupo in opcion['combinacion']:
                horarios = Grupo.obtenerHorariosDetallados(grupo.id_grupo)
                
                dias_info = {
                    'Lunes': '', 'Martes': '', 'Miércoles': '',
                    'Jueves': '', 'Viernes': '', 'Sábado': ''
                }
                
                for h in horarios:
                    dia = h['dia_semana']
                    hora_inicio = str(h['hora_inicio'])[:5] if hasattr(h['hora_inicio'], 'total_seconds') else h['hora_inicio']
                    hora_fin = str(h['hora_fin'])[:5] if hasattr(h['hora_fin'], 'total_seconds') else h['hora_fin']
                    
                    info_dia = f"{hora_inicio}-{hora_fin}\n{grupo.salon}"
                    dias_info[dia] = info_dia
                
                materia_texto = f"{grupo.materia['clave']}\n{grupo.materia['nombre']}"
                
                from models.profesor import Profesor
                profesor_obj = Profesor.obtenerPorId(grupo.id_profesor)
                profesor_texto = grupo.profesor
                if profesor_obj and profesor_obj.correo:
                    profesor_texto += f"\n{profesor_obj.correo}"
                
                fila = [
                    materia_texto, str(grupo.grupo), profesor_texto,
                    dias_info['Lunes'], dias_info['Martes'], dias_info['Miércoles'],
                    dias_info['Jueves'], dias_info['Viernes'], dias_info['Sábado']
                ]
                
                datos_tabla.append(fila)
            
            # Crear tabla con anchos ajustados
            tabla = Table(datos_tabla, colWidths=[2.4*inch,    # Materia
                                                  0.6*inch,    # Grupo
                                                  2.2*inch,    # Profesor
                                                  0.95*inch,   # Lunes
                                                  0.95*inch,   # Martes
                                                  0.95*inch,   # Miércoles
                                                  0.95*inch,   # Jueves
                                                  0.95*inch,   # Viernes
                                                  0.95*inch])  # Sábado
            
            estilo_tabla = TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5BA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Materia - izquierda
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Grupo - centro
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),      # Profesor - izquierda
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'),   # Días - centro
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, -1), 6.5),      # Materia - más pequeña
            ('FONTSIZE', (1, 1), (1, -1), 9),        # Grupo
            ('FONTSIZE', (2, 1), (2, -1), 7),        # Profesor - más pequeña
            ('FONTSIZE', (3, 1), (-1, -1), 8),       # Días - más pequeña
            ('TOPPADDING', (0, 1), (-1, -1), 10),    # Más padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10), # Más padding
            ('LEFTPADDING', (0, 1), (-1, -1), 6),    # Padding izquierdo
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),   # Padding derecho
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#34495e')),
        ])
            
            for i in range(1, len(datos_tabla)):
                if i % 2 == 0:
                    estilo_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ecf0f1'))
            
            tabla.setStyle(estilo_tabla)
            elements.append(tabla)
            
            # Separador entre opciones
            if idx < len(horarios_generados):
                elements.append(PageBreak())
        
        # Construir PDF
        doc.build(elements)
        
        return nombre_archivo