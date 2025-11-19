import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# Asumo que estas importaciones funcionan en tu entorno local
from models.materia import Materia
from models.grupo import Grupo
from controllers.generador import GeneradorHorarios
from utils.exportar import ExportadorPDF
from datetime import datetime
import os

class GeneradorHorariosGUI:
    """Interfaz gráfica para el generador de horarios"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Horarios - ICO")
        
        # Colores
        self.backcolor = "#2b2b2b"
        self.textcolor = "#ffffff"
        self.secondcolor = "#404040"
        
        self.accentcolor = "#486CA5"
        self.activecolor = "#1e3c70"
        self.disablecolor = "#A1A1A1"
        
        # Configurar fondo principal
        self.root.config(bg=self.backcolor)
        
        # Maximizar ventana
        self.root.state('zoomed')
        self.root.resizable(True, True)
        
        # Variables
        self.materias_disponibles = []
        self.materias_optativas = []
        self.grupos_disponibles = []
        self.materias_seleccionadas = []
        self.grupos_seleccionados = []
        self.horarios_generados = []
        self.indice_actual = 0
        self.generador = GeneradorHorarios()
        self.modo_seleccion = tk.StringVar(value='basico') 
        
        # Estilos
        self.configurarEstilos()
        
        # Crear interfaz
        self.crearInterfaz()
        
    def configurarEstilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para Treeview (tabla)
        style.configure("Treeview",
                        background=self.backcolor,
                        foreground=self.textcolor,
                        fieldbackground=self.backcolor,
                        rowheight=60,
                        font=('Arial', 11))
        
        style.configure("Treeview.Heading",
                        font=('Arial', 12, 'bold'),
                        background=self.accentcolor,
                        foreground='white',
                        relief='flat')
        
        style.map('Treeview.Heading',
                  background=[('active', self.activecolor)])
        
        # Estilo para Scrollbars
        style.configure("Vertical.TScrollbar", 
                        background=self.secondcolor, 
                        troughcolor=self.backcolor,
                        arrowcolor="white")
                        
    def crearInterfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Header
        frame_header = tk.Frame(self.root, padx=20, pady=20, bg=self.backcolor)
        frame_header.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(frame_header, text="GENERADOR DE HORARIOS", 
                 font=('Arial', 28, 'bold'), fg='white', bg=self.backcolor).pack()
        
        tk.Label(frame_header, text="Ingeniería en Computación", 
                 font=('Arial', 14), fg=self.textcolor, bg=self.backcolor).pack()
        
        #Configuración y Materias
        frame_superior = tk.Frame(self.root, bg=self.backcolor)
        frame_superior.pack(side=tk.TOP, fill=tk.BOTH, padx=15, pady=15)
        
        # COLUMNA IZQUIERDA: Configuración
        frame_config = tk.LabelFrame(frame_superior, text=" Configuración ", 
                                     font=('Arial', 13, 'bold'), padx=20, pady=15,
                                     bg=self.backcolor, fg=self.textcolor)
        frame_config.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Semestre
        frame_semestre = tk.Frame(frame_config, bg=self.backcolor)
        frame_semestre.pack(fill=tk.X, pady=8)
        
        tk.Label(frame_semestre, text="Semestre:", font=('Arial', 12),
                 bg=self.backcolor, fg=self.textcolor).pack(side=tk.LEFT, padx=(0, 10))
        
        self.combo_semestre = ttk.Combobox(frame_semestre, values=list(range(1, 10)), 
                                           state='readonly', width=12, font=('Arial', 12))
        self.combo_semestre.pack(side=tk.LEFT)
        self.combo_semestre.current(0)
        self.combo_semestre.bind('<<ComboboxSelected>>', self.cargarMaterias)
        
        # Turno
        frame_turno = tk.Frame(frame_config, bg=self.backcolor)
        frame_turno.pack(fill=tk.X, pady=8)
        
        tk.Label(frame_turno, text="Turno:", font=('Arial', 12),
                 bg=self.backcolor, fg=self.textcolor).pack(side=tk.LEFT, padx=(0, 10))
        
        self.var_turno = tk.StringVar(value='Mixto')
        
        
        def crear_radio(parent, text, val):
            tk.Radiobutton(parent, text=text, variable=self.var_turno, 
                          value=val, font=('Arial', 11),
                          bg=self.backcolor, fg=self.textcolor,
                          selectcolor=self.backcolor,
                          activebackground=self.secondcolor, activeforeground='white'
                          ).pack(side=tk.LEFT, padx=8)

        crear_radio(frame_turno, "Matutino", 'Matutino')
        crear_radio(frame_turno, "Vespertino", 'Vespertino')
        crear_radio(frame_turno, "Mixto", 'Mixto')
        
        # Margen de error
        frame_margen = tk.Frame(frame_config, bg=self.backcolor)
        frame_margen.pack(fill=tk.X, pady=8)
        
        tk.Label(frame_margen, text="Margen de error (min):", 
                 font=('Arial', 12), bg=self.backcolor, fg=self.textcolor).pack(side=tk.LEFT, padx=(0, 10))
        
        self.spinbox_margen = tk.Spinbox(frame_margen, from_=0, to=30, width=8, 
                                         font=('Arial', 12),
                                         bg=self.secondcolor, fg='white', buttonbackground=self.secondcolor)
        self.spinbox_margen.pack(side=tk.LEFT)
        
        # Límite de opciones
        frame_limite = tk.Frame(frame_config, bg=self.backcolor)
        frame_limite.pack(fill=tk.X, pady=8)
        
        tk.Label(frame_limite, text="Límite de opciones:", 
                 font=('Arial', 12), bg=self.backcolor, fg=self.textcolor).pack(side=tk.LEFT, padx=(0, 10))
        
        self.spinbox_limite = tk.Spinbox(frame_limite, from_=5, to=50, width=8, 
                                         font=('Arial', 12),
                                         bg=self.secondcolor, fg='white', buttonbackground=self.secondcolor)
        self.spinbox_limite.delete(0, tk.END)
        self.spinbox_limite.insert(0, "20")
        self.spinbox_limite.pack(side=tk.LEFT)
        
        # Modo de selección
        frame_modo = tk.LabelFrame(frame_config, text=" Modo de Selección ", 
                                   font=('Arial', 11, 'bold'), padx=10, pady=10,
                                   bg=self.backcolor, fg=self.textcolor)
        frame_modo.pack(fill=tk.X, pady=(15, 0))
        
        tk.Radiobutton(frame_modo, text="Básico (por materia)", 
                       variable=self.modo_seleccion,
                       value='basico', font=('Arial', 11),
                       command=self.cambiarModoSeleccion,
                       bg=self.backcolor, fg=self.textcolor, selectcolor=self.backcolor,
                       activebackground=self.secondcolor, activeforeground='white'
                       ).pack(anchor='w', pady=3)
        
        tk.Radiobutton(frame_modo, text="Avanzado (materia + profesor + grupo)", 
                       variable=self.modo_seleccion,
                       value='avanzado', font=('Arial', 11),
                       command=self.cambiarModoSeleccion,
                       bg=self.backcolor, fg=self.textcolor, selectcolor=self.backcolor,
                       activebackground=self.secondcolor, activeforeground='white'
                       ).pack(anchor='w', pady=3)
        
        # COLUMNA DERECHA: Materias
        frame_materias = tk.LabelFrame(frame_superior, text=" Materias ", 
                                      font=('Arial', 13, 'bold'), padx=20, pady=15,
                                      bg=self.backcolor, fg=self.textcolor)
        frame_materias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Botón cargar materias
        tk.Button(frame_materias, text="Cargar Materias", command=self.cargarMaterias, 
                  font=('Arial', 12, 'bold'),
                  bg=self.accentcolor, fg='white',
                  activebackground=self.activecolor, activeforeground='white',
                  padx=20, pady=8, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=(0, 10))
        
        # Frame con scroll para materias
        frame_scroll = tk.Frame(frame_materias, bg=self.backcolor)
        frame_scroll.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas_materias = tk.Canvas(frame_scroll, yscrollcommand=scrollbar.set, 
                                         highlightthickness=0, bg=self.backcolor) 
        self.canvas_materias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas_materias.yview)
        
        self.frame_lista_materias = tk.Frame(self.canvas_materias, bg=self.backcolor)
        self.canvas_materias.create_window((0, 0), window=self.frame_lista_materias, anchor='nw')
        
        self.frame_lista_materias.bind('<Configure>', 
                                       lambda e: self.canvas_materias.configure(
                                           scrollregion=self.canvas_materias.bbox('all')))
        
        # Label de contador
        self.label_contador = tk.Label(frame_materias, text="Seleccionados: 0",
                                       font=('Arial', 11, 'italic'), fg=self.textcolor, bg=self.backcolor)
        self.label_contador.pack(pady=(8, 0))
        
        # Botón generar (más grande y destacado)
        frame_btn_generar = tk.Frame(frame_superior, bg=self.backcolor)
        frame_btn_generar.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 0))
        
        tk.Button(frame_btn_generar, text="GENERAR\nHORARIOS",
                  command=self.generarHorarios, font=('Arial', 14, 'bold'),
                  bg=self.accentcolor, fg='white',
                  activebackground=self.activecolor, activeforeground='white',
                  padx=15, pady=15, relief=tk.FLAT, cursor='hand2').pack(expand=True)
        
        # ===== FRAME INFERIOR: TABLA DE HORARIOS =====
        frame_inferior = tk.Frame(self.root, bg=self.backcolor)
        frame_inferior.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Navegación superior
        frame_nav_superior = tk.Frame(frame_inferior, padx=15, pady=12, bg=self.backcolor)
        frame_nav_superior.pack(fill=tk.X)
        
        self.label_info_horario = tk.Label(frame_nav_superior, 
                                           text="Genera horarios para ver resultados",
                                           font=('Arial', 13, 'bold'), fg='white', bg=self.backcolor)
        self.label_info_horario.pack(side=tk.LEFT)
        
        # Controles de navegación
        frame_controles = tk.Frame(frame_nav_superior, bg=self.backcolor)
        frame_controles.pack(side=tk.RIGHT)
        
        self.btn_anterior = tk.Button(frame_controles, text="Anterior", 
                                      command=self.horarioAnterior,
                                      state=tk.DISABLED, font=('Arial', 11, 'bold'), 
                                      bg=self.accentcolor, fg='white', disabledforeground=self.disablecolor,
                                      padx=20, pady=6,
                                      relief=tk.FLAT, cursor='hand2')
        self.btn_anterior.pack(side=tk.LEFT, padx=5)
        
        self.label_navegacion = tk.Label(frame_controles, text="0 / 0",
                                         font=('Arial', 12, 'bold'), fg='white', 
                                         bg=self.backcolor, padx=15)
        self.label_navegacion.pack(side=tk.LEFT)
        
        self.btn_siguiente = tk.Button(frame_controles, text="Siguiente", 
                                       command=self.horarioSiguiente,
                                       state=tk.DISABLED, font=('Arial', 11, 'bold'),
                                       bg=self.accentcolor, fg='white', disabledforeground=self.disablecolor,
                                       padx=20, pady=6,
                                       relief=tk.FLAT, cursor='hand2')
        self.btn_siguiente.pack(side=tk.LEFT, padx=5)
        
        self.btn_exportar = tk.Button(frame_controles, text="Exportar PDF", 
                                      command=self.exportarPDF,
                                      state=tk.DISABLED,
                                      font=('Arial', 11, 'bold'), 
                                      bg="#c74536", fg='white', disabledforeground=self.disablecolor,
                                      padx=20, pady=6,
                                      relief=tk.FLAT, cursor='hand2')
        self.btn_exportar.pack(side=tk.LEFT, padx=(15, 0))
        
        # Frame para la tabla
        frame_tabla = tk.Frame(frame_inferior, relief=tk.SOLID, borderwidth=1, bg=self.backcolor)
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Crear Treeview (tabla)
        columnas = ('materia', 'grupo', 'profesor', 'lunes', 'martes', 
                    'miercoles', 'jueves', 'viernes', 'sabado')
        
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('materia', text='Materia')
        self.tree.heading('grupo', text='Grupo')
        self.tree.heading('profesor', text='Profesor')
        self.tree.heading('lunes', text='Lunes')
        self.tree.heading('martes', text='Martes')
        self.tree.heading('miercoles', text='Miércoles')
        self.tree.heading('jueves', text='Jueves')
        self.tree.heading('viernes', text='Viernes')
        self.tree.heading('sabado', text='Sábado')
        
        # Anchos de columnas
        self.tree.column('materia', width=250, anchor='w')
        self.tree.column('grupo', width=80, anchor='center')
        self.tree.column('profesor', width=200, anchor='w')
        self.tree.column('lunes', width=150, anchor='center')
        self.tree.column('martes', width=150, anchor='center')
        self.tree.column('miercoles', width=150, anchor='center')
        self.tree.column('jueves', width=150, anchor='center')
        self.tree.column('viernes', width=150, anchor='center')
        self.tree.column('sabado', width=150, anchor='center')
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Empaquetar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tags para colores alternados (Ajustados para Dark Mode)
        self.tree.tag_configure('oddrow', background="#2b2b2b", foreground="white")
        self.tree.tag_configure('evenrow', background="#383838", foreground="white")
    
    def cambiarModoSeleccion(self):
        """Cambia entre modo básico y avanzado"""
        self.cargarMaterias()
        
    def cargarMaterias(self, event=None):
        """Carga las materias según el modo seleccionado"""
        
        modo = self.modo_seleccion.get()
        
        if modo == 'basico':
            self.cargarMateriasBasico()
        else:
            self.cargarMateriasAvanzado()
    
    def cargarMateriasBasico(self):
        """Carga las materias en modo básico (solo materias)"""
        
        # Limpiar lista anterior
        for widget in self.frame_lista_materias.winfo_children():
            widget.destroy()
        
        self.materias_disponibles = []
        self.materias_optativas = []
        self.materias_seleccionadas = []
        
        # Obtener semestre
        semestre = int(self.combo_semestre.get())
        
        # Cargar materias
        if semestre >= 6:
            materias_dict = Materia.obtenerSemestreOptativa(semestre)
            self.materias_disponibles = materias_dict['regulares']
            self.materias_optativas = materias_dict['optativas']
        else:
            self.materias_disponibles = Materia.obtenerPorSemestre(semestre)
        
        # Mostrar materias regulares
        if self.materias_disponibles:
            tk.Label(self.frame_lista_materias, text="MATERIAS REGULARES",
                     font=('Arial', 11, 'bold'), bg="#5e52b8", fg='white',
                     pady=5).pack(fill=tk.X, pady=(0, 5))
            
            for materia in self.materias_disponibles:
                var = tk.BooleanVar()
                
                cb = tk.Checkbutton(self.frame_lista_materias, 
                                   text=f"{materia.clave} - {materia.nombre}",
                                   variable=var, font=('Arial', 11),
                                   command=self.actualizarContador,
                                   fg=self.textcolor, bg=self.backcolor, selectcolor=self.backcolor,
                                   activebackground=self.backcolor, activeforeground=self.textcolor,
                                   cursor='hand2')
                cb.pack(anchor='w', padx=15, pady=3)
                
                cb.materia = materia
                cb.var = var
        
        # Mostrar optativas
        if self.materias_optativas:
            tk.Label(self.frame_lista_materias, text="MATERIAS OPTATIVAS",
                     font=('Arial', 11, 'bold'), bg="#553686", fg='white',
                     pady=5).pack(fill=tk.X, pady=(10, 5))
            
            for materia in self.materias_optativas:
                var = tk.BooleanVar()
                
                cb = tk.Checkbutton(self.frame_lista_materias, 
                                   text=f"[OPT] {materia.clave} - {materia.nombre}",
                                   variable=var, font=('Arial', 11),
                                   command=self.actualizarContador,
                                   fg=self.textcolor, bg=self.backcolor, selectcolor=self.backcolor,
                                   activebackground=self.backcolor, activeforeground=self.textcolor,
                                   cursor='hand2')
                cb.pack(anchor='w', padx=15, pady=3)
                
                cb.materia = materia
                cb.var = var
        
        if not self.materias_disponibles and not self.materias_optativas:
            tk.Label(self.frame_lista_materias, text="No hay materias disponibles",
                     font=('Arial', 11), fg='red', bg=self.backcolor).pack(pady=20)
        
        self.actualizarContador()
    
    def cargarMateriasAvanzado(self):
        """Carga las materias en modo avanzado (materia + profesor + grupo)"""
        
        # Limpiar lista anterior
        for widget in self.frame_lista_materias.winfo_children():
            widget.destroy()
        
        self.grupos_disponibles = []
        self.grupos_seleccionados = []
        
        # Obtener semestre y turno
        semestre = int(self.combo_semestre.get())
        turno = self.var_turno.get()
        
        # Obtener materias
        if semestre >= 6:
            materias_dict = Materia.obtenerSemestreOptativa(semestre)
            materias = materias_dict['regulares'] + materias_dict['optativas']
        else:
            materias = Materia.obtenerPorSemestre(semestre)
        
        if not materias:
            tk.Label(self.frame_lista_materias, text="No hay materias disponibles",
                     font=('Arial', 11), fg='red', bg=self.backcolor).pack(pady=20)
            return
        
        # Para cada materia, obtener sus grupos
        for materia in materias:
            # Obtener grupos según el turno seleccionado
            grupos_materia = []
            
            if turno == 'Mixto':
                grupos_mat = Grupo.obtenerGruposPorMateriaTurno(materia.id_materia, 'Matutino')
                grupos_vesp = Grupo.obtenerGruposPorMateriaTurno(materia.id_materia, 'Vespertino')
                grupos_materia = grupos_mat + grupos_vesp
            else:
                grupos_materia = Grupo.obtenerGruposPorMateriaTurno(materia.id_materia, turno)
            
            if grupos_materia:
                # Header de la materia
                es_optativa = materia.semestre == 10
                bg_color = "#16a085" if es_optativa else "#2ecc71"
                texto_materia = f"[OPT] {materia.clave} - {materia.nombre}" if es_optativa else f"{materia.clave} - {materia.nombre}"
                
                tk.Label(self.frame_lista_materias, text=texto_materia,
                         font=('Arial', 11, 'bold'), bg=bg_color, fg='white',
                         pady=5).pack(fill=tk.X, pady=(5, 0))
                
                # Mostrar cada grupo
                for grupo in grupos_materia:
                    var = tk.BooleanVar()
                    
                    # Obtener horarios para mostrarlos
                    horarios_texto = ""
                    for horario in grupo.horarios:
                        horarios_texto += f"{horario['dias']} {horario['hora_inicio']}-{horario['hora_fin']} | "
                    horarios_texto = horarios_texto.rstrip(" | ")
                    
                    texto_grupo = f"   Grupo {grupo.grupo} | Prof: {grupo.profesor}\n"
                    texto_grupo += f"   {horarios_texto}"
                    
                    cb = tk.Checkbutton(self.frame_lista_materias, 
                                       text=texto_grupo,
                                       variable=var, font=('Arial', 10),
                                       command=self.actualizarContador,
                                       fg=self.textcolor, bg=self.backcolor, selectcolor=self.backcolor,
                                       justify='left', activebackground=self.backcolor, activeforeground=self.textcolor,
                                       cursor='hand2')
                    cb.pack(anchor='w', padx=25, pady=2)
                    
                    cb.grupo = grupo
                    cb.var = var
                    
                    self.grupos_disponibles.append(grupo)
        
        self.actualizarContador()
        
    def actualizarContador(self):
        """Actualiza el contador de selecciones"""
        count = 0
        
        for widget in self.frame_lista_materias.winfo_children():
            if isinstance(widget, tk.Checkbutton) and widget.var.get():
                count += 1
        
        modo = self.modo_seleccion.get()
        if modo == 'basico':
            self.label_contador.config(text=f"Materias seleccionadas: {count}")
        else:
            self.label_contador.config(text=f"Grupos seleccionados: {count}")
        
    def obtenerMateriasSeleccionadas(self):
        """Obtiene las IDs de las materias seleccionadas (modo básico)"""
        ids = []
        
        for widget in self.frame_lista_materias.winfo_children():
            if isinstance(widget, tk.Checkbutton) and widget.var.get():
                if hasattr(widget, 'materia'):
                    ids.append(widget.materia.id_materia)
        
        return ids
    
    def obtenerGruposSeleccionados(self):
        """Obtiene los IDs de grupos seleccionados (modo avanzado)"""
        ids = []
        
        for widget in self.frame_lista_materias.winfo_children():
            if isinstance(widget, tk.Checkbutton) and widget.var.get():
                if hasattr(widget, 'grupo'):
                    ids.append(widget.grupo.id_grupo)
        
        return ids
    
    def generarHorarios(self):
        """Genera los horarios según la configuración y modo"""
        
        modo = self.modo_seleccion.get()
        
        if modo == 'basico':
            self.generarHorariosBasico()
        else:
            self.generarHorariosAvanzado()
    
    def generarHorariosBasico(self):
        """Genera horarios en modo básico (el generador elige los grupos)"""
        
        # Validar materias seleccionadas
        ids_materias = self.obtenerMateriasSeleccionadas()
        
        if not ids_materias:
            messagebox.showwarning("Sin materias", 
                                  "Debes seleccionar al menos una materia")
            return
        
        if len(ids_materias) > 7:
            respuesta = messagebox.askyesno("Advertencia", 
                                           "Has seleccionado más de 7 materias.\n" +
                                           "Esto puede tomar mucho tiempo.\n" +
                                           "Incluso puede no haber solución válida.\n\n" +
                                           "¿Deseas continuar?")
            if not respuesta:
                return
        
        # Obtener configuración
        turno = self.var_turno.get()
        margen = int(self.spinbox_margen.get())
        limite = int(self.spinbox_limite.get())
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.label_info_horario.config(text="Generando horarios, espera un momento...",
                                      fg='#f39c12')
        self.root.update()
        
        # Generar
        try:
            self.horarios_generados = self.generador.generar(
                ids_materias, 
                turno, 
                limite=limite,
                margen_error=margen
            )
            
            if self.horarios_generados:
                self.indice_actual = 0
                self.mostrarHorarioActual()
                self.actualizarNavegacion()
                
                # Habilitar botones
                self.btn_exportar.config(state=tk.NORMAL)
                
                # Mensaje de éxito
                sin_conflictos = len([h for h in self.horarios_generados if not h['tiene_advertencia']])
                con_conflictos = len(self.horarios_generados) - sin_conflictos
                
                mensaje = f"Se generaron {len(self.horarios_generados)} opciones\n\n"
                mensaje += f"• Sin conflictos: {sin_conflictos}\n"
                if con_conflictos > 0:
                    mensaje += f"• Con empalme permitido: {con_conflictos}"
                
                messagebox.showinfo("Éxito", mensaje)
            else:
                self.label_info_horario.config(text="No se encontraron horarios válidos",
                                              fg='#e74c3c')
                
                messagebox.showwarning("Sin resultados", 
                                      "No se pudieron generar horarios válidos.\n\n" +
                                      "Intenta:\n" +
                                      "• Aumentar el margen de error\n" +
                                      "• Seleccionar 'Mixto' turnos\n" +
                                      "• Reducir el número de materias")
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()
    
    def generarHorariosAvanzado(self):
        """Genera horario con grupos específicos seleccionados"""
        
        ids_grupos = self.obtenerGruposSeleccionados()
        
        if not ids_grupos:
            messagebox.showwarning("Sin grupos", 
                                  "Debes seleccionar al menos un grupo")
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.label_info_horario.config(text="Verificando horario...",
                                      fg='#f39c12')
        self.root.update()
        
        try:
            # Obtener los objetos Grupo completos
            grupos_seleccionados = []
            for widget in self.frame_lista_materias.winfo_children():
                if isinstance(widget, tk.Checkbutton) and widget.var.get():
                    if hasattr(widget, 'grupo'):
                        grupos_seleccionados.append(widget.grupo)
            
            # Verificar conflictos
            tiene_conflicto, minutos_conflicto = self.generador._tieneConflictos(tuple(grupos_seleccionados))
            
            # Crear opción de horario
            opcion = {
                'combinacion': tuple(grupos_seleccionados),
                'tiene_advertencia': tiene_conflicto,
                'minutos_empalme': minutos_conflicto
            }
            
            self.horarios_generados = [opcion]
            self.indice_actual = 0
            self.mostrarHorarioActual()
            self.actualizarNavegacion()
            
            # Habilitar botones
            self.btn_exportar.config(state=tk.NORMAL)
            
            # Mensaje
            if tiene_conflicto:
                messagebox.showwarning("Conflicto detectado", 
                                      f"Los grupos seleccionados tienen un empalme de {minutos_conflicto} minutos.\n\n" +
                                      "El horario se muestra pero tiene conflictos.")
            else:
                messagebox.showinfo("Éxito", 
                                   "Los grupos seleccionados no tienen conflictos.\nHorario válido.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()
    
    def mostrarHorarioActual(self):
        """Muestra el horario en el índice actual en la tabla"""
        
        if not self.horarios_generados:
            return
        
        opcion = self.horarios_generados[self.indice_actual]
        
        # Actualizar info
        tiene_advertencia = opcion['tiene_advertencia']
        minutos = opcion['minutos_empalme']
        
        if tiene_advertencia:
            texto_info = f"Opción {self.indice_actual + 1} de {len(self.horarios_generados)} - empalme de {minutos} min"
            color_info = self.accentcolor
        else:
            texto_info = f"Opción {self.indice_actual + 1} de {len(self.horarios_generados)} - Sin conflictos"
            color_info = '#27ae60'
        
        self.label_info_horario.config(text=texto_info, fg=color_info)
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener datos del horario
        combinacion = opcion['combinacion']
        
        # Organizar por materia
        for idx, grupo in enumerate(combinacion):
            # Obtener horarios detallados
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
            
            # Formatear materia y profesor
            materia_texto = f"{grupo.materia['clave']} - {grupo.materia['nombre']}"
            
            # Obtener correo del profesor
            from models.profesor import Profesor
            profesor_obj = Profesor.obtenerPorId(grupo.id_profesor)
            profesor_texto = grupo.profesor
            if profesor_obj and profesor_obj.correo:
                profesor_texto += f"\n{profesor_obj.correo}"
            
            # Insertar en la tabla con tag para color alternado
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            self.tree.insert('', 'end', values=(
                materia_texto,
                grupo.grupo,
                profesor_texto,
                dias_info['Lunes'],
                dias_info['Martes'],
                dias_info['Miércoles'],
                dias_info['Jueves'],
                dias_info['Viernes'],
                dias_info['Sábado']
            ), tags=(tag,))
    
    def actualizarNavegacion(self):
        """Actualiza los botones de navegación"""
        
        total = len(self.horarios_generados)
        
        if total == 0:
            self.btn_anterior.config(state=tk.DISABLED)
            self.btn_siguiente.config(state=tk.DISABLED)
            self.label_navegacion.config(text="0 / 0")
            return
        
        self.label_navegacion.config(text=f"{self.indice_actual + 1} / {total}")
        
        # Botón anterior
        if self.indice_actual > 0:
            self.btn_anterior.config(state=tk.NORMAL)
        else:
            self.btn_anterior.config(state=tk.DISABLED)
        
        # Botón siguiente
        if self.indice_actual < total - 1:
            self.btn_siguiente.config(state=tk.NORMAL)
        else:
            self.btn_siguiente.config(state=tk.DISABLED)
    
    def horarioAnterior(self):
        """Muestra el horario anterior"""
        if self.indice_actual > 0:
            self.indice_actual -= 1
            self.mostrarHorarioActual()
            self.actualizarNavegacion()
    
    def horarioSiguiente(self):
        """Muestra el siguiente horario"""
        if self.indice_actual < len(self.horarios_generados) - 1:
            self.indice_actual += 1
            self.mostrarHorarioActual()
            self.actualizarNavegacion()
    
    def exportarPDF(self):
        """Exporta el horario actual a PDF"""
        
        if not self.horarios_generados:
            messagebox.showwarning("Sin horarios", 
                                  "No hay horarios generados para exportar")
            return
        
        try:
            # Preguntar si quiere exportar solo el actual o todos
            respuesta = messagebox.askquestion(
                "Exportar a PDF",
                "¿Deseas exportar TODOS los horarios generados?\n\n" +
                "SI = Exportar todas las opciones\n" +
                "NO = Exportar solo el horario actual"
            )
            
            exportador = ExportadorPDF()
            
            if respuesta == 'yes':
                # Exportar todos los horarios
                nombre_archivo = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=f"Propuesta de Horarios Completo ({datetime.now().strftime('%Y%m%d_%H%M%S')}).pdf"
                )
                
                if nombre_archivo:
                    semestre = int(self.combo_semestre.get())
                    turno = self.var_turno.get()
                    
                    archivo_generado = exportador.exportar_multiples_horarios(
                        self.horarios_generados,
                        turno,
                        semestre,
                        nombre_archivo.replace('.pdf', '')
                    )
                    
                    messagebox.showinfo("Éxito", 
                                       f"Se exportaron {len(self.horarios_generados)} horarios exitosamente.\n\n" +
                                       f"Archivo: {os.path.basename(archivo_generado)}")
            else:
                # Exportar solo el actual
                nombre_archivo = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=f"Horario Final - Opcion {self.indice_actual + 1} ({datetime.now().strftime('%Y%m%d_%H%M%S')}).pdf"
                )
                
                if nombre_archivo:
                    opcion = self.horarios_generados[self.indice_actual]
                    semestre = int(self.combo_semestre.get())
                    turno = self.var_turno.get()
                    
                    archivo_generado = exportador.exportar_horario(
                        opcion['combinacion'],
                        self.indice_actual + 1,
                        opcion['tiene_advertencia'],
                        opcion['minutos_empalme'],
                        turno,
                        semestre,
                        nombre_archivo
                    )
                    
                    messagebox.showinfo("Éxito", 
                                       f"Horario exportado exitosamente.\n\n" +
                                       f"Archivo: {os.path.basename(archivo_generado)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()