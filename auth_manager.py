"""
Módulo de autenticación y gestión de sesiones de usuario.

Este módulo maneja todo lo relacionado con:
- Registro de usuarios
- Login/logout
- Autenticación con Google OAuth
- Gestión de sesiones
- Decoradores de autenticación
"""

import logging
import secrets
import hashlib
import base64
from functools import wraps
from flask import session, request, redirect, url_for, flash, g, jsonify
import uuid
from datetime import datetime
from supabase_client import db

logger = logging.getLogger(__name__)


class AuthManager:
    """Gestor centralizado de autenticación y sesiones de usuario."""
    
    @staticmethod
    def login_required(f):
        """
        Decorador que requiere que el usuario esté autenticado.
        Si no está autenticado, redirige a la página de login.
        
        Args:
            f: Función a decorar
            
        Returns:
            Función decorada que verifica autenticación
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('web.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def load_current_user():
        """
        Carga la información del usuario actual en g.user para todas las peticiones.
        Mapea el UUID de autenticación al UUID de la tabla usuarios usando la función del searcher.
        """
        g.user = None
        if 'user_id' in session:
            auth_user_id = session.get('user_id')
            
            # Obtener el UUID de la tabla usuarios - método único y eficiente
            user_uuid = auth_user_id  # Por defecto, usar el auth_user_id como UUID del perfil
            
            # Solo buscar si realmente necesitamos mapear (para compatibilidad futura)
            try:
                response = db.client.table('usuarios').select('id').eq('auth_user_id', auth_user_id).execute()
                if response.data and len(response.data) > 0:
                    user_uuid = response.data[0]['id']
            except Exception as e:
                # Silencioso para evitar spam en logs
                pass
            
            g.user = {
                'id': auth_user_id,  # UUID de autenticación
                'user_uuid': user_uuid,  # UUID de la tabla usuarios (obtenido con searcher)
                'name': session.get('user_name'),
                'email': session.get('user_email'),
                'empresa': session.get('user_empresa', '')
            }
    
    @staticmethod
    def login_user(email: str, password: str):
        """
        Autentica un usuario con email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            dict: Resultado de la autenticación
        """
        try:
            if not email or not password:
                return {
                    "success": False,
                    "error": "Email y contraseña son requeridos",
                    "status_code": 400
                }
            
            # Autenticar con Supabase Auth
            auth_response = db.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                return {
                    "success": False,
                    "error": "Credenciales inválidas",
                    "status_code": 401
                }
            
            user = auth_response.user
            
            # Obtener información adicional del usuario desde info_contacto
            contact_response = db.client.table('info_contacto')\
                .select('id, nombre_completo, nombre_empresa')\
                .eq('usuario_id', user.id)\
                .execute()
            
            contact_info = contact_response.data[0] if contact_response.data else {}
            
            # Buscar el ID de la tabla usuarios correspondiente al auth_user_id
            user_mapping = db.client.table('usuarios')\
                .select('id')\
                .eq('auth_user_id', user.id)\
                .single()\
                .execute()
            
            if user_mapping.data:
                user_uuid = user_mapping.data['id']
            else:
                # Si no existe en usuarios, usar el auth_user_id como fallback
                user_uuid = str(user.id)
            
            # Crear sesión de usuario
            session['user_id'] = user_uuid  # ID de la tabla usuarios
            session['auth_user_id'] = str(user.id)  # ID de autenticación
            session['user_email'] = user.email
            session['user_name'] = contact_info.get('nombre_completo') or user.user_metadata.get('full_name', user.email)
            session['user_empresa'] = contact_info.get('nombre_empresa', '')
            
            # Almacenar tokens JWT para RLS
            try:
                # Extraer tokens correctamente de la respuesta de Supabase
                session_data = auth_response.session
                if session_data:
                    session['access_token'] = session_data.access_token
                    session['refresh_token'] = session_data.refresh_token
                    logger.info(f"JWT tokens stored in session for user: {user.email}")
                else:
                    logger.error("No session data in auth response")
            except Exception as e:
                logger.error(f"Error almacenando tokens JWT: {str(e)}")
            
            return {
                "success": True,
                "message": "Login exitoso",
                "redirect_url": "/",
                "status_code": 200
            }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error en login: {error_message}")
            
            # Manejar específicamente errores de autenticación de Supabase
            if "Invalid login credentials" in error_message:
                return {
                    "success": False,
                    "error": "Credenciales inválidas",
                    "status_code": 401
                }
            elif "NetworkError" in error_message or "ConnectionError" in error_message:
                return {
                    "success": False,
                    "error": "Error de conexión con el servidor de autenticación",
                    "status_code": 503
                }
            else:
                # Para cualquier otro error, incluidos errores HTML
                return {
                    "success": False,
                    "error": "Error al procesar la solicitud de login",
                    "status_code": 500
                }
    
    @staticmethod
    def logout_user():
        """Cierra la sesión del usuario actual."""
        session.clear()
        return {
            "success": True,
            "redirect_url": "/login"
        }
    
    @staticmethod
    def register_user(email: str, password: str, full_name: str, company: str = ""):
        """
        Registra un nuevo usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            full_name: Nombre completo del usuario
            company: Nombre de la empresa (opcional)
            
        Returns:
            dict: Resultado del registro
        """
        try:
            if not email or not password or not full_name:
                return {
                    "success": False,
                    "error": "Todos los campos son requeridos",
                    "status_code": 400
                }
            
            if len(password) < 6:
                return {
                    "success": False,
                    "error": "La contraseña debe tener al menos 6 caracteres",
                    "status_code": 400
                }
            
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
                return {
                    "success": False,
                    "error": "Error al crear usuario",
                    "status_code": 400
                }
            
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
            
            return {
                "success": True,
                "message": "Usuario creado exitosamente",
                "redirect_url": "/login",
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return {
                "success": False,
                "error": "Error al crear cuenta",
                "status_code": 500
            }
    
    @staticmethod
    def init_google_auth():
        """
        Inicia el flujo de autenticación con Google OAuth según MCP.
        
        Returns:
            dict: URL de redirección para Google OAuth
        """
        try:
            # Usar URL base dinámica en lugar de localhost
            base_url = request.environ.get('HTTP_X_FORWARDED_PROTO', request.scheme) + '://' + request.environ.get('HTTP_X_FORWARDED_HOST', request.host)
            redirect_uri = f"{base_url}/auth/callback"
            
            auth_response = db.client.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_uri,
                    "scopes": "email profile openid",
                    "skip_browser_redirect": False
                }
            })
            
            if auth_response.url:
                return {
                    "success": True,
                    "url": auth_response.url
                }
            else:
                return {
                    "success": False,
                    "error": "Error al generar URL de Google",
                    "status_code": 500
                }
                
        except Exception as e:
            logger.error(f"Error en Google auth: {str(e)}")
            return {
                "success": False,
                "error": "Error al conectar con Google",
                "status_code": 500
            }

    @staticmethod
    def api_google_auth():
        """
        API endpoint para iniciar el flujo de autenticación con Google OAuth.
        
        Returns:
            dict: Respuesta JSON con la URL de redirección
        """
        try:
            # Usar URL base dinámica en lugar de localhost
            base_url = request.environ.get('HTTP_X_FORWARDED_PROTO', request.scheme) + '://' + request.environ.get('HTTP_X_FORWARDED_HOST', request.host)
            redirect_uri = f"{base_url}/auth/callback"
            
            # Obtener la URL de redirección para Google OAuth
            auth_response = db.client.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_uri
                }
            })
            
            if auth_response.url:
                return {
                    "success": True,
                    "url": auth_response.url
                }
            else:
                return {
                    "success": False,
                    "error": "Error al generar URL de Google",
                    "status_code": 500
                }
                
        except Exception as e:
            logger.error(f"Error en Google auth API: {str(e)}")
            return {
                "success": False,
                "error": "Error al conectar con Google",
                "status_code": 500
            }
    
    @staticmethod
    def handle_google_callback(code: str):
        """
        Maneja el callback de Google OAuth.
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            dict: Resultado del proceso de autenticación
        """
        try:
            logger.info(f"Procesando callback - código: {code}")
            
            # Si no hay código, el token está en la sesión de Supabase
            if not code:
                logger.warning("No se recibió código, verificando sesión activa")
            
            # Obtener usuario actual desde Supabase Auth
            try:
                user_response = db.client.auth.get_user()
                
                if user_response and user_response.user:
                    user = user_response.user
                    logger.info(f"Usuario autenticado: {user.email}")
                else:
                    logger.error("No hay usuario autenticado")
                    return {
                        "success": False,
                        "redirect_url": "/register"
                    }
                    
            except Exception as e:
                logger.error(f"Error al obtener usuario: {e}")
                return {
                    "success": False,
                    "redirect_url": "/register"
                }
                logger.info(f"Usuario autenticado: {user.email}")
                
                # Verificar si ya existe en info_contacto
                contact_response = db.client.table('info_contacto')\
                    .select('id')\
                    .eq('usuario_id', str(user.id))\
                    .execute()
                
                if not contact_response.data:
                    # Crear entrada en info_contacto
                    contact_data = {
                        'usuario_id': str(user.id),
                        'nombre': user.user_metadata.get('full_name', ''),
                        'email': user.email,
                        'telefono': user.user_metadata.get('phone', ''),
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                    db.client.table('info_contacto').insert(contact_data).execute()
                    logger.info(f"Nuevo usuario registrado: {user.email}")
                
                # Guardar en sesión de Flask
                session['user_id'] = str(user.id)
                session['email'] = user.email
                session['user_name'] = user.user_metadata.get('full_name', user.email)
                
                return {
                    "success": True,
                    "redirect_url": "/"
                }
            else:
                logger.error("No se pudo obtener el usuario de Supabase")
                return {
                    "success": False,
                    "redirect_url": "/register"
                }
                
        except Exception as e:
            logger.error(f"Error en callback: {str(e)}")
            return {
                "success": False,
                "redirect_url": "/register"
            }
    
    @staticmethod
    def api_register(data):
        """
        API endpoint para registro manual de usuarios.
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            dict: Resultado del registro
        """
        try:
            email = data.get('email')
            password = data.get('password')
            full_name = data.get('nombre')
            company = data.get('telefono', '')
            
            return AuthManager.register_user(email, password, full_name, company)
            
        except Exception as e:
            logger.error(f"Error en registro API: {str(e)}")
            return {
                "success": False,
                "error": "Error al procesar el registro",
                "status_code": 500
            }
    
    @staticmethod
    def is_authenticated():
        """Verifica si el usuario está autenticado."""
        return 'user_id' in session
    
    @staticmethod
    def get_current_user():
        """Obtiene la información del usuario actual."""
        return g.user if hasattr(g, 'user') else None
    
    @staticmethod
    def get_user_id():
        """Obtiene el ID del usuario autenticado."""
        return session.get('user_id')
    
    @staticmethod
    def get_user_email():
        """Obtiene el email del usuario autenticado."""
        return session.get('user_email')
    
    @staticmethod
    def get_user_name():
        """Obtiene el nombre del usuario autenticado."""
        return session.get('user_name')


# Instancia global para importar fácilmente
auth_manager = AuthManager()
