"""
Módulo general para operaciones de escritura/modificación en la base de datos
Permite actualizar cualquier tabla/campo desde formularios JSON con manejo de RLS
"""

from flask import jsonify, g, session
from supabase import create_client
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DatabaseModifier:
    """Clase principal para manejar todas las operaciones de escritura en la base de datos"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
    def get_authenticated_client(self):
        """Obtener cliente Supabase autenticado con JWT del usuario"""
        try:
            # Intentar múltiples fuentes de token
            token = None
            
            # 1. Desde session
            if 'access_token' in session:
                token = session['access_token']
                logger.info("Token obtenido desde session")
            
            # 2. Desde g.user
            elif hasattr(g, 'user') and g.user:
                token = g.user.get('access_token')
                logger.info("Token obtenido desde g.user")
            
            # 3. Desde auth_manager si está disponible
            else:
                try:
                    from auth_manager import AuthManager
                    auth_manager = AuthManager()
                    current_user = auth_manager.load_current_user()
                    if current_user and 'access_token' in current_user:
                        token = current_user['access_token']
                        logger.info("Token obtenido desde auth_manager")
                except ImportError:
                    pass
            
            if not token:
                logger.error("No se encontró token de acceso en ninguna fuente")
                return None
                
            logger.info(f"Token encontrado: {token[:10]}...")
            
            # Crear cliente autenticado
            auth_client = create_client(self.supabase_url, self.supabase_key)
            auth_client.postgrest.auth(token)
            
            # Verificar autenticación
            test_result = auth_client.table('usuarios').select('id').limit(1).execute()
            logger.info("Cliente autenticado exitosamente")
            return auth_client
            
        except Exception as e:
            logger.error(f"Error creando cliente autenticado: {e}")
            return None
    
    def get_auth_user_id(self, auth_client, user_uuid):
        """Obtener el auth_user_id correspondiente al user_uuid"""
        try:
            user_info = auth_client.table('usuarios').select('auth_user_id').eq('id', user_uuid).single().execute()
            if not user_info.data:
                return None
            return user_info.data['auth_user_id']
        except Exception as e:
            logger.error(f"Error obteniendo auth_user_id: {e}")
            return None
    
    def validate_field(self, field_name, value, validation_rules=None):
        """Validar un campo según reglas específicas"""
        if not validation_rules:
            return True, None
            
        if 'min_length' in validation_rules and len(str(value)) < validation_rules['min_length']:
            return False, f"{field_name} debe tener al menos {validation_rules['min_length']} caracteres"
            
        if 'max_length' in validation_rules and len(str(value)) > validation_rules['max_length']:
            return False, f"{field_name} debe tener máximo {validation_rules['max_length']} caracteres"
            
        if 'required' in validation_rules and validation_rules['required'] and not value:
            return False, f"{field_name} es requerido"
            
        return True, None
    
    def check_unique_field(self, auth_client, table, field, value, exclude_auth_user_id=None):
        """Verificar si un valor es único en un campo específico"""
        try:
            query = auth_client.table(table).select('id').eq(field, value)
            if exclude_auth_user_id:
                query = query.neq('auth_user_id', exclude_auth_user_id)
            
            result = query.execute()
            return len(result.data) == 0
        except Exception as e:
            logger.error(f"Error verificando unicidad: {e}")
            return False
    
    def update_record(self, table, data, user_uuid, field_mappings=None, validation_rules=None):
        """
        Función general para actualizar registros en cualquier tabla
        
        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a actualizar
            user_uuid: UUID del usuario (usuarios.id)
            field_mappings: Mapeo de campos permitidos y sus validaciones
            validation_rules: Reglas de validación específicas por campo
        """
        try:
            auth_client = self.get_authenticated_client()
            if not auth_client:
                return {"success": False, "error": "Error de autenticación"}, 401
            
            # Obtener auth_user_id para RLS
            auth_user_id = self.get_auth_user_id(auth_client, user_uuid)
            if not auth_user_id:
                return {"success": False, "error": "Usuario no encontrado"}, 404
            
            # Filtrar campos permitidos
            if field_mappings:
                update_data = {}
                for field, value in data.items():
                    if field in field_mappings:
                        # Validar campo
                        rules = validation_rules.get(field, {}) if validation_rules else {}
                        is_valid, error_msg = self.validate_field(field, value, rules)
                        if not is_valid:
                            return {"success": False, "error": error_msg}, 400
                        
                        # Verificar unicidad si es necesario
                        if field_mappings.get(field, {}).get('unique', False):
                            unique = self.check_unique_field(auth_client, table, field, value, auth_user_id)
                            if not unique:
                                return {"success": False, "error": f"{field} ya existe"}, 400
                        
                        update_data[field] = value
            else:
                # Permitir todos los campos si no hay mapeo específico
                update_data = data
            
            if not update_data:
                return {"success": False, "error": "No hay campos para actualizar"}, 400   
            
            # Determinar campo de referencia según la tabla
            if table == 'usuarios':
                ref_field = 'auth_user_id'
                ref_value = auth_user_id
            else:
                # Para otras tablas, usar usuario_id
                ref_field = 'usuario_id'
                ref_value = user_uuid
            
            logger.info(f"Actualizando {table} para usuario {user_uuid} (auth_user_id: {auth_user_id})")
            logger.info(f"Datos a actualizar: {update_data}")
            
            # Realizar actualización
            update_result = auth_client.table(table).update(update_data).eq(ref_field, ref_value).execute()
            
            if not update_result.data or len(update_result.data) == 0:
                logger.error("No se encontraron datos en la respuesta de actualización")
                return {"success": False, "error": "No se pudo actualizar el registro"}, 500
            
            # Obtener datos actualizados
            updated_data = auth_client.table(table).select('*').eq(ref_field, ref_value).single().execute()
            
            return {
                "success": True,
                "message": f"{table} actualizado correctamente",
                "data": updated_data.data
            }, 200
            
        except Exception as e:
            logger.error(f"Error actualizando {table}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}, 500
    
    def insert_record(self, table, data, user_uuid=None):
        """Insertar un nuevo registro en cualquier tabla"""
        try:
            auth_client = self.get_authenticated_client()
            if not auth_client:
                return {"success": False, "error": "Error de autenticación"}, 401
            
            # Agregar usuario_id si se proporciona
            if user_uuid and 'usuario_id' not in data:
                data['usuario_id'] = user_uuid
            
            # Agregar timestamps
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Insertando en {table}: {data}")
            insert_result = auth_client.table(table).insert(data).execute()
            
            if not insert_result.data or len(insert_result.data) == 0:
                return {"success": False, "error": "No se pudo insertar el registro"}, 500
            
            return {
                "success": True,
                "message": f"Registro insertado en {table} correctamente",
                "data": insert_result.data[0]
            }, 200
            
        except Exception as e:
            logger.error(f"Error insertando en {table}: {e}")
            return {"success": False, "error": str(e)}, 500
    
    def get_record(self, table, user_uuid, select_fields='*'):
        """Obtener un registro de cualquier tabla"""
        try:
            auth_client = self.get_authenticated_client()
            if not auth_client:
                return None
            
            # Determinar campo de referencia según la tabla
            if table == 'usuarios':
                ref_field = 'id'
                ref_value = user_uuid
            else:
                ref_field = 'usuario_id'
                ref_value = user_uuid
            
            result = auth_client.table(table).select(select_fields).eq(ref_field, ref_value).single().execute()
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"Error obteniendo registro de {table}: {e}")
            return None
    
    def delete_record(self, table, user_uuid, extra_conditions=None):
        """Eliminar un registro de cualquier tabla"""
        try:
            auth_client = self.get_authenticated_client()
            if not auth_client:
                return {"success": False, "error": "Error de autenticación"}, 401
            
            # Determinar campo de referencia
            if table == 'usuarios':
                auth_user_id = self.get_auth_user_id(auth_client, user_uuid)
                if not auth_user_id:
                    return {"success": False, "error": "Usuario no encontrado"}, 404
                ref_field = 'auth_user_id'
                ref_value = auth_user_id
            else:
                ref_field = 'usuario_id'
                ref_value = user_uuid
            
            query = auth_client.table(table).delete().eq(ref_field, ref_value)
            
            # Agregar condiciones adicionales si existen
            if extra_conditions:
                for field, value in extra_conditions.items():
                    query = query.eq(field, value)
            
            delete_result = query.execute()
            
            return {
                "success": True,
                "message": f"Registro eliminado de {table} correctamente",
                "deleted_count": len(delete_result.data) if delete_result.data else 0
            }, 200
            
        except Exception as e:
            logger.error(f"Error eliminando de {table}: {e}")
            return {"success": False, "error": str(e)}, 500

# Instancia global para uso fácil
db_modifier = DatabaseModifier()

# Funciones de conveniencia para uso directo
def update_user_data(data, user_uuid):
    """Actualizar datos del usuario"""
    # Filtrar campos que no existen en la tabla
    allowed_fields = {'username', 'tipo_usuario', 'role', 'empresa', 'status'}
    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
    
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
    
    return db_modifier.update_record('usuarios', filtered_data, user_uuid, field_mappings, validation_rules)

def update_user_location(data, user_uuid):
    """Actualizar ubicación del usuario"""
    field_mappings = {
        'direccion': {},
        'ciudad': {},
        'provincia': {},
        'pais': {},
        'codigo_postal': {},
        'latitud': {},
        'longitud': {}
    }
    
    validation_rules = {
        'direccion': {'max_length': 255},
        'ciudad': {'max_length': 100},
        'provincia': {'max_length': 100},
        'pais': {'max_length': 100},
        'codigo_postal': {'max_length': 20}
    }
    
    return db_modifier.update_record('ubicaciones', data, user_uuid, field_mappings, validation_rules)

def update_user_contact(data, user_uuid):
    """Actualizar información de contacto del usuario"""
    field_mappings = {
        'correo_principal': {},
        'telefono_principal': {},
        'correo_secundario': {},
        'telefono_secundario': {},
        'sitio_web': {}
    }
    
    validation_rules = {
        'correo_principal': {'max_length': 255},
        'telefono_principal': {'max_length': 50},
        'correo_secundario': {'max_length': 255},
        'telefono_secundario': {'max_length': 50},
        'sitio_web': {'max_length': 255}
    }
    
    return db_modifier.update_record('info_contacto', data, user_uuid, field_mappings, validation_rules)
