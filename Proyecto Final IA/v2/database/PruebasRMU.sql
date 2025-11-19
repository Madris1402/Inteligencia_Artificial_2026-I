use horarios;

show tables;

desc grupos;
desc horarios_grupo;
desc materias;
desc profesores;
desc salones;

select * from grupos;
select * from horarios_grupo;
select * from materias;
select * from profesores;
select * from salones;

select m.nombre materia, m.semestre, concat_ws(' ', p.paterno, p.materno, p.nombre) profesor, s.nombre salon, turno, grupo, dia_semana, 
	concat_ws(' - ', hora_inicio, hora_fin) horario
from grupos g
join materias m
	on m.id_materia = g.id_materia
join profesores p
	on p.id_profesor = g.id_profesor
join salones s
	on  s.id_salon = g.id_salon
join horarios_grupo h
	on h.id_grupo = g.id_grupo
	where grupo = 1357
    order by grupo, horario asc;
    
        
        
select id_profesor, upper(concat_ws(' ', p.paterno, p.materno, p.nombre)) profesor from profesores p;

select id_materia, clave from materias;

select id_salon, nombre from salones;
    

