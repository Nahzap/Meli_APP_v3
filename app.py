import logging
from flask import Flask, render_template, request, jsonify, url_for, redirect, send_file, session, g
from datetime import datetime
import io
import os
from dotenv import load_dotenv
from data_tables_supabase import list_tables, get_table_data
from supabase_client import db
from buscador import NavegadorSupabase
from qr_code.generator import QRGenerator
import segno
from io import BytesIO
import base64

# Load environment variables
load_dotenv()

# Desactivar logs de hpack y httpcore
logging.getLogger('hpack').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'meliapp-secret-key-change-in-production')

# Filtro para formatear fechas en las plantillas
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if value is None:
        return ""
    if isinstance(value, str):
        # Si es un string, intentar convertirlo a datetime
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    return value.strftime(format)

app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para mensajes flash

# Configuración
DEBUG = False  # Siempre False para producción
PORT = int(os.environ.get('PORT', 3000))

# Configuración para producción
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.json.sort_keys = False

# ====================
# Funciones de autenticación
# ====================

def login_required(f):
    """
    Decorador que requiere que el usuario esté autenticado.
    Si no está autenticado, redirige a la página de login.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_current_user():
    """
    Carga la información del usuario actual en g.user para todas las peticiones.
    Mapea el UUID de autenticación al UUID de la tabla usuarios.
    """
    g.user = None
    if 'user_id' in session:
        auth_user_id = session.get('user_id')
        
        # Obtener el UUID de la tabla usuarios
        user_uuid = None
        try:
            response = db.client.table('usuarios').select('id').eq('auth_user_id', auth_user_id).maybe_single().execute()
            if hasattr(response, 'data') and response.data:
                user_uuid = response.data['id']
        except Exception as e:
            logger.error(f"Error al mapear auth_user_id a user_uuid: {str(e)}")
        
        g.user = {
            'id': auth_user_id,  # UUID de autenticación
            'user_uuid': user_uuid,  # UUID de la tabla usuarios
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }

# ====================

# ====================
# Endpoints de la API
# ====================

@app.route('/api/test', methods=['GET'])
def test_connection_endpoint():
    """
    Prueba la conexión con la base de datos Supabase.
    
    GET /api/test
    """
    try:
        success, message = test_supabase_connection()
        return jsonify({"success": success, "message": message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/table/<table_name>', methods=['GET'])
def get_table_data_endpoint(table_name):
    """
    Obtiene datos de una tabla específica con paginación.
    
    GET /api/table/<table_name>?page=1&per_page=20
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        success, result = get_table_data(table_name, page, per_page)
        
        if success:
            return jsonify({
                "success": True,
                "table": table_name,
                "data": result['data'],
                "pagination": result['pagination']
            })
        else:
            return jsonify({"success": False, "error": result}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tables', methods=['GET'])
def list_tables_endpoint():
    """
    Lista todas las tablas disponibles en la base de datos.
    
    GET /api/tables
    """
    try:
        success, result = list_tables()
        if success:
            return jsonify({"success": True, "tables": result})
        else:
            return jsonify({"success": False, "error": result}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/gestionar-lote', methods=['POST'])
def manejar_lote_de_miel():
    """
    Endpoint para crear o actualizar un lote de miel.
    Actúa como un proxy seguro a la Edge Function de Supabase 'Honey_Manage_Lots'.
    
    POST /api/gestionar-lote
    
    Body JSON:
    {
        "usuario_id": "uuid-del-usuario",
        "ubicacion_id": "uuid-de-la-ubicacion",
        "temporada": "2024-2025",
        "kg_producidos": 150.5,
        "descripcion_general": "Miel de flores silvestres",
        "composicion_polen": "flores-silvestres-80%|eucalipto-20%"
    }
    
    Returns:
    {
        "success": true,
        "loteId": "uuid-del-lote-creado"
    }
    """
    try:
        # Obtener los datos JSON enviados en la solicitud
        datos_lote = request.get_json()
        
        if not datos_lote:
            return jsonify({
                "success": False, 
                "error": "No se proporcionaron datos en la solicitud."
            }), 400

        # Validar campos requeridos
        campos_requeridos = ['usuario_id', 'ubicacion_id', 'temporada', 'kg_producidos']
        for campo in campos_requeridos:
            if campo not in datos_lote:
                return jsonify({
                    "success": False, 
                    "error": f"Campo requerido faltante: {campo}"
                }), 400

        # Invocar la Edge Function 'Honey_Manage_Lots' con los datos recibidos
        resultado = db.invoke_edge_function_sync('Honey_Manage_Lots', datos_lote)
        
        # Verificar si hay error en la respuesta
        if 'error' in resultado:
            return jsonify({
                "success": False,
                "error": resultado.get('error', 'Error desconocido en la Edge Function')
            }), 400

        # Devolver la respuesta exitosa
        return jsonify({
            "success": True,
            "loteId": resultado.get('loteId'),
            "data": resultado
        }), 200

    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": f"Error de validación: {str(ve)}"
        }), 400
    except Exception as e:
        # Manejar cualquier error que ocurra durante el proceso
        app.logger.error(f"Error al invocar la Edge Function Honey_Manage_Lots: {e}")
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

