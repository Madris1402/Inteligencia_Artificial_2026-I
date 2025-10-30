import pygame
import numpy as np
import time

# Configuración de Pygame 
ANCHO, ALTO = 800, 600 #Tamaño de la ventana
FPS = 8

# Configuración del Juego de la Vida 
TAM_CELULA = 10        #Tamaño en píxeles de cada célula (cuadrado)
NUM_CELDAS_ANCHO = ANCHO // TAM_CELULA
NUM_CELDAS_ALTO = ALTO // TAM_CELULA

#Colores
COLOR_FONDO = (25, 25, 25)
COLOR_CELULA_VIVA = (128, 128, 255)
COLOR_LINEA_CUADRICULA = (40, 40, 40)

# Inicialización de Pygame 
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de la Vida de Conway")
reloj = pygame.time.Clock()

# Funciones

def inicializar_tablero_aleatorio(): # Crea un tablero inicial con células vivas (1) o muertas (0) al azar.
    return np.random.randint(0, 2, size=(NUM_CELDAS_ALTO, NUM_CELDAS_ANCHO))

def dibujar_tablero(pantalla, tablero): # Dibuja todas las células y la cuadrícula en la pantalla.
    pantalla.fill(COLOR_FONDO) #Limpia la pantalla con el color de fondo

    for fila in range(NUM_CELDAS_ALTO):
        for col in range(NUM_CELDAS_ANCHO):
            #Dibuja la célula
            if tablero[fila, col] == 1:
                pygame.draw.rect(pantalla, COLOR_CELULA_VIVA, 
                                 (col * TAM_CELULA, fila * TAM_CELULA, TAM_CELULA, TAM_CELULA))
            
            #Dibuja la cuadrícula
            pygame.draw.rect(pantalla, COLOR_LINEA_CUADRICULA, 
                             (col * TAM_CELULA, fila * TAM_CELULA, TAM_CELULA, TAM_CELULA), 1)

def actualizar_tablero(tablero_actual):
    
    #Crear una copia del tablero para almacenar el nuevo estado.
    nuevo_tablero = np.copy(tablero_actual)

    for fila in range(NUM_CELDAS_ALTO):
        for col in range(NUM_CELDAS_ANCHO):
            
            #Creamos una 'ventana' de 3x3 alrededor de la célula actual, manejando los bordes
            total_vecinos_vivos = int((tablero_actual[
                max(0, fila - 1): min(NUM_CELDAS_ALTO, fila + 2),
                max(0, col - 1): min(NUM_CELDAS_ANCHO, col + 2)
            ]).sum() - tablero_actual[fila, col]) #Restamos la propia célula si estaba viva

            #Aplicar las reglas del juego
            if tablero_actual[fila, col] == 1: #Célula viva
                if total_vecinos_vivos < 2 or total_vecinos_vivos > 3:
                    nuevo_tablero[fila, col] = 0 #Muere
            else: #Célula muerta
                if total_vecinos_vivos == 3:
                    nuevo_tablero[fila, col] = 1 #Revive

    return nuevo_tablero

# Bucle Principal

tablero = inicializar_tablero_aleatorio()
ejecutando = True
pausado = False #Estado de la simulación

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE: #Espacio para Pausar
                pausado = not pausado
                print("Pausa" if pausado else "Reanudar")
            if evento.key == pygame.K_r: # Tecla R para Reiniciar el Juego
                tablero = inicializar_tablero_aleatorio()
                pausado = False 
                print("Tablero Reiniciado")
            if evento.key == pygame.K_c: # Tecla C para Limpiar el Tablero
                tablero = np.zeros((NUM_CELDAS_ALTO, NUM_CELDAS_ANCHO)) # Crear un tablero vacío
                pausado = True  # Entrar a modo Dibuijo
                print("Tablero Borrado")
        
        if evento.type == pygame.MOUSEBUTTONDOWN and pausado: #Solo dibujar si está pausado
            x, y = evento.pos
            col = x // TAM_CELULA
            fila = y // TAM_CELULA
            
            #Asegurarse de que el clic está dentro del tablero
            if 0 <= fila < NUM_CELDAS_ALTO and 0 <= col < NUM_CELDAS_ANCHO:
                #Alternar el estado de la célula
                tablero[fila, col] = 1 - tablero[fila, col] 

    # Lógica de Actualización y Dibujo 
    if not pausado:
        tablero = actualizar_tablero(tablero)
    
    dibujar_tablero(pantalla, tablero)
    pygame.display.flip() #Actualiza la pantalla completa
    
    reloj.tick(FPS) #Controla la velocidad de la simulación

pygame.quit()