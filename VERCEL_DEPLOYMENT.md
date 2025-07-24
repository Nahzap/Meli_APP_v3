# Guía de Despliegue en Vercel - MeliAPP_v2 (PRODUCCIÓN)

## Configuración de Producción Según Documentación Oficial de Vercel

Esta configuración sigue las mejores prácticas oficiales de Vercel para aplicaciones Flask en producción.

## Archivos Creados/Modificados para Producción

### 1. `vercel.json` - Configuración Principal de Producción
- **Python 3.12**: Versión recomendada por Vercel
- **Memoria optimizada**: 1024MB para mejor rendimiento
- **Cache headers**: Configuración de cache para APIs
- **Rewrites**: Redirección automática de `/` a `/buscar`
- **Variables de entorno**: Configuración segura

### 2. `requirements.txt` - Dependencias Optimizadas
- **Flask 3.0.3**: Versión más reciente compatible con Python 3.12
- **Supabase 2.3.4**: Cliente actualizado
- **Versiones específicas**: Para estabilidad en producción

### 3. `.vercelignore` - Archivos Excluidos
- Excluye archivos de desarrollo y cache
- Optimiza el tamaño del deployment

### 4. `runtime.txt` - Python 3.12
- Versión recomendada por Vercel para producción
- Mejor rendimiento y compatibilidad

### 5. `app.py` - Optimizado para Producción
- **Detección de entorno**: Automática entre desarrollo/producción
- **Logging optimizado**: Diferentes niveles según entorno
- **Manejo de errores**: Robusto para producción
- **Configuración WSGI**: Exposición correcta de la app

### 6. `.env.production` - Template de Variables
- Guía para configurar variables en Vercel dashboard
- No contiene valores reales (seguridad)

## Pasos para Desplegar

### 1. Configurar Variables de Entorno en Vercel (CRÍTICO)

**⚠️ IMPORTANTE**: Configura estas variables en el dashboard de Vercel antes del despliegue.

#### Variables Requeridas:

```bash
# Supabase Configuration
SUPABASE_URL=https://jrduviahstserdwtfkft.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZHV2aWFoc3RzZXJkd3Rma2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2NDAxMDQsImV4cCI6MjA2MjIxNjEwNH0.YkDb2yXbYeaQp2G8tEsoysjfTeBynUzUFjnIkqdW3FY

# Production Environment
VERCEL=1
FLASK_ENV=production

# Security (Generar una clave secreta fuerte)
SECRET_KEY=tu_clave_secreta_de_produccion_aqui
```

#### Pasos para Configurar en Vercel Dashboard:

1. Ve a tu proyecto en [vercel.com](https://vercel.com)
2. Navega a **Settings** → **Environment Variables**
3. Agrega cada variable con su valor correspondiente
4. Selecciona **Production**, **Preview**, y **Development** según necesites
5. Guarda los cambios

#### Verificación de Variables:

Puedes verificar que las variables estén configuradas correctamente visitando `/api/test` después del despliegue.

### 2. Desplegar con Vercel CLI (Recomendado)

```bash
# 1. Instalar Vercel CLI globalmente
npm i -g vercel

# 2. Autenticarse
vercel login

# 3. Primer despliegue (desde la raíz del proyecto)
vercel

# 4. Despliegues posteriores a producción
vercel --prod

# 5. Verificar el despliegue
vercel inspect
```

#### Comandos Adicionales Útiles:

```bash
# Ver logs en tiempo real
vercel logs --follow

# Listar todos los despliegues
vercel ls

# Promover un despliegue a producción
vercel promote [deployment-url]
```

### 3. Desplegar desde GitHub

1. Conecta tu repositorio de GitHub con Vercel
2. Las variables de entorno se configuran automáticamente
3. Cada push a main desplegará automáticamente

## Rutas Disponibles Después del Despliegue

### Rutas Web
- `/` - Página principal del buscador
- `/buscar` - Buscar usuarios
- `/sugerir` - Autocompletado de usuarios

### Rutas API
- `/api/test` - Probar conexión con Supabase
- `/api/tables` - Listar todas las tablas
- `/api/table/<tabla>` - Ver datos de una tabla específica
- `/api/usuario/<uuid>` - Obtener usuario por segmento de UUID
- `/api/usuario/<uuid>/qr` - Generar QR del usuario

## Notas Importantes

1. **Timeout**: Las funciones tienen un timeout de 30 segundos
2. **Cold Start**: La primera petición puede ser más lenta
3. **Variables de Entorno**: Nunca commitear el archivo `.env`
4. **Logs**: Usar `vercel logs` para ver logs de producción

## Solución de Problemas

### Error de Importación
Si hay errores de importación, verificar que todos los módulos estén en `requirements.txt`

### Error de Conexión a Supabase
Verificar que las variables de entorno estén configuradas correctamente en Vercel

### Timeout
Si las consultas son muy lentas, considerar optimizar las queries o aumentar el timeout

## Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs --follow

# Ver información del proyecto
vercel inspect

# Eliminar deployment
vercel remove [deployment-url]
```
