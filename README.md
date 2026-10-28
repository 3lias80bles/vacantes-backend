# Vacantes App - Backend

Backend de Vacantes App, desarrollado con Python y Flask.
Este proyecto se encarga de gestionar la lógica del sistema y
la comunicación con la base de datos SQL.

## Tecnologías

- Python
- Flask
- SQLAlchemy
- Flask-Migrate

## Requisitos

Antes de comenzar, es necesario tener instalado:

- Git
- Python 3
- pip
- venv

El motor de base de datos y su controlador se configurarán
de acuerdo con las necesidades del proyecto.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/3lias80bles/vacantes-backend.git
```

Entrar en la carpeta del proyecto:

```bash
cd vacantes-backend
```

### 2. Crear un entorno virtual

```bash
python3 -m venv venv
```

### 3. Activar el entorno virtual

En Linux:

```bash
source venv/bin/activate
```

En Windows (CMD):

```cmd
venv\Scripts\activate.bat
```

En Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configurar las variables de entorno

Copiar `.env.example` como `.env` y establecer `DATABASE_URL` con la
URL de conexión de PostgreSQL. La aplicación carga automáticamente
`.env` al iniciar.

No compartir contraseñas ni credenciales en GitHub.

### 6. Ejecutar la aplicación

Si el punto de entrada es `app.py`:

```bash
python app.py
```

La dirección local dependerá de la configuración de Flask.
Por defecto, suele ser:

http://127.0.0.1:5000

## Estructura del proyecto

```text
vacantes-backend/
├── app/
│   ├── routes/
│   ├── models/
│   └── services/
├── tests/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Trabajo en equipo

Antes de comenzar a trabajar, actualizar los cambios:

```bash
git pull
```

¡¡¡¡¡¡¡¡¡¡SI LLEGASTE HASTA AQUI, PLATICAREMOS COMO SE TRABAJARAN LOS CAMBIOS EN EL EQUIPO!!!!!!!!! 


Crear una rama para cada nueva funcionalidad:

```bash
git switch -c feature/nombre-funcionalidad
```

Después de realizar los cambios:

```bash
git add .
git commit -m "feat: descripcion del cambio"
git push -u origin feature/nombre-funcionalidad
```

Integrar los cambios mediante un Pull Request en GitHub.

## Estado del proyecto

En desarrollo.