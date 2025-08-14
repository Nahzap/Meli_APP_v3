from flask import Blueprint, request, jsonify, g
import logging
from modify_DB import db_modifier

logger = logging.getLogger(__name__)

edit_bp = Blueprint('edit_user_data', __name__)

@edit_bp.route('/api/edit/usuarios', methods=['POST'])
def edit_usuarios():
    """Editar información de usuario usando el módulo modify_DB"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        user_uuid = g.user.get('user_uuid')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Remove non-existent fields
        data = {k: v for k, v in data.items() if k not in ['updated_at', 'created_at', 'id']}
        
        # Definir validaciones para usuarios
        field_mappings = {
            'username': {'unique': True},
            'tipo_usuario': {},
            'role': {},
            'empresa': {},
            'status': {}
        }
        
        validation_rules = {
            'username': {'min_length': 2, 'max_length': 80},
            'tipo_usuario': {'max_length': 50},
            'role': {'max_length': 50},
            'empresa': {'max_length': 100}
        }
        
        # Filtrar solo campos válidos
        valid_fields = ['username', 'tipo_usuario', 'role', 'empresa', 'status']
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        if not filtered_data:
            return jsonify({"success": False, "error": "No hay campos válidos para actualizar"}), 400
        
        # Usar el módulo modify_DB para actualizar
        result, status_code = db_modifier.update_record(
            'usuarios', 
            filtered_data, 
            user_uuid, 
            field_mappings, 
            validation_rules
        )
        
        # Agregar URL del perfil si la actualización fue exitosa
        if result.get('success'):
            result['profile_url'] = f"/profile/{user_uuid}"
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error editando usuario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/edit/ubicaciones', methods=['POST'])
def edit_ubicaciones():
    """Editar ubicaciones del usuario usando el módulo modify_DB"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        user_uuid = g.user.get('user_uuid')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Definir campos válidos para ubicaciones
        valid_fields = ['direccion', 'ciudad', 'provincia', 'pais', 'codigo_postal', 'latitud', 'longitud']
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        if not filtered_data:
            return jsonify({"success": False, "error": "No hay campos para actualizar"}), 400
        
        # Usar el módulo modify_DB para actualizar
        result, status_code = db_modifier.update_record('ubicaciones', filtered_data, user_uuid)
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error editando ubicaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/data/usuarios', methods=['GET'])
def get_usuario_data():
    """Obtener datos del usuario autenticado para el formulario de edición"""
    try:
        user_uuid = g.user.get('user_uuid')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Obtener datos del usuario
        usuario = db_modifier.get_record('usuarios', user_uuid)
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Obtener información de contacto
        info_contacto = db_modifier.get_record('info_contacto', user_uuid)
        
        # Obtener ubicaciones
        ubicaciones = db_modifier.get_record('ubicaciones', user_uuid)
        
        return jsonify({
            "success": True,
            "usuario": usuario,
            "info_contacto": info_contacto or {},
            "ubicaciones": ubicaciones or {}
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de usuario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@edit_bp.route('/api/data/info_contacto', methods=['GET'])
def get_info_contacto_data():
    """Obtener datos de info_contacto del usuario autenticado"""
    try:
        user_uuid = g.user.get('user_uuid')
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
def edit_info_contacto():
    """Editar información de contacto del usuario usando el módulo modify_DB"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        user_uuid = g.user.get('user_uuid')
        if not user_uuid:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
        
        # Definir campos válidos para información de contacto
        valid_fields = ['nombre_completo', 'nombre_empresa', 'correo_principal', 'telefono_principal', 'correo_secundario', 'telefono_secundario', 'direccion', 'comuna', 'region', 'pais']
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        if not filtered_data:
            return jsonify({"success": False, "error": "No hay campos para actualizar"}), 400
        
        # Usar el módulo modify_DB para actualizar
        result, status_code = db_modifier.update_record('info_contacto', filtered_data, user_uuid)
        
        # Agregar URL de perfil al resultado (igual que usuarios)
        if result.get('success', False):
            result['profile_url'] = f"/profile/{user_uuid}"
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error editando info_contacto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