# ====================
# Rutas de la interfaz web
# ====================

# Inicializar el navegador de Supabase
navegador = NavegadorSupabase(db.client)

@app.route('/', methods=['GET'])
def home():
    """
    Página principal con diseño moderno y llamadas a la acción.
    
    GET /
    """
    return render_template('pages/home.html')

@app.route('/search')
def search():
    """
    Página de búsqueda con el nuevo template.
    """
    return render_template('pages/search.html')

@app.route('/gestionar-lote')
@login_required
def gestionar_lote():
    """
    Página para gestionar lotes de miel con formulario interactivo.
    
    GET /gestionar-lote
    """
    return render_template('pages/gestionar_lote.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Sistema de acceso para usuarios registrados.
    
    GET /login - Muestra el formulario de login
    POST /login - Procesa el login con email y contraseña
    """
    if request.method == 'GET':
        return render_template('pages/login.html')
    
    # Procesar login POST
    try:
        data = request.get_json() or request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email y contraseña son requeridos"}), 400
        
        # Autenticar con Supabase Auth
        auth_response = db.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            return jsonify({"success": False, "error": "Credenciales inválidas"}), 401
        
        user = auth_response.user
        
        # Obtener información adicional del usuario desde info_contacto
        contact_response = db.client.table('info_contacto')\
            .select('id, nombre_completo, nombre_empresa')\
            .eq('usuario_id', user.id)\
            .execute()
        
        contact_info = contact_response.data[0] if contact_response.data else {}
        
        # Crear sesión con datos del usuario autenticado
        session['user_id'] = str(user.id)
        session['user_email'] = user.email
        session['user_name'] = contact_info.get('nombre_completo') or user.user_metadata.get('full_name', user.email)
        session['user_empresa'] = contact_info.get('nombre_empresa', '')
        
        return jsonify({
            "success": True, 
            "message": "Login exitoso",
            "redirect_url": "/"
        })
        
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario actual.
    
    GET /logout
    """
    session.clear()
    return redirect(url_for('login'))

@app.route('/register')
def register():
    """
    Página de registro con opciones de Google OAuth y registro manual.
    
    GET /register
    """
    return render_template('pages/register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """
    API endpoint para registro manual de usuarios.
    
    POST /api/register
    Body: {email, password, fullName, company}
    """
    try:
        data = request.get_json() or request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('fullName', '').strip()
        company = data.get('company', '').strip()
        
        if not email or not password or not full_name:
            return jsonify({"success": False, "error": "Todos los campos son requeridos"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        # Crear usuario con Supabase Auth
        auth_response = db.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "company": company
                }
            }
        })
        
        if not auth_response.user:
            return jsonify({"success": False, "error": "Error al crear usuario"}), 400
        
        user = auth_response.user
        
        # Crear entrada en info_contacto si no existe
        try:
            db.client.table('info_contacto').insert({
                "usuario_id": str(user.id),
                "nombre_completo": full_name,
                "nombre_empresa": company,
                "correo_principal": email
            }).execute()
        except Exception as e:
            logger.warning(f"Error al crear info_contacto: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": "Usuario creado exitosamente",
            "redirect_url": "/login"
        })
        
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        return jsonify({"success": False, "error": "Error al crear cuenta"}), 500

@app.route('/api/auth/google', methods=['POST'])
def api_google_auth():
    """
    API endpoint para iniciar el flujo de autenticación con Google.
    
    POST /api/auth/google
    """
    try:
        # Obtener la URL de redirección para Google OAuth
        auth_response = db.client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": f"{request.url_root}auth/callback"
            }
        })
        
        if auth_response.url:
            return jsonify({
                "success": True,
                "url": auth_response.url
            })
        else:
            return jsonify({"success": False, "error": "Error al generar URL de Google"}), 500
            
    except Exception as e:
        logger.error(f"Error en Google auth: {str(e)}")
        return jsonify({"success": False, "error": "Error al conectar con Google"}), 500

@app.route('/auth/callback')
def auth_callback():
    """
    Callback para manejar el retorno de Google OAuth.
    
    GET /auth/callback
    """
    try:
        code = request.args.get('code')
        if not code:
            return redirect(url_for('register'))
        
        # Intercambiar código por sesión
        auth_response = db.client.auth.exchange_code_for_session(code)
        
        if auth_response.user:
            user = auth_response.user
            
            # Verificar si ya existe en info_contacto
            contact_response = db.client.table('info_contacto')\
                .select('id')\
                .eq('usuario_id', str(user.id))\
                .execute()
            
            if not contact_response.data:
                # Crear entrada en info_contacto
                full_name = user.user_metadata.get('full_name', '')
                company = user.user_metadata.get('company', '')
                
                db.client.table('info_contacto').insert({
                    "usuario_id": str(user.id),
                    "nombre_completo": full_name or user.email,
                    "nombre_empresa": company,
                    "correo_principal": user.email
                }).execute()
            
            # Crear sesión
            session['user_id'] = str(user.id)
            session['user_email'] = user.email
            session['user_name'] = user.user_metadata.get('full_name', user.email)
            session['user_empresa'] = user.user_metadata.get('company', '')
            
            return redirect(url_for('home'))
        else:
            return redirect(url_for('register'))
            
    except Exception as e:
        logger.error(f"Error en callback: {str(e)}")
        return redirect(url_for('register'))

@app.route('/profile/<user_id>')
def profile(user_id):
    """
    Página de perfil público con diseño moderno.
    
    GET /profile/<user_id>
    """
    try:
        # Validar formato UUID o buscar por username
        import uuid
        try:
            # Si es un UUID válido
            uuid.UUID(user_id)
            user_uuid = user_id
            
            # Buscar usuario por UUID exacto
            user_response = navegador.supabase.table('usuarios').select('*').eq('id', user_uuid).execute()
            if not user_response.data:
                return render_template('pages/profile.html', 
                                     error="Usuario no encontrado"), 404
            user_info = user_response.data[0]
            
        except ValueError:
            # Si no es UUID, buscar por username
            if len(user_id) >= 2:
                # Buscar por username (case-insensitive)
                search_response = navegador.supabase.table('usuarios')\
                    .select('*')\
                    .ilike('username', f'%{user_id}%')\
                    .limit(1)\
                    .execute()
                
                if search_response.data:
                    user_info = search_response.data[0]
                    user_uuid = user_info['id']
                else:
                    return render_template('pages/profile.html', 
                                         error="Usuario no encontrado"), 404
            else:
                return render_template('pages/profile.html', 
                                     error="Por favor ingresa al menos 2 caracteres"), 400
        
        # Ahora user_info y user_uuid están definidos
        # Buscar información de contacto
        contact_response = navegador.supabase.table('info_contacto').select('*').eq('usuario_id', user_uuid).execute()
        contact_info = contact_response.data[0] if contact_response.data else {}
        
        # Buscar ubicaciones
        locations_response = navegador.supabase.table('ubicaciones').select('*').eq('usuario_id', user_uuid).execute()
        locations = locations_response.data if locations_response.data else []
        
        # Generar QR
        qr_url = url_for('get_user_qr', uuid_segment=user_uuid[:8], _external=True)
        
        # Preparar datos para la plantilla con columnas correctas
        user_template_data = {
            'id': user_uuid,
            'nombre': user_info.get('username', 'Usuario'),
            'email': contact_info.get('correo_personal', ''),
            'telefono': user_info.get('telefono') or contact_info.get('telefono'),
            'ubicacion': locations[0].get('nombre') if locations else None,
            'descripcion': user_info.get('descripcion', ''),
            'especialidad': user_info.get('role', 'Apicultor'),
            'especialidades': [user_info.get('role')] if user_info.get('role') else [],
            'especialidades_completas': [user_info.get('role')] if user_info.get('role') else [],
            'contacto_completo': contact_info,
            'ubicaciones': locations
        }
        
        return render_template('pages/profile.html', 
                             user=user_template_data,
                             qr_url=qr_url)
                              
    except Exception as e:
        logger.error(f"Error al cargar perfil: {str(e)}", exc_info=True)
        return render_template('pages/profile.html', 
                             error="Error al cargar el perfil"), 500

# Mantener ruta antigua para compatibilidad
@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """
    Ruta de búsqueda que maneja búsquedas por nombre o ID.
    """
    if request.method == 'POST':
        search_term = request.form.get('usuario_id', '').strip()
        if search_term:
            try:
                # Buscar usuario por username o ID
                if len(search_term) >= 2:
                    # Buscar por username (case-insensitive)
                    search_response = navegador.supabase.table('usuarios')\
                        .select('id', 'username', 'role')\
                        .ilike('username', f'%{search_term}%')\
                        .limit(10)\
                        .execute()
                    
                    # Si no se encuentra por username, buscar por ID exacto
                    if not search_response.data:
                        search_response = navegador.supabase.table('usuarios')\
                            .select('id', 'username', 'role')\
                            .eq('id', search_term)\
                            .limit(1)\
                            .execute()
                    
                    if search_response.data:
                        user = search_response.data[0]
                        return redirect(url_for('profile', user_id=user['id']))
                    else:
                        return render_template('pages/search.html', 
                                             error="Usuario no encontrado")
                else:
                    return render_template('pages/search.html', 
                                         error="Por favor ingresa al menos 2 caracteres")
            except Exception as e:
                logger.error(f"Error en búsqueda: {str(e)}")
                return render_template('pages/search.html', 
                                     error="Error al buscar usuario")
    
    return redirect(url_for('search'))

@app.route('/sugerir', methods=['GET'])
def sugerir():
    """
    Endpoint para obtener sugerencias de autocompletado de usuarios.
    
    GET /sugerir?q=<término>
    
    Parámetros:
    - q: Término de búsqueda
    
    Retorna:
    - Lista de usuarios que coinciden con el término de búsqueda
    """
    try:
        termino = request.args.get('q', '').strip()
        if not termino:
            return jsonify({'results': []})
            
        # Obtener sugerencias de usuarios que coincidan con el término de búsqueda
        response = db.client.table('usuarios') \
            .select('id, username, tipo_usuario, status') \
            .ilike('username', f'%{termino}%') \
            .limit(10) \
            .execute()
            
        users = response.data if hasattr(response, 'data') else []
        
        # Formatear resultados para el frontend
        suggestions = [{
            'id': user['id'],
            'nombre': user.get('username', ''),
            'especialidad': user.get('role', 'Apicultor')
        } for user in users]
        
        return jsonify({
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error en /sugerir: {str(e)}", exc_info=True)
        return jsonify({"error": "Error al obtener sugerencias"}), 500

@app.route('/api/test-db', methods=['GET'])
def test_db():
    """
    Prueba la conexión con la base de datos y devuelve información del sistema.
    
    GET /api/test-db
    """
    try:
        # Verificar conexión a Supabase
        response = db.client.table('usuarios').select('count', count='exact').execute()
        return jsonify({
            "conexion": "OK",
            "total_usuarios": response.count if hasattr(response, 'count') else 'N/A',
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Error en /api/test-db: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuario/<uuid_segment>')
def get_usuario_by_uuid_segment(uuid_segment):
    """
    Redirige al perfil del usuario usando el primer segmento de su UUID.
    
    GET /api/usuario/550e8400 -> redirige al perfil del usuario con ID que comience con 550e8400
    """
    try:
        if not uuid_segment or len(uuid_segment) != 8:
            return jsonify({"error": "Formato de segmento UUID inválido. Debe tener 8 caracteres."}), 400
            
        # Convertir a minúsculas para consistencia
        uuid_segment = uuid_segment.lower()
        
        # Obtener todos los usuarios y filtrar localmente
        response = db.client.table('usuarios').select('id').execute()
        
        # Buscar usuario cuyo ID comience con el segmento proporcionado ......... MODIFICAR PARA QUE SEA DIRECTO CON SUPABASE
        matching_users = [user for user in response.data 
                         if user.get('id', '').lower().startswith(uuid_segment)]
        
        if not matching_users:
            return jsonify({"error": f"No se encontró ningún usuario con el ID que comience con {uuid_segment}"}), 404
            
        # Tomar el primer usuario que coincida
        user_id = matching_users[0]['id']
        
        # Redirigir a la página de búsqueda con el ID completo
        return redirect(url_for('buscar', usuario_id=user_id))
        
    except Exception as e:
        logger.error(f"Error al buscar usuario por segmento UUID {uuid_segment}: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/api/usuario/<uuid_segment>/qr')
def get_user_qr(uuid_segment):
    """
    Genera y devuelve un código QR que redirecciona al perfil del usuario.
    
    GET /api/usuario/550e8400/qr?format=png -> Devuelve una imagen PNG del QR
    GET /api/usuario/550e8400/qr?format=svg -> Devuelve una imagen SVG del QR
    GET /api/usuario/550e8400/qr?format=json -> Devuelve un JSON con el QR en base64
    """
    try:
        # Validar formato de UUID
        if not uuid_segment or len(uuid_segment) != 8:
            return jsonify({"error": "Formato de segmento UUID inválido. Debe tener 8 caracteres."}), 400
            
        # Convertir a minúsculas para consistencia
        uuid_segment = uuid_segment.lower()
        
        # Reutilizar la lógica existente para buscar el usuario por UUID segment
        # Buscar usuario cuyo ID comience con el segmento proporcionado
        response = db.client.table('usuarios').select('id').execute()
        
        matching_users = [user for user in response.data 
                        if user.get('id', '').lower().startswith(uuid_segment)]
        
        if not matching_users:
            return jsonify({"error": f"No se encontró ningún usuario con el ID que comience con {uuid_segment}"}), 404
            
        # Obtener el ID completo del usuario
        user_id = matching_users[0]['id']
        
        # Obtener formato solicitado (solo permitimos png y json)
        qr_format = request.args.get('format', 'png')
        scale = int(request.args.get('scale', 5))
        
        # Crear generador QR
        qr_generator = QRGenerator()
        
        # Generar la URL web para el QR (apuntando directamente al perfil del usuario)
        base_url = request.url_root.rstrip('/')
        profile_url = f"{base_url}/profile/{user_id}"
        
        # Generar QR directamente con segno
        qr = segno.make(profile_url, error='m')
        
        if qr_format == 'png':
            # Generar QR en PNG y devolverlo como archivo
            output = io.BytesIO()
            qr.save(output, kind='png', scale=scale)
            output.seek(0)
            return send_file(output, mimetype='image/png', as_attachment=False, download_name=f'qr-{user_id}.png')
        
        elif qr_format == 'json':
            # Generar QR en formato JSON con imagen base64
            output = io.BytesIO()
            qr.save(output, kind='png', scale=scale)
            qr_base64 = base64.b64encode(output.getvalue()).decode('ascii')
            
            return jsonify({
                "success": True,
                "qr_code": f"data:image/png;base64,{qr_base64}",
                "user_id": user_id,
                "uuid_segment": uuid_segment
            })
        else:
            return jsonify({"error": f"Formato '{qr_format}' no soportado. Formatos válidos: png, json"}), 400
            
    except Exception as e:
        logger.error(f"Error al generar QR para usuario con segmento UUID {uuid_segment}: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

# ====================
# Punto de entrada
# ====================

def list_routes():
    """
    Muestra todas las rutas registradas en la aplicación con sus métodos HTTP.
    Agrupadas por categorías para mejor legibilidad.
    """
    # Agrupar rutas por categoría
    api_routes = []
    web_routes = []
    static_routes = []
    
    for rule in app.url_map.iter_rules():
        methods = sorted([m for m in rule.methods if m not in ('OPTIONS', 'HEAD')])
        route_path = str(rule)
        route_info = {
            'endpoint': rule.endpoint,
            'path': route_path,
            'methods': methods
        }
        
        if rule.endpoint == 'static':
            static_routes.append(route_info)
        elif route_path.startswith('/api/'):
            api_routes.append(route_info)
        else:
            web_routes.append(route_info)
    
    # Generar salida formateada
    output = []
    
    # 1. Rutas web
    output.append("\n=== RUTAS WEB ===")
    for route in sorted(web_routes, key=lambda x: x['path']):
        methods = ','.join(route['methods'])
        output.append(f"{route['path']:50} [{methods:10}]")
    
    # 2. Rutas API
    output.append("\n=== RUTAS API ===")
    for route in sorted(api_routes, key=lambda x: x['path']):
        methods = ','.join(route['methods'])
        output.append(f"{route['path']:50} [{methods:10}]")
    
    # 3. Rutas estáticas (opcional, si quieres mostrarlas)
    if static_routes:
        output.append("\n=== RUTAS ESTÁTICAS ===")
        for route in static_routes:
            output.append(f"{route['path']:50} [GET      ]")
    
    return '\n'.join(output)

def print_welcome_message():
    """Muestra un mensaje de bienvenida con información de los endpoints principales."""
    welcome_msg = """
=== MELI SUPABASE TEST ===

ENDPOINTS PRINCIPALES:

[WEB]
/                       - Página principal del buscador
/buscar                 - Buscar usuarios (GET: formulario, POST: resultados)
/sugerir?q=<termino>   - Autocompletado de usuarios

[API]
/api/usuario/<uuid>     - Obtener usuario por segmento de UUID (8 caracteres)
/api/test               - Probar conexión con Supabase
/api/tables             - Listar todas las tablas
/api/table/<tabla>      - Ver datos de una tabla específica
/api/test-db            - Verificar estado de la base de datos

[EJEMPLOS]
http://localhost:3000/api/table/usuarios?page=1&per_page=10
http://localhost:3000/api/usuario/ce27e79e
http://localhost:3000/sugerir?q=nombre
"""
    print(welcome_msg)

def main():
    """Función principal que inicia la aplicación."""
    try:
        # Configurar la codificación de la consola para Windows (solo local)
        import sys
        import io
        
        # Configurar la salida estándar
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
        # Verificar la conexión con Supabase al inicio
        db.test_connection()
        print("\n[OK] Conexión con Supabase establecida correctamente")
        
        # Mostrar rutas detalladas
        print("\n=== RUTAS REGISTRADAS ===")
        print(list_routes())
        
        # Mostrar mensaje de bienvenida
        print_welcome_message()
        
        # Iniciar la aplicación
        print(f"\n🚀 Iniciando servidor en http://127.0.0.1:{PORT}/buscar")
        print("Presiona CTRL+C para salir\n")
        
        # Iniciar la aplicación sin reloader
        app.run(debug=DEBUG, port=PORT, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Error al conectar con Supabase: {str(e)}")
        print("Asegúrate de que las credenciales en el archivo .env sean correctas.")

# Para Vercel, exponemos la app directamente
if __name__ == '__main__':
    main()
