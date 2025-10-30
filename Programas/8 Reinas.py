# Constante para el tamaño del tablero (8x8)
N = 8

def imprimir_tablero(tablero): # Función para imprimir el tablero

    for fila in range(N):
        linea = ""
        for col in range(N):
            if tablero[fila] == col:
                linea += "Q "
            else:
                linea += ". "
        print(linea)
    print("\n" + "=" * (N * 2) + "\n")

def es_seguro(tablero, fila_actual, col_actual): # Función para verificar si se puede colocar una reina

    # Iteramos sobre las filas del tablero (1 a N)
    for fila_a_revisar in range(N):

        # No nos comparamos con la posición actual que estamos probando
        if fila_a_revisar == fila_actual:
            continue

        # Saltamos filas que no tienen una reina puesta.
        col_existente = tablero[fila_a_revisar]
        if col_existente == -1:
            continue

        # Verificar si hay otra reina en la misma columna
        if col_existente == col_actual:
            return False

        # Verificar si hay otra reina en la misma diagonal
        if abs(col_existente - col_actual) == abs(fila_a_revisar - fila_actual):
            return False

    # Si pasó todas las revisiones contra todas las otras reinas, es seguro
    return True

def resolver_recursivo(tablero, fila_actual, lista_soluciones, fila_fija):

    # Caso Base
    if fila_actual == N:
        lista_soluciones.append(tablero[:])
        return

    # Si la fila actual es la que el usuario ya fijó, la saltamos y pasamos a la siguiente.
    if fila_actual == fila_fija:
        resolver_recursivo(tablero, fila_actual + 1, lista_soluciones, fila_fija)
        return

    # Caso Recursivo
    # Intentar colocar una reina en cada columna de la fila actual
    for col in range(N):

        if es_seguro(tablero, fila_actual, col):

            tablero[fila_actual] = col

            resolver_recursivo(tablero, fila_actual + 1, lista_soluciones, fila_fija)

            # Hacemos "backtrack" limpiando la casilla para la siguiente iteración del bucle 'for'.
            tablero[fila_actual] = -1


def resolver_8_reinas(fila_fija, col_fija):

    soluciones = []
    tablero = [-1] * N

    # Colocamos la reina del usuario
    tablero[fila_fija] = col_fija

    # Empezamos el proceso recursivo desde la fila 1
    resolver_recursivo(tablero, 0, soluciones, fila_fija)

    return soluciones

# Punto de Entrada Principal
if __name__ == "__main__":

    #  OBTENER FILA
    fila_elegida = -1
    while fila_elegida < 0 or fila_elegida >= N:
        try:
            entrada = input(f"¿En qué fila (1-{N}) quieres colocar la primera reina? ")
            fila_elegida = int(entrada) - 1 # Convertir a índice 0

            if fila_elegida < 0 or fila_elegida >= N:
                print(f"Error: El número debe estar entre 1 y {N}.")
        except ValueError:
            print("Error: Por favor, introduce un número válido.")

    #  OBTENER COLUMNA
    col_elegida = -1
    while col_elegida < 0 or col_elegida >= N:
        try:
            entrada = input(f"¿En qué columna (1-{N}) quieres colocar la reina (en la fila {fila_elegida + 1})? ")
            col_elegida = int(entrada) - 1 # Convertir a índice 0

            if col_elegida < 0 or col_elegida >= N:
                print(f"Error: El número debe estar entre 1 y {N}.")
        except ValueError:
            print("Error: Por favor, introduce un número válido.")

    print(f"\nBuscando soluciones con la reina fija en la posición (Fila {fila_elegida + 1}, Columna {col_elegida + 1})...\n")

    soluciones_encontradas = resolver_8_reinas(fila_elegida, col_elegida)

    if soluciones_encontradas:
        print(f"Se encontraron {len(soluciones_encontradas)} soluciones.")
        print("Mostrando las primeras 5 (si existen):\n")
        print("==============================================")

        for i, sol in enumerate(soluciones_encontradas[:5], start=1):
            print(f"Solución {i} (Reina en Fila {fila_elegida + 1}, Columna {col_elegida + 1})\n")
            imprimir_tablero(sol)

        if len(soluciones_encontradas) > 5:
            print(f"... y {len(soluciones_encontradas) - 5} soluciones más.")
    else:
        print(f"No se encontró ninguna solución con la reina en (Fila {fila_elegida + 1}, Columna {col_elegida + 1}).")