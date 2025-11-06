import tkinter as tk
from tkinter import ttk, messagebox
import heapq  # Para la cola de prioridad (open_list)
import random
import time

# Constantes del Grid 
ANCHO = 35      # Celdas de ancho
ALTO = 25     # Celdas de alto
TAM_CELDA = 20       # Tamaño de cada celda en píxeles
TIEMPO_ANIM = 10 # Delay en ms para la visualización del algoritmo
TIEMPO_CAMINO = 25      # Delay en ms para dibujar el camino final

# Tipos de Celdas (para el grid lógico) 
VACIO = 0
MURO = 1
INICIO = 2
FINAL = 3

# Colores para la visualización 
COLORS = {
    VACIO: "white",        # Vacío
    MURO: "black",         # Muro
    INICIO: "green",        # Inicio
    FINAL: "red",            # Fin
    "open": "lightgreen",     # Nodos en la open_list
    "closed": "lightblue",    # Nodos en la closed_list
    "path": "gold"            # Camino final
}

class Node:

    def __init__(self, position, parent=None):
        self.position = position  # Tupla (fila, columna)
        self.parent = parent
        
        self.g = 0  # Costo desde el inicio hasta este nodo
        self.h = 0  # Costo heurístico (estimado) desde este nodo hasta el final
        self.f = 0  # Costo total (f = g + h)

    def __eq__(self, other):
        # Dos nodos son iguales si sus posiciones son iguales
        return self.position == other.position

    def __hash__(self):
        # Necesario para poder usar nodos en un 'set'
        return hash(self.position)

    def __lt__(self, other):
        # Necesario para que heapq (cola de prioridad) ordene por costo F
        return self.f < other.f

