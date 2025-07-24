@ -0,0 +1,119 @@
# MELI Supabase Test

Aplicación web desarrollada con Flask y Supabase para buscar y visualizar información de usuarios en una base de datos.

## 🚀 Características

- Interfaz web amigable para buscar usuarios
- Autocompletado de búsquedas
- Visualización detallada de información de usuarios
- Generación de códigos QR para perfiles de usuario
- Descarga de códigos QR generados
- Integración con Supabase como base de datos
- API RESTful para consultas programáticas
- Paginación de resultados
- Manejo de errores y logs detallados

## 🛠️ Requisitos Previos

- Python 3.8 o superior
- Cuenta de Supabase
- Variables de entorno configuradas para la conexión a Supabase

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd meli_supa_test
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_KEY=tu_clave_de_api_supabase
   ```

## 🏃 Ejecución

Para iniciar la aplicación en modo desarrollo:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:3000`

## 🌐 Endpoints de la API

### Prueba de conexión
- `GET /api/test` - Verifica la conexión con Supabase

### Tablas
- `GET /api/tables` - Lista todas las tablas disponibles
- `GET /api/table/<table_name>` - Obtiene datos de una tabla específica con paginación
  - Parámetros: 
    - `page` (opcional): Número de página (por defecto: 1)
    - `per_page` (opcional): Elementos por página (por defecto: 20)

### Búsqueda
- `GET /` o `/buscar` - Interfaz de búsqueda web
- `GET /sugerir` - Sugerencias de autocompletado
  - Parámetros:
    - `q`: Término de búsqueda

### Usuarios
- `GET /api/usuario/<uuid_segment>` - Redirige al perfil de usuario usando un segmento de UUID (primeros 8 caracteres)
- `GET /api/usuario/<uuid_segment>/qr` - Genera un código QR para el perfil de usuario
  - Parámetros:
    - `format` (opcional): Formato de salida (`png` o `json`, por defecto: `png`)
    - `scale` (opcional): Tamaño del QR (por defecto: 5)

## 🏗️ Estructura del Proyecto

```
meli_supa_test/
├─ app.py                 # Aplicación principal de Flask
├─ supabase_client.py     # Cliente de Supabase
├─ data_tables_supabase.py # Funciones para manejar tablas de datos
├─ buscador.py            # Lógica de búsqueda
├─ qr_code/               # Módulo para generación de códigos QR
│   └─ generator.py      # Generador de códigos QR con segno
├─ services/
│   └─ user_service.py   # Servicio para operaciones de usuario
├─ templates/
│   └─ buscar.html       # Plantilla de la interfaz web
├─ docs/                  # Documentación del proyecto
│   ├─ README.md         # Documentación principal
│   └─ OBJ_14042025.md   # Planificación de funcionalidad QR
└─ requirements.txt       # Dependencias del proyecto
```

## 🔒 Variables de Entorno

| Variable        | Descripción                                  | Requerido |
|----------------|---------------------------------------------|-----------|
| SUPABASE_URL   | URL de tu proyecto Supabase                 | Sí        |
| SUPABASE_KEY   | Clave de API de Supabase                    | Sí        |
| FLASK_ENV      | Entorno de Flask (development/production)    | No        |
| FLASK_DEBUG    | Modo debug (1 para activar)                 | No        |


## 🛠️ Dependencias Principales

- Flask - Framework web
- python-dotenv - Manejo de variables de entorno
- supabase - Cliente de Python para Supabase

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, lee nuestras pautas de contribución antes de enviar un pull request.

## 📧 Contacto

Para consultas o soporte, por favor contacta al equipo de desarrollo.