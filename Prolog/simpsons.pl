% --- HECHOS ---

% Se designan los padres de cada integrante
padre(homero, maggie).
padre(homero, lisa).
padre(homero, bart).
padre(clancy, marge).
padre(abraham, homero).
padre(abraham, herb).
padre(abraham, abbey).

% Se designan las madres de cada integrante
madre(marge, maggie).
madre(marge, lisa).
madre(marge, bart).
madre(jacqueline, marge).
madre(jacqueline, selma).
madre(jacqueline, patty).
madre(mona, homero).

% --- REGLAS ---

% Progenitor (Padre o Madre)
% P es progenitor de H si es su padre O su madre
progenitor(P, H) :- padre(P, H).
progenitor(P, H) :- madre(P, H).

% Abuelos
% A es abuelo o abuela de N si A es padre de P y P es progenitor de N
abuelo(A, N) :-
    padre(A, P),
    progenitor(P, N).

abuela(A, N) :-
    madre(A, P),
    progenitor(P, N).

esAbuelo(A) :- abuelo(A, _); abuela(A, _).


% Hermanos
% H1 es hermano de H2 si P es progenitor de H1 y H2 y si H1 es diferente de H2
sonHermanos(H1, H2) :-
    progenitor(P, H1),
    progenitor(P, H2),
    H1 \= H2.

tieneHermanos(H) :- sonHermanos(H, _).


% Tíos
% T es tio de S si T es hermano de P y P es progenitor de S
tio(T, S) :-
    sonHermanos(T, P),
    progenitor(P, S).

esTio(T) :- tio(T, _).