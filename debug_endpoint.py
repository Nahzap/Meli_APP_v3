"""
Endpoint de debug para verificar datos reales en la base de datos
"""

from flask import Blueprint, jsonify, session
import logging
from supabase import create_client
import os

logger = logging.getLogger(__name__)
debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/info_contacto/<uuid:usuario_uuid>', methods=['GET'])
def debug_info_contacto(usuario_uuid):
    """Verificar datos reales de info_contacto para un usuario"""
    try:
        # Crear cliente anónimo para debug (sin autenticación)
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # Usar cliente anónimo
        auth_client = supabase
        
        # Verificar datos actuales
        logger.info(f"=== DEBUG ENDPOINT: Verificando info_contacto para {usuario_uuid} ===")
        
        # Buscar por usuario_id (UUID del usuario)
        result = auth_client.table('info_contacto').select('*').eq('usuario_id', str(usuario_uuid)).execute()
        
        logger.info(f"Query result: {result.data}")
        logger.info(f"Query count: {len(result.data) if result.data else 0}")
        
        return jsonify({
            "usuario_uuid": str(usuario_uuid),
            "datos_encontrados": result.data,
            "cantidad_registros": len(result.data) if result.data else 0,
            "query": f"SELECT * FROM info_contacto WHERE usuario_id = '{usuario_uuid}'"
        })
        
    except Exception as e:
        logger.error(f"Error en debug endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/test_update/<uuid:usuario_uuid>', methods=['POST'])
def test_update(usuario_uuid):
    """Probar update directo y verificar cambios reales"""
    try:
        # Crear cliente anónimo
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # Datos de prueba únicos con timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        test_data = {
            'nombre_completo': f'TEST {timestamp}',
            'correo_principal': f'test.{timestamp}@debug.cl',
            'telefono_principal': f'569{timestamp.replace(":", "")}'
        }
        
        logger.info(f"=== TEST UPDATE BRUTAL ===")
        logger.info(f"Usuario: {usuario_uuid}")
        logger.info(f"Antes de update - Datos: {test_data}")
        
        # Paso 1: Verificar datos ANTES
        before_data = supabase.table('info_contacto').select('*').eq('usuario_id', str(usuario_uuid)).execute()
        logger.info(f"DATOS ANTES: {before_data.data}")
        
        # Paso 2: Ejecutar update directo
        update_result = supabase.table('info_contacto').update(test_data).eq('usuario_id', str(usuario_uuid)).execute()
        logger.info(f"RESULTADO UPDATE: {update_result.data}")
        
        # Paso 3: Verificar datos DESPUÉS
        after_data = supabase.table('info_contacto').select('*').eq('usuario_id', str(usuario_uuid)).execute()
        logger.info(f"DATOS DESPUÉS: {after_data.data}")
        
        # Paso 4: Comparar cambios
        cambios = "NINGUNO"
        if after_data.data and before_data.data:
            if after_data.data[0] != before_data.data[0]:
                cambios = "SI HUBO CAMBIOS"
        
        return jsonify({
            "usuario_uuid": str(usuario_uuid),
            "datos_antes": before_data.data,
            "datos_despues": after_data.data,
            "cambios_detectados": cambios,
            "query_update": f"UPDATE info_contacto SET nombre_completo='{test_data['nombre_completo']}' WHERE usuario_id='{usuario_uuid}'"
        })
        
    except Exception as e:
        logger.error(f"ERROR CRÍTICO: {str(e)}")
        return jsonify({"error": str(e), "tipo_error": type(e).__name__}), 500
