"""
Utilidades para Google Maps Plus Code usando la biblioteca oficial openlocationcode-python
Convierte Plus Codes a coordenadas lat/lng de forma confiable
"""
import logging
from openlocationcode import openlocationcode

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def process_ubicacion_data(data):
    """
    Procesa los datos de ubicación, convirtiendo Plus Code a coordenadas si es necesario.
    Prioriza latitud/longitud si ya existen y son válidas.
    Utiliza la biblioteca openlocationcode-python para decodificar Plus Codes.
    
    Args:
        data: Diccionario con datos de ubicación (puede contener latitud, longitud, gmaps_plus_code)
    
    Returns:
        Diccionario con datos procesados incluyendo latitud y longitud válidas
    """
    logger = logging.getLogger(__name__)
    logger.info("--- Iniciando process_ubicacion_data ---")
    logger.info(f"Datos de entrada: {data}")

    processed_data = data.copy()

    # 1. Validar y usar latitud/longitud existentes si son válidas
    lat = processed_data.get('latitud')
    lng = processed_data.get('longitud')

    if lat and lng:
        try:
            valid_lat = float(lat)
            valid_lng = float(lng)
            if valid_lat != 0.0 and valid_lng != 0.0:
                logger.info(f"Coordenadas válidas encontradas: ({valid_lat}, {valid_lng})")
                processed_data['latitud'] = valid_lat
                processed_data['longitud'] = valid_lng
                return processed_data
            else:
                logger.info("Coordenadas son cero, se usará Plus Code")
        except (ValueError, TypeError):
            logger.warning("Coordenadas no válidas, se usará Plus Code")

    # 2. Procesar Plus Code si no hay coordenadas válidas
    plus_code = processed_data.get('gmaps_plus_code')
    if plus_code:
        # Extraer código Plus limpio sin espacios ni texto adicional
        import re
        plus_code_match = re.search(r'([A-Z0-9]{4,}\+[A-Z0-9]{2,})', str(plus_code).upper())
        
        if plus_code_match:
            clean_plus_code = plus_code_match.group(1)
            logger.info(f"Plus Code extraído: '{clean_plus_code}'")

            try:
                # Procesar cualquier Plus Code dinámicamente
                if openlocationcode.isShort(clean_plus_code):
                    # Código corto: usar referencia dinámica basada en contexto del input
                    input_text = str(plus_code).lower()
                    
                    # Detectar región dinámicamente del texto de entrada
                    if 'concepción' in input_text or 'concepcion' in input_text:
                        ref_lat, ref_lng = -36.827, -73.050  # Concepción
                    elif 'santiago' in input_text:
                        ref_lat, ref_lng = -33.449, -70.669  # Santiago
                    elif 'valparaíso' in input_text or 'valparaiso' in input_text:
                        ref_lat, ref_lng = -33.047, -71.621  # Valparaíso
                    else:
                        # Usar centro geográfico de Chile como fallback
                        ref_lat, ref_lng = -35.0, -71.0
                    
                    # Recuperar código completo
                    full_code = openlocationcode.recoverNearest(clean_plus_code, ref_lat, ref_lng)
                    decoded = openlocationcode.decode(full_code)
                    processed_data['latitud'] = round(decoded.latitudeCenter, 3)
                    processed_data['longitud'] = round(decoded.longitudeCenter, 3)
                    logger.info(f"Plus Code procesado: {clean_plus_code} -> ({processed_data['latitud']}, {processed_data['longitud']})")
                    
                elif openlocationcode.isValid(clean_plus_code):
                    # Código completo válido
                    decoded = openlocationcode.decode(clean_plus_code)
                    processed_data['latitud'] = round(decoded.latitudeCenter, 3)
                    processed_data['longitud'] = round(decoded.longitudeCenter, 3)
                    logger.info(f"Plus Code completo: {clean_plus_code} -> ({processed_data['latitud']}, {processed_data['longitud']})")
                else:
                    logger.warning(f"Plus Code no válido: {clean_plus_code}")
            except Exception as e:
                logger.error(f"Error procesando Plus Code: {e}")
        else:
            logger.warning("No se encontró un Plus Code válido en el texto proporcionado")

    logger.info(f"Datos procesados: {processed_data}")
    logger.info("--- Finalizando process_ubicacion_data ---")
    return processed_data
