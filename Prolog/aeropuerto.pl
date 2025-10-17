% Hechos dinamicos
:- dynamic en/2.
:- dynamic dentro/2.

carga(c1).
carga(c2).
aeropuerto(mex).
aeropuerto(oax).
avion(a1).
avion(a2).

%Estado inicial
en(c1, mex).
en(c2, oax).
en(a1, mex).
en(a2, oax).

cargar(C, Av, Aerop) :-
    carga(C),
    avion(Av),
    aeropuerto(Aerop),
    en(C, Aerop),       % La carga esta en el aeropuerto
    en(Av, Aerop),      % El avion esta en el aeropuerto
    % Efectos
    retract(en(C, Aerop)), % La carga NO esta en el aeropuerto
    assert(dentro(C, Av)), % La carga esta DENTRO del avion

    write(C), write(' ha sido cargado en '), write(Av), nl.

descargar(C, Av, Aerop) :-
    carga(C),
    avion(Av),
    aeropuerto(Aerop),
    dentro(C, Av),     % La carga esta DENTRO del avion
    en(Av, Aerop),     % El avion esta en el aeropuerto
    % Efectos
    retract(dentro(C, Av)), % La carga NO esta dentro del avion
    assert(en(C, Aerop)),   % La carga esta en el aeropuerto

    write(C), write(' ha sido descargada en el aeropuerto '), write(Aerop), nl.

volar(Av, Origen, Destino) :-
    avion(Av),
    aeropuerto(Origen),
    aeropuerto(Destino),
    en(Av, Origen),
    % Efectos
    retract(en(Av, Origen)), % El avion NO esta en el origen
    assert(en(Av, Destino)), % EL avion esta en el destino

    write(Av), write(' ha volado de '), write(Origen), write(' a '), write(Destino), nl.

% Reinicia el estado de la simulacion
inicializar :-
    % Eliminar todos los hechos dinamicos actuales
    retractall(en(_, _)),
    retractall(dentro(_, _)),

    % Restaura el estado inicial
    assert(en(c1, mex)),
    assert(en(c2, oax)),
    assert(en(a1, mex)),
    assert(en(a2, oax)),

    write('Simulaci�n inicializada.'), nl.
