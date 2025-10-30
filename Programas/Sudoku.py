import random

# Constante para el tamaño (9x9)
N = 9

def imprimir_tablero(tablero): # Función para imprimir el tablero

    for i in range(N):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - ")

        for j in range(N):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                # Imprime el número o un punto si es 0
                print(tablero[i][j] if tablero[i][j] != 0 else ".")
            else:
                print(str(tablero[i][j] if tablero[i][j] != 0 else ".") + " ", end="")
    print("\n" + "=-"*12 + "=\n")


def encontrar_vacio(tablero):
    
    for i in range(N):
        for j in range(N):
            if tablero[i][j] == 0:
                return (i, j)  # Devuelve tupla (fila, columna)
    return None

def es_valido(tablero, num, pos): # Verifica si el num es válido en la posición

    fila, col = pos

    # Verificar la fila
    for j in range(N):
        if tablero[fila][j] == num:
            return False

    # Verificar la columna
    for i in range(N):
        if tablero[i][col] == num:
            return False

    # Verificar la caja 3x3
    # Encontrar la esquina superior izquierda de la caja
    inicio_fila_caja = (fila // 3) * 3
    inicio_col_caja = (col // 3) * 3

    for i in range(inicio_fila_caja, inicio_fila_caja + 3):
        for j in range(inicio_col_caja, inicio_col_caja + 3):
            if tablero[i][j] == num:
                return False

    # Si pasa las 3 pruebas, es válido
    return True

def resolver_sudoku(tablero):

    # Caso Base
    vacio = encontrar_vacio(tablero)
    if not vacio:
        return True  # ¡Solución encontrada!

    fila, col = vacio

    # Caso Recursivo
    for num in range(1, 10):
        # Probar
        if es_valido(tablero, num, (fila, col)):

            # Colocar
            tablero[fila][col] = num

            # Llamada recursiva
            if resolver_sudoku(tablero):
                return True

            # Backtrack
            tablero[fila][col] = 0

    # Si ningún número del 1 al 9 funcionó, retornar False
    return False


# Generador de Sudokus usando random para generar soluciones diferentes
def generar_solucion(tablero):

    vacio = encontrar_vacio(tablero)
    if not vacio:
        return True

    fila, col = vacio

    # Revolver los números
    numeros_aleatorios = random.sample(range(1, 10), 9)

    for num in numeros_aleatorios:
        if es_valido(tablero, num, (fila, col)):
            tablero[fila][col] = num
            if generar_solucion(tablero):
                return True
            tablero[fila][col] = 0

    return False

def generar_sudoku(casillas_a_quitar):

    # Empezar con un tablero vacío
    tablero = [[0 for _ in range(N)] for _ in range(N)]

    # Generar una solución completa aleatoria
    generar_solucion(tablero)

    # Perforar agujeros
    agujeros_hechos = 0
    while agujeros_hechos < casillas_a_quitar:
        fila = random.randint(0, 8)
        col = random.randint(0, 8)

        # Solo quitar si la casilla no está ya vacía
        if tablero[fila][col] != 0:
            tablero[fila][col] = 0
            agujeros_hechos += 1

    return tablero

# Programa Principal

if __name__ == "__main__":

    # Definir dificultad (cuántas casillas quitar)
    # Fácil: ~30-35
    # Medio: ~40-45
    # Difícil: ~50-55

    Selector = """
    Seleccione la dificultad:
    Fácil (Presionar 1)
    Medio (Presionar 2)
    Difícil (Presionar 3)
    """
    dif_input = int(input(Selector))
    dificultad = (dif_input * 15) + 15

    # Convertir el valor a texto para la interfaz
    if dif_input == 1:
        txt_dif = "Fácil"
    elif dif_input == 2:
        txt_dif = "Medio"
    else:
        txt_dif = "Difícil"

    # Evitar que la dificultad sea superior a 55 o menor a 30
    if dificultad < 30:
        dificultad = 30
    elif dificultad > 55:
        dificultad = 55

    print(f"\nGenerando un nuevo Sudoku de dificultad: {txt_dif}\n")

    mi_puzle = generar_sudoku(dificultad)

    print("=-=-= SUDOKU GENERADO =-=-= \n")
    imprimir_tablero(mi_puzle)

    input("Presiona Enter para ver la solución...")

    # Resolver
    if resolver_sudoku(mi_puzle):
        print("=-=-= SOLUCIÓN =-=-=\n")
        imprimir_tablero(mi_puzle)
    else:
        print("Error: El puzle generado no tiene solución.")