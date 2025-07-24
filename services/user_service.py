"""
Servicio para manejar operaciones relacionadas con usuarios en la base de datos.
"""
from typing import Tuple, Dict, List, Any
from supabase_client import db

def get_user_data(user_id: str) -> Tuple[Dict, Dict, List, List, List, List, str]:
    """
    Obtiene todos los datos de un usuario desde la base de datos.
    
    Args:
        user_id: ID del usuario a buscar
        
    Returns:
        Tuple[user_data, contact_data, locations, producciones, origenes_botanicos, solicitudes, error_message]
    """
    try:
        # Obtener datos del usuario
        user_response = db.get_usuario(user_id)
        if not user_response.data:
            return None, None, [], [], [], [], "Usuario no encontrado"

        user = user_response.data
        
        # Obtener información de contacto
        contact_response = db.get_contacto(user_id)
        contact = contact_response.data if contact_response.data else {}
        
        # Obtener ubicaciones
        locations_response = db.get_ubicaciones(user_id)
        locations = locations_response.data if hasattr(locations_response, 'data') else []
        
        # Obtener producción apícola
        produccion_response = db.get_producciones_apicolas(user_id)
        producciones = produccion_response.data if hasattr(produccion_response, 'data') else []
        produccion_ids = [p['id'] for p in producciones]
        
        # Obtener orígenes botánicos
        origenes_botanicos = []
        if produccion_ids:
            origenes_response = db.get_origenes_botanicos(produccion_ids)
            origenes_botanicos = origenes_response.data if hasattr(origenes_response, 'data') else []
        
        # Obtener solicitudes
        solicitudes_response = db.get_solicitudes_apicultor(user_id)
        solicitudes = solicitudes_response.data if hasattr(solicitudes_response, 'data') else []
        
        return user, contact, locations, producciones, origenes_botanicos, solicitudes, ""
        
    except Exception as e:
        error_msg = f"Error al buscar usuario: {str(e)}"
        print(error_msg)
        return None, None, [], [], [], [], error_msg
