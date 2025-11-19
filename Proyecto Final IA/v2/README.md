# GeneradorHorarios
Aplicación para generar varios horarios escolares con distintos filtros.

Para establecer la conexión a la base de datos se debe crear un archivo `.env` en la raíz del proyecto (mismo nivel que horarios.py)

```
# Configuración de la base de datos MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=horarios
DB_PORT=3306
```

## Librerías utilizadas:
- `pip install mysql-connector-python` - Conexión a la base de datos
- `pip install python-dotenv` - Manejo de archivo .env (variables de entorno)
- `pip install reportlab` - Exportación del horario en PDF