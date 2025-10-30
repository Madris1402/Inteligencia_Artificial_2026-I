import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import random
from typing import Dict, List, Tuple
import time

# Definir el Tablero
CUADRICULA = 4
POS_INICIAL = (CUADRICULA - 1, 0) # Posición inicial

# Definición de tipos
Tile = Dict[str, bool]
Tablero = List[List[Tile]]
Position = Tuple[int, int]

class WumpusWorldGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Mundo de Wumpus")
        master.geometry("1000x600")

        # Estado del Juego 
        self.tablero: Tablero = []
        self.jugador_pos: Position = POS_INICIAL
        self.wumpus_pos: Position = (0, 0)
        self.wumpus_vive: bool = True
        self.flecha: bool = True
        self.oro_encontrado: bool = False
        self.game_over: bool = False

        # Frames Principales 
        self.game_frame = tk.Frame(master, bg='black')
        self.game_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Cuadrícula de Juego
        self.grid_labels: List[List[tk.Label]] = []
        self.crea_cuadricula()

        # Panel de Control 
        self.inicia_controles()

        # Iniciar el juego 
        self.iniciar()

    def crea_cuadricula(self):

        for r in range(CUADRICULA):
            row_labels = []
            self.game_frame.rowconfigure(r, weight=1)
            self.game_frame.columnconfigure(r, weight=1)
            for c in range(CUADRICULA):
                label = tk.Label(self.game_frame, text="?", font=('Arial', 14, 'bold'),
                                 width=8, height=4, relief="sunken", borderwidth=2,
                                 bg='black', fg='white')
                label.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                row_labels.append(label)
            self.grid_labels.append(row_labels)

    def inicia_controles(self):
        
        # Semilla 
        seed_frame = tk.Frame(self.control_frame)
        seed_frame.pack(fill='y', pady=10)
        tk.Label(seed_frame, text="Semilla:").pack(side=tk.LEFT)
        self.seed_entry = tk.Entry(seed_frame, width=20)
        self.seed_entry.pack(side=tk.LEFT, padx=20)
        tk.Button(seed_frame, text="Reiniciar Juego", command=self.iniciar).pack(side=tk.RIGHT)

        # Log de Estado 
        tk.Label(self.control_frame, text="Estado y Sensaciones:").pack(pady=(10,0))
        self.status_log = scrolledtext.ScrolledText(self.control_frame, height=20, width=45, wrap=tk.WORD, state='disabled')
        self.status_log.pack(pady=10, fill='x')

        # Movimiento 
        mover_frame = tk.LabelFrame(self.control_frame, text="Moverse")
        mover_frame.pack(pady=10, fill='x', side=tk.LEFT)
        
        tk.Button(mover_frame, text="↑", width=6, command=lambda: self.mover(-1, 0)).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(mover_frame, text="←", width=6, command=lambda: self.mover(0, -1)).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(mover_frame, text="→", width=6, command=lambda: self.mover(0, 1)).grid(row=1, column=2, padx=3, pady=3)
        tk.Button(mover_frame, text="↓", width=6, command=lambda: self.mover(1, 0)).grid(row=1, column=1, padx=3, pady=3)
        mover_frame.columnconfigure(1, weight=0) # Centrar botones

        # Acciones (Disparar) 
        action_frame = tk.LabelFrame(self.control_frame, text="Disparar Flecha")
        action_frame.pack(pady=10, fill='x', side=tk.RIGHT)
        
        tk.Button(action_frame, text="↑", width=6, command=lambda: self.disparar(-1, 0)).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(action_frame, text="←", width=6, command=lambda: self.disparar(0, -1)).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(action_frame, text="→", width=6, command=lambda: self.disparar(0, 1)).grid(row=1, column=2, padx=3, pady=3)
        tk.Button(action_frame, text="↓", width=6, command=lambda: self.disparar(1, 0)).grid(row=1, column=1, padx=3, pady=3)
        action_frame.columnconfigure(1, weight=0) # Centrar botones

    def log_status(self, message: str):

        self.status_log.config(state='normal')
        self.status_log.insert(tk.END, message + "\n")
        self.status_log.see(tk.END)
        self.status_log.config(state='disabled')

    def iniciar(self): #Estado Inicial del Juego

        # Resetear estado
        self.jugador_pos = POS_INICIAL
        self.wumpus_vive = True
        self.flecha = True
        self.oro_encontrado = False
        self.game_over = False
        self.status_log.config(state='normal')
        self.status_log.delete('1.0', tk.END)
        self.status_log.config(state='disabled')

        # Configurar Semilla
        seed_str = self.seed_entry.get()
        
        if seed_str.isdigit():
            # Semilla definida por el usuario
            current_seed = int(seed_str)
            self.log_status("==" * 22 + f"\nJuego iniciado con semilla: {current_seed}\n"+ "==" * 22)
        else:
            # Generar Semilla Aleatoria
            current_seed = round(((int(time.time())/10e4) ** 2 % 1.0)* 10e4) # El tiempo actual / 10e4, elevado al cuadrado, modulo 1.0 * 10e4 redondeado
            self.log_status("==" * 22 + f"\nJuego iniciado con semilla aleatoria: {current_seed}\n" + "==" * 22)

        # Aplicar la semilla
        random.seed(current_seed)
        self.seed_entry.delete(0, tk.END) # Limpiar el campo de texto

        # Inicializar tablero
        self.tablero = [[self.create_tile() for _ in range(CUADRICULA)] for _ in range(CUADRICULA)]

        # Colocar elementos
        self.tablero[self.jugador_pos[0]][self.jugador_pos[1]]['visitado'] = True
        
        safe_squares = [(r, c) for r in range(CUADRICULA) for c in range(CUADRICULA) if (r, c) != POS_INICIAL]
        random.shuffle(safe_squares)

        self.wumpus_pos = safe_squares.pop()
        self.tablero[self.wumpus_pos[0]][self.wumpus_pos[1]]['wumpus'] = True

        oro_pos = safe_squares.pop()
        self.tablero[oro_pos[0]][oro_pos[1]]['oro'] = True

        num_pozos = max(1, int(CUADRICULA * CUADRICULA * 0.15))
        for _ in range(num_pozos):
            if not safe_squares: break
            pozo_pos = safe_squares.pop()
            self.tablero[pozo_pos[0]][pozo_pos[1]]['pozo'] = True

        # Propagar sensaciones
        self.actualiza_sensaciones()

        # Interfaz
        self.actualiza_interfaz()
        self.log_status("¡Encuentra el oro y vuelve al inicio!\n")
        self.reporta_sensaciones()

    def create_tile(self) -> Tile:

        return {'pozo': False, 'wumpus': False, 'oro': False, 'hedor': False, 'brisa': False, 'resplandor': False, 'visitado': False}

    def actualiza_sensaciones(self):

        for r in range(CUADRICULA):
            for c in range(CUADRICULA):
                # Limpiar sensaciones antiguas
                self.tablero[r][c]['hedor'] = False
                self.tablero[r][c]['brisa'] = False
                self.tablero[r][c]['resplandor'] = False

        for r in range(CUADRICULA):
            for c in range(CUADRICULA):
                # Añadir Hedor si Wumpus está vivo
                if self.tablero[r][c]['wumpus'] and self.wumpus_vive:
                    self.sensaciones(r, c, 'hedor')
                
                # Añadir Brisa
                if self.tablero[r][c]['pozo']:
                    self.sensaciones(r, c, 'brisa')
                # Añadir Brillo
                if self.tablero[r][c]['oro']:
                    self.sensaciones(r, c, 'resplandor')
    
    def sensaciones(self, r: int, c: int, sensation_key: str):

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < CUADRICULA and 0 <= nc < CUADRICULA:
                self.tablero[nr][nc][sensation_key] = True

    def actualiza_interfaz(self):

        for r in range(CUADRICULA):
            for c in range(CUADRICULA):
                label = self.grid_labels[r][c]
                tile = self.tablero[r][c]
                
                text_lines = []
                bg = 'grey'

                if not tile['visitado']:
                    text_lines = ["?"]
                    bg = '#222' # Casi negro
                    fg = 'white'
                else:
                    # Casilla visitada
                    bg = '#555' # Gris oscuro
                    fg = 'white'
                    
                    if tile['pozo']: text_lines.append("🕳️")
                    if not self.wumpus_vive and (r,c) == self.wumpus_pos:
                        text_lines.append("👾(💀)")
                    elif tile['wumpus']: text_lines.append("👾") # Solo si moriste
                        
                    if tile['oro']: text_lines.append("🧈")
                    if tile['resplandor']: text_lines.append("✧")
                    if tile['hedor']: text_lines.append("ཀ")
                    if tile['brisa']: text_lines.append("〰")
                    if not text_lines: text_lines = ["Seguro"]

                if (r, c) == self.jugador_pos:
                    agent_text = "🧍"
                    if self.oro_encontrado:
                        agent_text = "🧍🧈"
                    
                    text_lines.insert(0, agent_text)
                    bg = 'white'
                    fg = 'black'
                
                label.config(text="\n".join(text_lines), bg=bg, fg=fg)

    def reporta_sensaciones(self):

        r, c = self.jugador_pos
        tile = self.tablero[r][c]
        messages = []
        
        if tile['resplandor']:
            self.log_status("Ves un Resplandor\n")
        if tile['hedor']:
            messages.append("Hueles un Hedor\n")
        if tile['brisa']:
            messages.append("Sientes una Brisa\n")
        
        if not messages:
            messages.append("No sientes nada aquí\n")
        
        self.log_status(" ".join(messages))

    def mover(self, dr: int, dc: int):
        if self.game_over: return

        nr, nc = self.jugador_pos[0] + dr, self.jugador_pos[1] + dc

        # Comprobar límites
        if not (0 <= nr < CUADRICULA and 0 <= nc < CUADRICULA):
            self.log_status("No puedes moverte, hay una pared")
            return

        # Mover jugador
        self.jugador_pos = (nr, nc)
        tile = self.tablero[nr][nc]
        tile['visitado'] = True
        self.log_status(f"Mueves a ({nr}, {nc})\n")

        # Comprobar peligros
        if tile['wumpus'] and self.wumpus_vive:
            self.log_status("==" * 10 + "\nGAME OVER\n\nWumpus te ha comido\n" + "==" * 10)
            self.end_game(win=False)
            return

        if tile['pozo']:
            self.log_status("==" * 10 + "\nGAME OVER\n\nCaíste en un pozo\n" + "==" * 10)
            self.end_game(win=False)
            return

        # Comprobar oro
        if tile['oro']:
            self.oro_encontrado = True
            tile['oro'] = False # Recoger el oro
            self.log_status("¡Encontraste el Oro!")
            self.actualiza_sensaciones()
        

        # Comprobar victoria
        if self.oro_encontrado and self.jugador_pos == POS_INICIAL:
            self.log_status("==" * 10 + "\n¡FELICIDADES!\n\nEscapaste con el oro\n" + "==" * 10)
            self.end_game(win=True)
            return

        # Si sigues vivo, reporta sensaciones y actualiza
        self.reporta_sensaciones()
        self.actualiza_interfaz()

    def disparar(self, dr: int, dc: int):

        if self.game_over: return
        if not self.flecha:
            self.log_status("¡Ya no tienes flechas!\n")
            return

        self.flecha = False
        self.log_status("Disparas la flecha...\n")

        r, c = self.jugador_pos
        # Simular trayectoria de la flecha
        while True:
            r, c = r + dr, c + dc
            
            # Si golpea pared
            if not (0 <= r < CUADRICULA and 0 <= c < CUADRICULA):
                self.log_status("La flecha golpea una pared y se pierde\n")
                return

            # Si golpea Wumpus
            if self.tablero[r][c]['wumpus'] and self.wumpus_vive:
                self.wumpus_vive = False
                self.log_status("¡¡¡GRRRRAAAAA!!!\nMataste al Wumpus\n")
                self.actualiza_sensaciones()
                self.actualiza_interfaz()
                return

    def end_game(self, win: bool): #Muestra todos los elementos del tablero
        self.game_over = True
        
        for r in range(CUADRICULA):
            for c in range(CUADRICULA):
                self.tablero[r][c]['visitado'] = True
        
        self.actualiza_interfaz()
        

# Ejecución Principal 
if __name__ == "__main__":
    root = tk.Tk()
    app = WumpusWorldGUI(root)
    root.mainloop()