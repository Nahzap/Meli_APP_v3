"""
Módulo para manejar operaciones relacionadas con tablas en Supabase.
Incluye funciones para listar tablas, obtener datos, etc.
"""
import os
import json
import uuid
import decimal
import datetime
from supabase_client import db


def ensure_json_serializable(data):
    """
    Convierte cualquier valor no serializable a JSON en una representación que sí lo sea.
    
    Args:
        data: El valor a convertir
    
    Returns:
        El valor convertido a una representación serializable a JSON
    """
    if isinstance(data, (str, int, float, bool, type(None))):
        return data
    elif isinstance(data, (list, tuple)):
        return [ensure_json_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {key: ensure_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, (datetime.datetime, datetime.date)):
        return data.isoformat()
    elif isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, decimal.Decimal):
        return float(data)
    else:
        return str(data)


def list_tables():
    """
    Obtiene la lista de todas las tablas en la base de datos.
    
    Returns:
        tuple: (success, result) donde success es un booleano que indica si la operación fue exitosa,
               y result es una lista de nombres de tablas o un mensaje de error
    """
    try:
        # Usar la función RPC personalizada
        result = db.client.rpc('get_all_tables').execute()
        
        if hasattr(result, 'data') and result.data:
            tables = [table['table_name'] for table in result.data]
            return True, tables
        return False, "No se encontraron tablas"
            
    except Exception as e:
        error_msg = f"Error al listar tablas: {str(e)}"
        print(error_msg)
        return False, error_msg


def get_table_data(table_name, page=1, per_page=20):
    """
    Obtiene datos paginados de una tabla específica.
    
    Args:
        table_name (str): Nombre de la tabla
        page (int): Número de página (comienza en 1)
        per_page (int): Cantidad de registros por página
        
    Returns:
        tuple: (success, result) donde success es un booleano que indica si la operación fue exitosa,
               y result es un diccionario con los datos o un mensaje de error
    """
    try:
        # Validar parámetros
        try:
            page = max(1, int(page))
            per_page = min(100, max(1, int(per_page)))
        except (ValueError, TypeError):
            return False, "Parámetros de paginación inválidos"

        # Calcular rango
        start = (page - 1) * per_page
        end = start + per_page - 1

        # Realizar consulta
        result = db.client.table(table_name)\
                        .select('*', count='exact')\
                        .range(start, end)\
                        .execute()

        if not hasattr(result, 'data') or result.data is None:
            return False, f"No se encontraron datos en la tabla {table_name}"
            
        # Obtener el total de registros
        total_records = getattr(result, 'count', len(result.data))
        
        # Calcular total de páginas
        total_pages = (total_records + per_page - 1) // per_page
        
        # Asegurar que los datos sean serializables a JSON
        json_safe_data = ensure_json_serializable(result.data)
        
        return True, {
            'data': json_safe_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_records': total_records,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            }
        }
            
    except Exception as e:
        error_msg = f"Error al obtener datos de la tabla {table_name}: {str(e)}"
        print(error_msg)
        return False, error_msg
