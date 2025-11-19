from models.materia import Materia
from controllers.generador import GeneradorHorarios

def menuSeleccion():
    """Menú para seleccionar el turno"""
    print("\n" + "="*60)
    print("SELECCIÓN DE TURNO")
    print("="*60)
    print("\n1. Solo Matutino")
    print("2. Solo Vespertino")
    print("3. Ambos turnos (Mixto)")
    
    while True:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            return 'Matutino'
        elif opcion == '2':
            return 'Vespertino'
        elif opcion == '3':
            return 'Ambos'
        else:
            print("Opción inválida. Intenta de nuevo.")

def probarSeleccion():
    """Prueba el generador con selección de turnos"""
    
    print("\n" + "="*80)
    print("GENERADOR DE HORARIOS - SELECCIÓN DE TURNOS")
    print("="*80 + "\n")
    
    # 1. Seleccionar semestre
    semestre = int(input("Ingresa el semestre (1-9, o 10 para optativas): "))
    
    # 2. Seleccionar turno
    turno_seleccionado = menuSeleccion()
    
    # 3. Margen de error
    margen_error = int(input("\nMargen de error en minutos (0 para estricto): "))
    
    # 4. Obtener materias
    print(f"\nObteniendo materias del semestre {semestre}...")
    
    if semestre >= 6:
        materias_dict = Materia.obtenerSemestreOptativa(semestre)
        materias = materias_dict['regulares'] + materias_dict['optativas']
    else:
        materias = Materia.obtenerPorSemestre(semestre)
    
    if not materias:
        print("No hay materias en ese semestre")
        return
    
    print(f"\n✓ Materias disponibles:")
    for i, mat in enumerate(materias, 1):
        tipo = "OPTATIVA" if mat.semestre == 10 else f"Semestre {mat.semestre}"
        print(f"  {i}. [{tipo}] {mat}")
    
    # 5. Seleccionar materias (simple: las primeras 3)
    num_materias = min(3, len(materias))
    materias_seleccionadas = materias[:num_materias]
    ids_materias = [mat.id_materia for mat in materias_seleccionadas]
    
    print(f"\n🎯 Materias seleccionadas:")
    for mat in materias_seleccionadas:
        print(f"  - {mat}")
    
    # 6. Generar horarios
    print(f"\nConfiguración:")
    print(f"   Turno: {turno_seleccionado}")
    print(f"   Margen de error: {margen_error} minutos")
    
    generador = GeneradorHorarios()
    horarios_validos = generador.generar(
        ids_materias, 
        turno_seleccionado, 
        limite=10,
        margen_error=margen_error
    )
    
    # 7. Mostrar resultados
    if horarios_validos:
        print(f"\nSe generaron {len(horarios_validos)} opciones\n")
        
        # Separar por tipo
        sin_empalme = [h for h in horarios_validos if not h['tiene_advertencia']]
        con_empalme = [h for h in horarios_validos if h['tiene_advertencia']]
        
        print(f"Sin empalme: {len(sin_empalme)}")
        print(f"Con empalme: {len(con_empalme)}")
        
        # Analizar turnos en los horarios generados
        if turno_seleccionado == 'Ambos':
            print("\nAnálisis de turnos en las opciones:")
            
            for i, opcion in enumerate(horarios_validos, 1):
                turnos_usados = set()
                for grupo in opcion['combinacion']:
                    turnos_usados.add(grupo.turno)
                
                if len(turnos_usados) == 2:
                    print(f"   Opción {i}: MIXTO (Matutino + Vespertino)")
                elif 'Matutino' in turnos_usados:
                    print(f"   Opción {i}: Solo Matutino")
                else:
                    print(f"   Opción {i}: Solo Vespertino")
        
        # Mostrar las primeras 2 opciones detalladamente
        print("\n" + "="*80)
        print("MOSTRANDO PRIMERAS 2 OPCIONES")
        print("="*80)
        
        for i, opcion in enumerate(horarios_validos[:10], 1):
            print(f"\n{'='*80}")
            print(f"OPCIÓN {i}")
            
            # Analizar turnos de esta opción
            turnos_en_opcion = set()
            for grupo in opcion['combinacion']:
                turnos_en_opcion.add(grupo.turno)
            
            if len(turnos_en_opcion) == 2:
                print("Horario MIXTO")
            elif 'Matutino' in turnos_en_opcion:
                print("Horario MATUTINO")
            else:
                print("Horario VESPERTINO")
            
            if opcion['tiene_advertencia']:
                print(f"  empalme de {opcion['minutos_empalme']} minutos")
            else:
                print("✓ Sin conflictos")
            
            print('='*80)
            
            # Resumen general
            print(generador.obtenerResumenHorario(opcion))
            
            # Vista por días
            generador.imprimirHorarioDia(opcion)
            
            if i < len(horarios_validos[:10]):
                input("\nPresiona Enter para ver la siguiente opción...")
    else:
        print("\nNo se encontraron horarios válidos")
        print("   Posibles causas:")
        print("   - No hay suficientes grupos en el turno seleccionado")
        print("   - Todos los horarios tienen conflictos")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    probarSeleccion()