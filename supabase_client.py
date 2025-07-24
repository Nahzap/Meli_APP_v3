"""
Módulo para manejar la conexión con Supabase.
"""
from supabase import create_client, Client
from dotenv import load_dotenv
import os

class SupabaseClient:
    _instance = None
    client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa el cliente de Supabase."""
        # Cargar variables de entorno desde .env
        env_loaded = load_dotenv(".env")
        if not env_loaded:
            raise ValueError("No se pudo cargar el archivo .env. Asegúrate de que existe en el directorio raíz.")
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Variables SUPABASE_URL y/o SUPABASE_KEY no definidas")
        
        try:
            self.client = create_client(self.url, self.key)
            # Verificar que la conexión se estableció correctamente
            if not hasattr(self.client, 'table'):
                raise ValueError("No se pudo inicializar el cliente de Supabase")
        except Exception as e:
            raise ValueError(f"Error al conectar con Supabase: {str(e)}")
    
    def test_connection(self):
        """
        Prueba la conexión con Supabase.
        Solo verifica que las credenciales sean válidas y que se pueda establecer la conexión.
        No intenta acceder a ninguna tabla.
        """
        # Verificar que las credenciales existen
        if not self.url or not self.key:
            return False, "Error: Faltan credenciales de Supabase"
            
        # Verificar formato de credenciales
        if not self.url.startswith('http'):
            return False, f"Error: URL de Supabase inválida"
            
        if not self.key.startswith('ey'):
            return False, "Error: Clave de API de Supabase inválida"
            
        # Verificar que el cliente se inicializó
        if not hasattr(self, 'client') or not self.client:
            return False, "Error: No se pudo inicializar el cliente de Supabase"
            
        # Si llegamos aquí, la conexión es exitosa
        return True, f"Conexion exitosa a Supabase"
    
    def get_usuario(self, user_id: str):
        """Obtiene un usuario por su ID."""
        return self.client.table('usuarios').select('*').eq('id', user_id).maybe_single().execute()
    
    def get_contacto(self, user_id: str):
        """Obtiene la información de contacto de un usuario."""
        return self.client.table('info_contacto').select('*').eq('usuario_id', user_id).maybe_single().execute()
    
    def get_ubicaciones(self, user_id: str):
        """Obtiene las ubicaciones de un usuario."""
        return self.client.table('ubicaciones').select('*').eq('usuario_id', user_id).execute()
    
    def get_producciones_apicolas(self, user_id: str):
        """Obtiene las producciones apícolas de un usuario."""
        return self.client.table('produccion_apicola')\
            .select('*')\
            .eq('usuario_id', user_id)\
            .order('temporada', desc=True)\
            .execute()
    
    def get_origenes_botanicos(self, produccion_ids: list):
        """Obtiene los orígenes botánicos para una lista de IDs de producción."""
        if not produccion_ids:
            return []
        return self.client.table('origenes_botanicos')\
            .select('*')\
            .in_('produccion_id', produccion_ids)\
            .execute()
    
    def get_solicitudes_apicultor(self, user_id: str):
        """Obtiene las solicitudes de apicultor de un usuario."""
        return self.client.table('solicitudes_apicultor')\
            .select('*')\
            .eq('usuario_id', user_id)\
            .order('created_at', desc=True)\
            .execute()

# Instancia global
db = SupabaseClient()
