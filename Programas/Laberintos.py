import tkinter as tk
from tkinter import ttk, messagebox
import heapq  # Para la cola de prioridad (open_list)
import random
import time

# --- Constantes del Grid ---
GRID_WIDTH = 35      # Celdas de ancho
GRID_HEIGHT = 25     # Celdas de alto
CELL_SIZE = 20       # Tamaño de cada celda en píxeles
ANIMATION_DELAY = 10 # Delay en ms para la visualización del algoritmo
PATH_DELAY = 25      # Delay en ms para dibujar el camino final

# --- Tipos de Celdas (para el grid lógico) ---
TYPE_EMPTY = 0
TYPE_WALL = 1
TYPE_START = 2
TYPE_END = 3

# --- Colores para la visualización ---
COLORS = {
    TYPE_EMPTY: "white",        # Vacío
    TYPE_WALL: "black",         # Muro
    TYPE_START: "green",        # Inicio
    TYPE_END: "red",            # Fin
    "open": "lightgreen",     # Nodos en la open_list
    "closed": "lightblue",    # Nodos en la closed_list
    "path": "gold"            # Camino final
}

class Node:
    """
    Clase para representar un nodo en el algoritmo A*.
    Guarda su posición, su nodo 'padre' (de dónde venimos) y los costos G, H y F.
    """
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

        # --- Variables de estado ---
        self.grid_data = [[TYPE_EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.start_pos = None
        self.end_pos = None
        self.is_running = False  # Previene ediciones mientras el algoritmo corre
        self.after_id = None     # Para poder cancelar la animación

        # --- Variables del algoritmo ---
        self.nodes = []          # Grid 2D de objetos Node
        self.open_list = []      # Cola de prioridad (min-heap)
        self.closed_set = set()  # Set para nodos ya visitados (acceso O(1))
        
        # --- Configuración de la Interfaz ---
        
        # Frame de controles (botones, radio)
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame del canvas (laberinto)
        canvas_frame = ttk.Frame(self.root, padding=(0, 10, 10, 10))
        canvas_frame.pack(side=tk.RIGHT)

        # Canvas para dibujar el grid
        self.canvas = tk.Canvas(canvas_frame, 
                                width=GRID_WIDTH * CELL_SIZE, 
                                height=GRID_HEIGHT * CELL_SIZE, 
                                bg="grey")
        self.canvas.pack()

        # --- Controles ---
        
        # 1. Botones de acción
        action_frame = ttk.LabelFrame(control_frame, text="Acciones", padding=10)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Iniciar A*", command=self.start_algorithm).pack(fill=tk.X)
        ttk.Button(action_frame, text="Generar Laberinto", command=self.generate_random_maze).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Limpiar Camino", command=self.clear_path).pack(fill=tk.X)
        ttk.Button(action_frame, text="Limpiar Tablero", command=self.clear_board).pack(fill=tk.X, pady=5)

        # 2. Modo de Edición (Radio Buttons)
        edit_frame = ttk.LabelFrame(control_frame, text="Modo de Edición", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)
        
        self.edit_mode = tk.StringVar(value="wall") # Valor por defecto
        
        ttk.Radiobutton(edit_frame, text="Poner Muro", variable=self.edit_mode, value="wall").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Poner Inicio", variable=self.edit_mode, value="start").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Poner Fin", variable=self.edit_mode, value="end").pack(anchor=tk.W)
        ttk.Radiobutton(edit_frame, text="Borrar", variable=self.edit_mode, value="empty").pack(anchor=tk.W)

        # --- Eventos del Mouse ---
        self.canvas.bind("<Button-1>", self.handle_mouse_click) # Click
        self.canvas.bind("<B1-Motion>", self.handle_mouse_click) # Click y arrastrar

        # --- Inicialización ---
        self.canvas_rects = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Manejar cierre

    ## ------------------------------------------
    ## --- Funciones de Dibujo y Edición ---
    ## ------------------------------------------

    def draw_grid(self):
        """
        Dibuja el grid completo sobre el canvas.
        Crea un rectángulo para cada celda y guarda su ID en self.canvas_rects
        para poder actualizarlo individualmente después.
        """
        self.canvas.delete("all")
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                node_type = self.grid_data[r][c]
                color = COLORS[node_type]
                
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="grey")
                self.canvas_rects[r][c] = rect_id

    def update_cell_color(self, r, c, color):
        """Actualiza el color de una sola celda en el canvas."""
        rect_id = self.canvas_rects[r][c]
        self.canvas.itemconfig(rect_id, fill=color)

    def set_node_type(self, r, c, new_type):
        """
        Establece el tipo de una celda (muro, inicio, fin, vacío)
        y maneja la lógica de que solo puede haber un inicio y un fin.
        """
        # Ignorar si está fuera de los límites
        if not (0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH):
            return

        # Obtener el tipo actual
        current_type = self.grid_data[r][c]

        # No hacer nada si ya es de este tipo
        if current_type == new_type:
            return

        # --- Lógica de Inicio (Solo puede haber uno) ---
        if new_type == TYPE_START:
            # Si ya hay un inicio, borrar el antiguo
            if self.start_pos:
                old_r, old_c = self.start_pos
                self.grid_data[old_r][old_c] = TYPE_EMPTY
                self.update_cell_color(old_r, old_c, COLORS[TYPE_EMPTY])
            
            # Establecer el nuevo inicio
            self.start_pos = (r, c)
            
        # --- Lógica de Fin (Solo puede haber uno) ---
        elif new_type == TYPE_END:
            # Si ya hay un fin, borrar el antiguo
            if self.end_pos:
                old_r, old_c = self.end_pos
                self.grid_data[old_r][old_c] = TYPE_EMPTY
                self.update_cell_color(old_r, old_c, COLORS[TYPE_EMPTY])
            
            # Establecer el nuevo fin
            self.end_pos = (r, c)

        # --- Lógica de Borrado ---
        # Si borramos la celda de inicio/fin, actualizamos la variable de estado
        if current_type == TYPE_START:
            self.start_pos = None
        elif current_type == TYPE_END:
            self.end_pos = None

        # Finalmente, actualizamos el grid lógico y el visual
        self.grid_data[r][c] = new_type
        self.update_cell_color(r, c, COLORS[new_type])

    def handle_mouse_click(self, event):
        """Manejador para clicks y arrastre del mouse sobre el canvas."""
        if self.is_running:
            return # No permitir edición mientras corre el algoritmo

        # Calcular la fila y columna basado en las coordenadas del evento
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        
        # Obtener el modo de edición seleccionado
        mode = self.edit_mode.get()
        
        if mode == "wall":
            self.set_node_type(r, c, TYPE_WALL)
        elif mode == "start":
            self.set_node_type(r, c, TYPE_START)
        elif mode == "end":
            self.set_node_type(r, c, TYPE_END)
        elif mode == "empty":
            self.set_node_type(r, c, TYPE_EMPTY)

    ## ------------------------------------------
    ## --- Funciones de los Botones ---
    ## ------------------------------------------

    def clear_board(self):
        """Limpia todo el tablero, borrando muros, inicio y fin."""
        self.stop_algorithm() # Detiene cualquier animación en curso
        
        self.start_pos = None
        self.end_pos = None
        self.grid_data = [[TYPE_EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid() # Redibuja el grid vacío

    def clear_path(self):
        """
        Limpia solo los resultados del algoritmo (camino, celdas abiertas/cerradas),
        dejando los muros, inicio y fin intactos.
        """
        self.stop_algorithm()
        
        # Redibuja el grid. Esto borra los colores de "open", "closed" y "path"
        # y restaura los colores base (muro, inicio, fin, vacío).
        self.draw_grid()

    def generate_random_maze(self):
        """
        Genera un laberinto aleatorio usando el algoritmo "Recursive Backtracker" (DFS).
        Garantiza que el laberinto generado es solucionable.
        """
        if self.is_running:
            return

        self.clear_board()
        
        # 1. Empezar con un grid lleno de muros
        self.grid_data = [[TYPE_WALL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Set de celdas visitadas (fila, col)
        visited = set()
        stack = []
        
        # Almacena las celdas que son pasillos (para poner inicio/fin)
        path_cells = [] 

        # 2. Elegir una celda inicial aleatoria (debe ser impar para el algoritmo)
        start_r = random.randrange(1, GRID_HEIGHT, 2)
        start_c = random.randrange(1, GRID_WIDTH, 2)
        
        stack.append((start_r, start_c))
        visited.add((start_r, start_c))
        self.grid_data[start_r][start_c] = TYPE_EMPTY
        path_cells.append((start_r, start_c))

        while stack:
            r, c = stack[-1] # Ver el tope de la pila
            
            # 3. Encontrar vecinos no visitados (a 2 pasos de distancia)
            neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH and
                    (nr, nc) not in visited):
                    neighbors.append((nr, nc))

            if neighbors:
                # 4. Elegir un vecino aleatorio
                nr, nc = random.choice(neighbors)
                
                # 5. "Romper" el muro entre la celda actual y el vecino
                wall_r, wall_c = (r + nr) // 2, (c + nc) // 2
                self.grid_data[wall_r][wall_c] = TYPE_EMPTY
                self.grid_data[nr][nc] = TYPE_EMPTY
                
                path_cells.append((nr, nc))
                path_cells.append((wall_r, wall_c)) # El muro roto también es pasillo
                
                # 6. Moverse al vecino
                visited.add((nr, nc))
                stack.append((nr, nc))
            else:
                # 7. Si no hay vecinos, retroceder (backtrack)
                stack.pop()

        # 8. Poner el Inicio y Fin en celdas de pasillo aleatorias
        pos_start = random.choice(path_cells)
        pos_end = random.choice(path_cells)
        
        # Asegurarse de que no sean la misma celda
        while pos_start == pos_end:
            pos_end = random.choice(path_cells)
            
        self.set_node_type(pos_start[0], pos_start[1], TYPE_START)
        self.set_node_type(pos_end[0], pos_end[1], TYPE_END)

        # Redibujar todo el laberinto generado
        self.draw_grid()

    ## ------------------------------------------
    ## --- Lógica del Algoritmo A* ---
    ## ------------------------------------------

    def start_algorithm(self):
        """Prepara e inicia la ejecución paso a paso del algoritmo A*."""
        if self.is_running:
            return
            
        # 1. Validar que tengamos inicio y fin
        if not self.start_pos or not self.end_pos:
            messagebox.showerror("Error", "Debes establecer un punto de INICIO y un punto de FIN.")
            return

        # 2. Limpiar cualquier camino o visualización anterior
        self.clear_path()
        self.is_running = True

        # 3. Inicializar las estructuras de datos de A*
        self.nodes = [[Node((r, c)) for c in range(GRID_WIDTH)] for r in range(GRID_HEIGHT)]
        self.open_list = []
        self.closed_set = set()

        # 4. Configurar el nodo inicial
        start_node = self.nodes[self.start_pos[0]][self.start_pos[1]]
        start_node.g = 0
        start_node.h = self.heuristic(start_node.position, self.end_pos)
        start_node.f = start_node.g + start_node.h

        # 5. Añadir el nodo inicial a la cola de prioridad (open_list)
        # Usamos heapq para mantener el nodo con menor 'f' al frente
        heapq.heappush(self.open_list, start_node)
        
        # 6. Iniciar el bucle del algoritmo (usando root.after para animación)
        self.a_star_step()

    def a_star_step(self):
        """
        Ejecuta un solo paso del algoritmo A*.
        Se llama a sí mismo repetidamente usando 'root.after' para crear la animación.
        """
        
        # --- Condición de Parada: No hay más nodos o no se encontró camino ---
        if not self.open_list:
            self.is_running = False
            messagebox.showinfo("Resultado", "No se encontró un camino.")
            return

        # 1. Obtener el nodo con el menor costo 'f' de la cola de prioridad
        current_node = heapq.heappop(self.open_list)
        
        # Optimización: Si ya procesamos este nodo (versiones con peor 'g'
        # pueden quedar en la cola), lo ignoramos.
        if current_node in self.closed_set:
            self.after_id = self.root.after(ANIMATION_DELAY, self.a_star_step)
            return
            
        self.closed_set.add(current_node)

        # 2. Visualización: Colorear la celda 'cerrada'
        r, c = current_node.position
        if current_node.position != self.start_pos:
            self.update_cell_color(r, c, COLORS["closed"])
            
        # --- Condición de Éxito: Llegamos al final ---
        if current_node.position == self.end_pos:
            self.reconstruct_path(current_node)
            self.is_running = False
            return

        # 3. Explorar Vecinos (Arriba, Abajo, Izquierda, Derecha)
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc # Posición del vecino

            # 4. Validar Vecino
            # ¿Está dentro del grid?
            if not (0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH):
                continue
            # ¿Es un muro?
            if self.grid_data[nr][nc] == TYPE_WALL:
                continue
            # ¿Ya está en la lista cerrada?
            neighbor_node = self.nodes[nr][nc]
            if neighbor_node in self.closed_set:
                continue

            # 5. Calcular costos para el vecino
            # El costo 'g' (movimiento) es 1 (asumimos costo uniforme)
            new_g = current_node.g + 1 
            
            # 6. Comprobar si este es un mejor camino hacia el vecino
            # (Si es la primera vez que lo vemos O encontramos un camino más corto)
            if new_g < neighbor_node.g or neighbor_node.g == 0:
                neighbor_node.g = new_g
                neighbor_node.h = self.heuristic(neighbor_node.position, self.end_pos)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                neighbor_node.parent = current_node
                
                # 7. Añadir a la open_list para explorarlo
                heapq.heappush(self.open_list, neighbor_node)
                
                # 8. Visualización: Colorear la celda 'abierta'
                if neighbor_node.position != self.end_pos:
                    self.update_cell_color(nr, nc, COLORS["open"])

        # 9. Programar el siguiente paso de la animación
        self.after_id = self.root.after(ANIMATION_DELAY, self.a_star_step)

    def heuristic(self, pos_a, pos_b):
        """
        Calcula la heurística (costo estimado).
        Usamos la "Distancia Manhattan", que es perfecta para grids
        donde solo nos movemos en 4 direcciones.
        """
        r1, c1 = pos_a
        r2, c2 = pos_b
        return abs(r1 - r2) + abs(c1 - c2)

    def reconstruct_path(self, end_node):
        """
        Una vez encontrado el nodo final, retrocede usando los 'parent'
        para construir la lista del camino final.
        """
        path = []
        current = end_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        
        # El camino está al revés (del fin al inicio), lo invertimos
        path.reverse()
        
        # Iniciar la animación de dibujar el camino
        self.draw_path_animation(path)

    def draw_path_animation(self, path):
        """Dibuja el camino final de forma animada, celda por celda."""
        if not path:
            self.is_running = False # Terminó la animación del camino
            return
        
        # Sacar la siguiente celda del camino
        r, c = path.pop(0)
        
        # No repintar el inicio ni el fin
        if (r, c) != self.start_pos and (r, c) != self.end_pos:
            self.update_cell_color(r, c, COLORS["path"])
            
        # Programar el dibujo de la siguiente celda
        self.after_id = self.root.after(PATH_DELAY, lambda: self.draw_path_animation(path))

    ## ------------------------------------------
    ## --- Funciones de Control de la App ---
    ## ------------------------------------------

    def stop_algorithm(self):
        """Detiene cualquier animación 'after' que esté en curso."""
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            
    def on_close(self):
        """Manejador para el cierre de la ventana."""
        self.stop_algorithm()
        self.root.destroy()


# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = AStarPathfinder(main_window)
    main_window.mainloop()