class AStarPathfinder:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Algoritmo A*")
        self.root.resizable(False, False)

        # Variables de estado 
        self.grid_data = [[VACIO for _ in range(ANCHO)] for _ in range(ALTO)]
        self.start_pos = None
        self.end_pos = None
        self.is_running = False  # Previene ediciones mientras el algoritmo corre
        self.after_id = None     # Para poder cancelar la animación

        # Variables del algoritmo 
        self.nodes = []          # Grid 2D de objetos Node
        self.open_list = []      # Cola de prioridad (min-heap)
        self.closed_set = set()  # Set para nodos ya visitados (acceso O(1))
        
        # Configuración de la Interfaz 
        
        # Frame de controles (botones, radio)
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame del canvas (laberinto)
        canvas_frame = ttk.Frame(self.root, padding=(0, 10, 10, 10))
        canvas_frame.pack(side=tk.RIGHT)

        # Canvas para dibujar el grid
        self.canvas = tk.Canvas(canvas_frame, 
                                width=ANCHO * TAM_CELDA, 
                                height=ALTO * TAM_CELDA, 
                                bg="grey")
        self.canvas.pack()

        # Controles 
        
        # Botones
        action_frame = ttk.LabelFrame(control_frame, text="Acciones", padding=10)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Iniciar A*", command=self.iniciar).pack(fill=tk.X)
        ttk.Button(action_frame, text="Generar Laberinto", command=self.genera_laberinto).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Limpiar Camino", command=self.limpiar_camino).pack(fill=tk.X)
        ttk.Button(action_frame, text="Limpiar Tablero", command=self.limpiar_tablero).pack(fill=tk.X, pady=5)

        edit_frame = ttk.LabelFrame(control_frame, text="Modo de Edición", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)
        
        self.edit_mode = tk.StringVar(value="wall")
        
        ttk.Radiobutton(edit_frame, text="Poner Muro", variable=self.edit_mode, value="wall").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Poner Inicio", variable=self.edit_mode, value="start").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Poner Fin", variable=self.edit_mode, value="end").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Borrar", variable=self.edit_mode, value="empty").pack(anchor=tk.W)

        self.canvas.bind("<Button-1>", self.handle_mouse_click)
        self.canvas.bind("<B1-Motion>", self.handle_mouse_click)

        # Inicialización 
        self.canvas_rects = [[None for _ in range(ANCHO)] for _ in range(ALTO)]
        self.dibuja_tablero()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Manejar cierre


    def dibuja_tablero(self):

        self.canvas.delete("all")
        for r in range(ALTO):
            for c in range(ANCHO):
                node_type = self.grid_data[r][c]
                color = COLORS[node_type]
                
                x1 = c * TAM_CELDA
                y1 = r * TAM_CELDA
                x2 = x1 + TAM_CELDA
                y2 = y1 + TAM_CELDA
                
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="grey")
                self.canvas_rects[r][c] = rect_id

    def cambia_color(self, r, c, color):

        rect_id = self.canvas_rects[r][c]
        self.canvas.itemconfig(rect_id, fill=color)

    def definir_tipo(self, r, c, new_type):

        # Ignorar si está fuera de los límites
        if not (0 <= r < ALTO and 0 <= c < ANCHO):
            return

        # Obtener el tipo actual
        current_type = self.grid_data[r][c]

        if current_type == new_type:
            return

        # Establecer el inicio
        if new_type == INICIO:
            if self.start_pos:
                old_r, old_c = self.start_pos
                self.grid_data[old_r][old_c] = VACIO
                self.cambia_color(old_r, old_c, COLORS[VACIO])
            
            self.start_pos = (r, c)
            
        # Establecer el fin
        elif new_type == FINAL:

            if self.end_pos:
                old_r, old_c = self.end_pos
                self.grid_data[old_r][old_c] = VACIO
                self.cambia_color(old_r, old_c, COLORS[VACIO])
            
            
            self.end_pos = (r, c)

        # Borrar

        if current_type == INICIO:
            self.start_pos = None
        elif current_type == FINAL:
            self.end_pos = None

        self.grid_data[r][c] = new_type
        self.cambia_color(r, c, COLORS[new_type])

    def handle_mouse_click(self, event):

        if self.is_running:
            return

        c = event.x // TAM_CELDA
        r = event.y // TAM_CELDA
        
        # Cambiar de Modo
        mode = self.edit_mode.get()
        
        if mode == "wall":
            self.definir_tipo(r, c, MURO)
        elif mode == "start":
            self.definir_tipo(r, c, INICIO)
        elif mode == "end":
            self.definir_tipo(r, c, FINAL)
        elif mode == "empty":
            self.definir_tipo(r, c, VACIO)

    

    def limpiar_tablero(self):

        self.detener() # Detiene cualquier animación en curso
        
        self.start_pos = None
        self.end_pos = None
        self.grid_data = [[VACIO for _ in range(ANCHO)] for _ in range(ALTO)]
        self.dibuja_tablero() # Redibuja el grid vacío

    def limpiar_camino(self):
        
        self.detener()
        
        # Redibuja el grid. Esto borra los colores de "open", "closed" y "path"
        # y restaura los colores base (muro, inicio, fin, vacío).
        self.dibuja_tablero()

    def genera_laberinto(self):

        if self.is_running:
            return

        self.limpiar_tablero()
        
        self.grid_data = [[MURO for _ in range(ANCHO)] for _ in range(ALTO)]
        visited = set()
        stack = []
        path_cells = [] 

        start_r = random.randrange(1, ALTO, 2)
        start_c = random.randrange(1, ANCHO, 2)
        
        stack.append((start_r, start_c))
        visited.add((start_r, start_c))
        self.grid_data[start_r][start_c] = VACIO
        path_cells.append((start_r, start_c))

        while stack:
            r, c = stack[-1] 
            
            neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < ALTO and 0 <= nc < ANCHO and
                    (nr, nc) not in visited):
                    neighbors.append((nr, nc))

            if neighbors:
                
                nr, nc = random.choice(neighbors)
                
                wall_r, wall_c = (r + nr) // 2, (c + nc) // 2
                self.grid_data[wall_r][wall_c] = VACIO
                self.grid_data[nr][nc] = VACIO
                
                path_cells.append((nr, nc))
                path_cells.append((wall_r, wall_c))
                
                visited.add((nr, nc))
                stack.append((nr, nc))
            else:
                # Si no hay vecinos, retroceder
                stack.pop()

        # Poner el Inicio y Fin aleatoriamente
        pos_start = random.choice(path_cells)
        pos_end = random.choice(path_cells)
        
        while pos_start == pos_end:
            pos_end = random.choice(path_cells)
            
        self.definir_tipo(pos_start[0], pos_start[1], INICIO)
        self.definir_tipo(pos_end[0], pos_end[1], FINAL)

        # Redibujar todo el laberinto generado
        self.dibuja_tablero()


    def iniciar(self):

        if self.is_running:
            return
            
        # Validar que tengamos inicio y fin
        if not self.start_pos or not self.end_pos:
            messagebox.showerror("Error", "Debes establecer un punto de INICIO y un punto de FIN.")
            return

        self.limpiar_camino()
        self.is_running = True

        self.nodes = [[Node((r, c)) for c in range(ANCHO)] for r in range(ALTO)]
        self.open_list = []
        self.closed_set = set()

        # Configurar el nodo inicial
        start_node = self.nodes[self.start_pos[0]][self.start_pos[1]]
        start_node.g = 0
        start_node.h = self.heuristic(start_node.position, self.end_pos)
        start_node.f = start_node.g + start_node.h

        heapq.heappush(self.open_list, start_node)  # Usamos heapq para mantener el nodo con menor 'f' al frente
        
        self.sig_paso()

    def sig_paso(self):
    
        if not self.open_list:
            self.is_running = False
            messagebox.showinfo("Resultado", "No se encontró un camino.")
            return

        # Obtener el nodo con el menor costo
        current_node = heapq.heappop(self.open_list)
        
        # Si ya procesamos este nodo (versiones con peor 'g' pueden quedar en la cola), lo ignoramos.
        if current_node in self.closed_set:
            self.after_id = self.root.after(TIEMPO_ANIM, self.sig_paso)
            return
            
        self.closed_set.add(current_node)

        # Colorear la celda cerrada
        r, c = current_node.position
        if current_node.position != self.start_pos:
            self.cambia_color(r, c, COLORS["closed"])
            
        # Se llego al final
        if current_node.position == self.end_pos:
            self.recrea_camino(current_node)
            self.is_running = False
            return

        # Explorar Vecinos
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc # Posición del vecino

            # Validar Vecinos
            if not (0 <= nr < ALTO and 0 <= nc < ANCHO):
                continue
            if self.grid_data[nr][nc] == MURO:
                continue
            neighbor_node = self.nodes[nr][nc]
            if neighbor_node in self.closed_set:
                continue

            # Calcular costos
            new_g = current_node.g + 1 # Costo de 1
            
            # Comprobar si este es el mejor camino
            if new_g < neighbor_node.g or neighbor_node.g == 0:
                neighbor_node.g = new_g
                neighbor_node.h = self.heuristic(neighbor_node.position, self.end_pos)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                neighbor_node.parent = current_node
                
                # Añadir a la lista para explorarlo
                heapq.heappush(self.open_list, neighbor_node)
                
                # Colorear celdas disponibles
                if neighbor_node.position != self.end_pos:
                    self.cambia_color(nr, nc, COLORS["open"])

        self.after_id = self.root.after(TIEMPO_ANIM, self.sig_paso)

    def heuristic(self, pos_a, pos_b): # Usando Distancia Manhathan para calcular la heuristica
        
        r1, c1 = pos_a
        r2, c2 = pos_b
        return abs(r1 - r2) + abs(c1 - c2)

    def recrea_camino(self, end_node):

        path = []
        current = end_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        
        path.reverse() # Se pintaba de fin a inicio, esto lo invierte
        
        # Iniciar la animación de dibujar el camino
        self.animar_camino(path)

    def animar_camino(self, path):
        
        if not path:
            self.is_running = False
            return
        
        # Sacar la siguiente celda del camino
        r, c = path.pop(0)
        
        # No repintar el inicio ni el fin
        if (r, c) != self.start_pos and (r, c) != self.end_pos:
            self.cambia_color(r, c, COLORS["path"])
            
        self.after_id = self.root.after(TIEMPO_CAMINO, lambda: self.animar_camino(path))


    def detener(self):

        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            
    def on_close(self): # Si se cierra la ventana, se elimina el proceso

        self.detener()
        self.root.destroy()


# Punto de Entrada Principal 
if __name__ == "__main__":
    main_window = tk.Tk()
    app = AStarPathfinder(main_window)
    main_window.mainloop()