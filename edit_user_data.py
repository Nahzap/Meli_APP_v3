from flask import Blueprint, request, jsonify, g
import logging
from modify_DB import db_modifier, update_user_data
from auth_manager import AuthManager

logger = logging.getLogger(__name__)

edit_bp = Blueprint('edit_user_data', __name__)

@edit_bp.route('/api/edit/usuarios', methods=['POST'])
@AuthManager.login_required
def edit_usuarios():
    """Editar información de usuario usando el módulo modify_DB"""
    try:
        logger.info("=== INICIANDO EDICIÓN DE USUARIO ===")
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        # Obtener user_uuid desde g.user después de la autenticación
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        logger.info(f"📦 Datos recibidos: {data}")
        logger.info(f"👤 UUID usuario: {user_uuid}")
        
        # Remove non-existent fields
        data = {k: v for k, v in data.items() if k not in ['updated_at', 'created_at', 'id']}
        
        # Filtrar solo campos válidos para usuarios
        valid_fields = ['username', 'tipo_usuario', 'role', 'empresa', 'status']
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        logger.info(f"🔍 Datos filtrados: {filtered_data}")
        
        # DEBUG: Verificar si hay campo role y su longitud
        if 'role' in filtered_data:
            original_role = str(filtered_data['role'])
            logger.info(f"📝 Campo role - Original: '{original_role}' ({len(original_role)} chars)")
        
        if not filtered_data:
            return jsonify({"success": False, "error": "No hay campos válidos para actualizar"}), 400
        
        # Usar la función update_user_data que incluye truncamiento de role
        logger.info(f"🔄 Llamando a update_user_data con datos: {filtered_data}")
        result, status_code = update_user_data(filtered_data, user_uuid)
        
        logger.info(f"✅ Resultado: {result}, Status: {status_code}")
        # Agregar URL del perfil siempre usando el UUID del usuario autenticado
        if isinstance(result, dict) and result.get('success'):
            result['profile_url'] = f"/profile/{user_uuid}"
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error editando usuario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/edit/ubicaciones', methods=['POST', 'PUT', 'DELETE'])
@AuthManager.login_required
def handle_ubicaciones():
    """Manejar operaciones CRUD para ubicaciones con conversión automática de Plus Code"""
    try:
        method = request.method
        logger.info(f"🗺️ [UBICACIONES] ===== INICIANDO {method} =====")
        
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
        
        if method == 'DELETE':
            # Eliminar ubicación
            data = request.get_json()
            location_id = data.get('id')
            
            if not location_id:
                return jsonify({"success": False, "error": "ID de ubicación requerido"}), 400
            
            # Verificar que la ubicación pertenece al usuario
            ubicaciones = db_modifier.get_records('ubicaciones', user_uuid)
            ubicacion = next((u for u in ubicaciones if u.get('id') == location_id), None)
            
            if not ubicacion:
                return jsonify({"success": False, "error": "Ubicación no encontrada o no pertenece al usuario"}), 404
            
            result, status_code = db_modifier.delete_record('ubicaciones', user_uuid, {'id': location_id})
            return jsonify(result), status_code
            
        elif method == 'POST':
            # Crear nueva ubicación
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Datos requeridos"}), 400
            
            # Importar el conversor de Plus Code
            from gmaps_utils import process_ubicacion_data
            processed_data = process_ubicacion_data(data)
            
            # Validar campos requeridos
            required_fields = ['nombre', 'latitud', 'longitud']
            missing_fields = [f for f in required_fields if f not in processed_data or not processed_data[f]]
            
            if missing_fields:
                return jsonify({"success": False, "error": f"Campos requeridos: {missing_fields}"}), 400
            
            # Preparar datos para inserción - solo columnas existentes
            insert_data = {
                'auth_user_id': user_uuid,
                'nombre': str(processed_data['nombre']).strip(),
                'latitud': float(processed_data['latitud']),
                'longitud': float(processed_data['longitud']),
                'norma_geo': str(processed_data.get('norma_geo', 'WGS84')).strip(),
                'descripcion': str(processed_data.get('descripcion', '')).strip()
            }
            
            result, status_code = db_modifier.insert_record('ubicaciones', insert_data, user_uuid)
            
            if result and isinstance(result, dict) and result.get('success'):
                result['profile_url'] = f"/profile/{user_uuid}"
            
            return jsonify(result), status_code
            
        elif method == 'PUT':
            # Actualizar ubicación existente
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Datos requeridos"}), 400
            
            location_id = data.get('id')
            if not location_id:
                return jsonify({"success": False, "error": "ID de ubicación requerido"}), 400
            
            # Verificar que la ubicación pertenece al usuario
            ubicaciones = db_modifier.get_records('ubicaciones', user_uuid)
            ubicacion = next((u for u in ubicaciones if u.get('id') == location_id), None)
            
            if not ubicacion:
                return jsonify({"success": False, "error": "Ubicación no encontrada o no pertenece al usuario"}), 404
            
            # Importar el conversor de Plus Code
            from gmaps_utils import process_ubicacion_data
            processed_data = process_ubicacion_data(data)
            
            # Validar campos requeridos
            required_fields = ['nombre', 'latitud', 'longitud']
            missing_fields = [f for f in required_fields if f not in processed_data or not processed_data[f]]
            
            if missing_fields:
                return jsonify({"success": False, "error": f"Campos requeridos: {missing_fields}"}), 400
            
            # Preparar datos para actualización - solo columnas existentes
            update_data = {
                'nombre': str(processed_data['nombre']).strip(),
                'latitud': float(processed_data['latitud']),
                'longitud': float(processed_data['longitud']),
                'norma_geo': str(processed_data.get('norma_geo', 'WGS84')).strip(),
                'descripcion': str(processed_data.get('descripcion', '')).strip()
            }
            
            result, status_code = db_modifier.update_record('ubicaciones', update_data, user_uuid, {'id': location_id})
            
            if result and isinstance(result, dict) and result.get('success'):
                result['profile_url'] = f"/profile/{user_uuid}"
            
            return jsonify(result), status_code
            
    except ValueError as e:
        logger.error(f"🗺️ [UBICACIONES] ❌ Error de validación: {e}")
        return jsonify({"success": False, "error": f"Formato inválido de coordenadas: {e}"}), 400
    except Exception as e:
        logger.error(f"🗺️ [UBICACIONES] 💥 Error crítico: {e}")
        import traceback
        logger.error(f"🗺️ [UBICACIONES] 💥 Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/data/usuarios', methods=['GET'])
@AuthManager.login_required
def get_usuario_data():
    """Obtener datos del usuario autenticado para el formulario de edición"""
    try:
        # Obtener el UUID del usuario autenticado desde g.user
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
            
        # Log para debugging
        logger.info(f"Usuario UUID obtenido: {user_uuid}")
        
        # Obtener datos del usuario
        usuario = db_modifier.get_record('usuarios', user_uuid)
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado en la base de datos"}), 404
        # Obtener información de contacto
        info_contacto = db_modifier.get_record('info_contacto', user_uuid)
        
        # Obtener ubicaciones
        ubicaciones = db_modifier.get_record('ubicaciones', user_uuid)
        
        return jsonify({
            "success": True,
            "usuario": db_modifier.get_record('usuarios', user_uuid),
            "info_contacto": info_contacto or {},
            "ubicaciones": ubicaciones or {},
            "id": user_uuid  # UUID completo del usuario autenticado
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de usuario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/data/ubicaciones', methods=['GET'])
@AuthManager.login_required
def get_ubicaciones_data():
    """Obtener ubicaciones del usuario autenticado"""
    try:
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Obtener ubicaciones
        ubicaciones = db_modifier.get_records('ubicaciones', user_uuid)
        
        return jsonify({
            "success": True,
            "ubicaciones": ubicaciones or []
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo ubicaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/data/info_contacto', methods=['GET'])
@AuthManager.login_required
def get_info_contacto_data():
    """Obtener datos de info_contacto del usuario autenticado"""
    try:
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Obtener información de contacto
        info_contacto = db_modifier.get_record('info_contacto', user_uuid)
        
        return jsonify({
            "success": True,
            "data": info_contacto or {}
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de info_contacto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/edit/info_contacto', methods=['POST'])
@AuthManager.login_required
def edit_info_contacto():
    """Editar información de contacto del usuario usando el módulo modify_DB"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        # Obtener el UUID del usuario autenticado
        user_uuid = g.user.get('id')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
            
        logger.info(f"Actualizando info_contacto para usuario: {user_uuid}")
        logger.info(f"Datos recibidos RAW: {data}")
        logger.info(f"Tipo de datos: {type(data)}")
        
        # Convertir todos los valores a strings y limpiar
        clean_data = {}
        for k, v in data.items():
            if v is not None:
                clean_data[k] = str(v).strip()
                logger.info(f"Campo {k}: '{v}' -> '{clean_data[k]}' (len: {len(clean_data[k])})")
        
        # Definir campos válidos
        valid_fields = ['nombre_completo', 'nombre_empresa', 'correo_principal', 'telefono_principal', 'correo_secundario', 'telefono_secundario', 'direccion', 'comuna', 'region', 'pais']
        
        # Filtrar campos válidos
        filtered_data = {k: v for k, v in clean_data.items() if k in valid_fields}
        logger.info(f"Campos válidos: {filtered_data}")
        
        # Verificar contenido real
        has_content = False
        for k, v in filtered_data.items():
            if v and str(v).strip():
                logger.info(f"Campo CON contenido: {k} = '{v}'")
                has_content = True
            else:
                logger.info(f"Campo SIN contenido: {k} = '{v}'")
        
        logger.info(f"¿Tiene contenido real?: {has_content}")
        
        if not has_content:
            return jsonify({"success": False, "error": "Por favor ingresa al menos un valor válido"}), 400
        
        # Solo enviar campos con contenido real
        final_data = {k: v for k, v in filtered_data.items() if v and str(v).strip()}
        logger.info(f"Datos finales para actualizar: {final_data}")
        
        # Usar la función específica para info_contacto
        from modify_DB import update_user_contact
        result, status_code = update_user_contact(filtered_data, user_uuid)
        
        # Agregar URL del perfil siempre usando el UUID del usuario autenticado
        if isinstance(result, dict) and result.get('success', False):
            result['profile_url'] = f"/profile/{user_uuid}"
            result['user_id'] = user_uuid  # Asegurar que incluya el ID
            result['redirect_url'] = f"/profile/{user_uuid}"  # URL explícita para redirección
            logger.info(f"Redirección configurada: /profile/{user_uuid}")
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error editando info_contacto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500