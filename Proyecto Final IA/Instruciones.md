### Pasos para la instalación del Programa
1. Ejecutar los archivos horarios.sql e insert_horarios.sql de la carpeta database en MySQL.

2. Generar un archivo .env en la carpeta raíz del programa con la siguiente estructura:

```python
# Configuración de la base de datos MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña #Cambiar por la contraseña del usuario
DB_NAME=horarios
DB_PORT=3306
```

3. Instalar las siguientes librerías de Python:

`pip install mysql-connector-python` || Conexión a la base de datos
`pip install python-dotenv` || Manejo de archivo .env (variables de entorno)
`pip install reportlab` || Exportación del horario en PDF
