# 📋 MeliAPP v3 - Informe General del Proyecto

## 🎯 Resumen Ejecutivo

**MeliAPP v3** es una plataforma web integral para la gestión de operaciones apícolas, construida con Flask y Supabase. Representa una evolución completa desde la versión anterior, incorporando autenticación moderna con Google OAuth, sistema de clasificación botánica visual, gestión de lotes apícolas, y generación de QR codes para perfiles públicos.

## 🏗️ Arquitectura del Sistema

### **Stack Tecnológico**
- **Backend**: Flask 2.3.3 (Python 3.8+)
- **Base de Datos**: Supabase (PostgreSQL 14+)
- **Frontend**: HTML5 + Tailwind CSS + JavaScript vanilla
- **Autenticación**: Google OAuth 2.0 + Supabase Auth
- **Deployment**: Vercel-ready con configuración optimizada
- **QR Codes**: Librería Segno
- **HTTP Client**: httpx para requests asíncronos

### **Estructura de Archivos**

```
MeliAPP_v2/
├── 📁 docs/                          # Documentación del proyecto
│   ├── README.md                    # Documentación principal
│   ├── PROJECT_REPORT.md            # Este informe
│   └── clases.csv                   # Datos de clasificación botánica
├── 📁 static/                       # Assets estáticos
│   ├── 📁 css/                      # Estilos Tailwind
│   ├── 📁 js/                       # JavaScript modular
│   │   ├── botanical-chart.js       # Gráficos botánicos
│   │   ├── lotes-carousel.js        # Carrusel de lotes
│   │   └── oauth-handler.js         # Manejo OAuth
│   └── 📁 images/                   # Imágenes del proyecto
├── 📁 templates/                    # Plantillas HTML
│   ├── 📁 base/                     # Layouts base
│   ├── 📁 pages/                    # Páginas principales
│   ├── 📁 auth/                     # Autenticación
│   └── 📁 components/               # Componentes reutilizables
├── 📁 qr_code/                      # Módulo de generación QR
│   ├── __init__.py
│   └── generator.py
├── 🐍 Archivos Python principales:
│   ├── app.py                       # Aplicación Flask principal
│   ├── auth_manager.py              # Gestión centralizada de autenticación
│   ├── auth_manager_routes.py       # Rutas de autenticación separadas
│   ├── supabase_client.py           # Cliente Supabase singleton
│   ├── searcher.py                  # Búsqueda avanzada multi-tabla
│   ├── botanical_chart.py           # Sistema de clasificación botánica
│   ├── lotes_routes.py              # API de gestión de lotes
│   ├── data_tables_supabase.py      # Operaciones de tablas
│   ├── edit_user_data.py            # Edición de datos usuarios
│   ├── profile_routes.py            # Rutas de perfiles
│   ├── web_routes.py                # Rutas web principales
│   └── gmaps_utils.py               # Utilidades Google Maps
├── 📄 Archivos de configuración:
├── requirements.txt                 # Dependencias Python
├── runtime.txt                      # Versión Python para Vercel
├── vercel.json                      # Configuración Vercel
├── .env.example                     # Variables de entorno ejemplo
├── .gitignore                       # Archivos ignorados por Git
└── .vercelignore                    # Archivos ignorados por Vercel
```

## 🔐 Sistema de Autenticación

### **Flujo de Autenticación**
1. **Google OAuth Integration**: Implementación completa con Supabase Auth
2. **Registro Automático**: Creación de usuarios y perfiles al autenticarse
3. **Gestión de Sesiones**: Cookies seguras con TTL de 1 hora
4. **Roles de Usuario**: Apicultores y clientes diferenciados

### **Endpoints de Autenticación**
- `GET /login` - Página de inicio de sesión
- `GET /register` - Registro de nuevos usuarios
- `GET /auth/callback` - Callback de Google OAuth
- `POST /api/auth/login` - API login
- `POST /api/auth/register` - API registro
- `GET /api/auth/session` - Estado de sesión
- `POST /api/auth/logout` - Cierre de sesión

## 🗄️ Esquema de Base de Datos

### **Tablas Principales**

#### **usuarios**
- `auth_user_id` (UUID, PRIMARY KEY) - Referencia a auth.users
- `username` (VARCHAR) - Nombre de usuario único
- `tipo_usuario` (VARCHAR) - 'apicultor' o 'cliente'
- `created_at` (TIMESTAMP) - Fecha de creación
- `updated_at` (TIMESTAMP) - Última actualización

#### **info_contacto**
- `id` (UUID, PRIMARY KEY)
- `auth_user_id` (UUID, FK) - Referencia a usuarios
- `nombre_completo` (VARCHAR)
- `correo_personal` (VARCHAR)
- `telefono` (VARCHAR)
- `direccion` (TEXT)
- `region` (VARCHAR)
- `comuna` (VARCHAR)

#### **ubicaciones**
- `id` (UUID, PRIMARY KEY)
- `auth_user_id` (UUID, FK) - Referencia a usuarios
- `nombre` (VARCHAR) - Nombre del apiario
- `descripcion` (TEXT)
- `latitud` (DECIMAL)
- `longitud` (DECIMAL)
- `norma_geo` (VARCHAR) - Código geográfico

#### **origenes_botanicos**
- `id` (UUID, PRIMARY KEY)
- `auth_user_id` (UUID, FK) - Referencia a usuarios
- `nombre_lote` (VARCHAR)
- `descripcion_flora` (TEXT)
- `sector_actividad` (VARCHAR)
- `composicion_polen` (JSON) - Análisis de polen
- `caracteristicas_organicas` (TEXT)
- `orden` (INTEGER) - Orden de visualización

#### **solicitudes_apicultor**
- `id` (UUID, PRIMARY KEY)
- `auth_user_id` (UUID, FK) - Referencia a usuarios
- `nombre_completo` (VARCHAR)
- `nombre_empresa` (VARCHAR)
- `region` (VARCHAR)
- `comuna` (VARCHAR)
- `telefono` (VARCHAR)
- `status` (VARCHAR) - 'pendiente', 'aprobado', 'rechazado'

## 🔍 Sistema de Búsqueda

### **Searcher - Motor de Búsqueda Avanzado**
- **Búsqueda Multi-tabla**: Usuarios, contactos, ubicaciones, lotes
- **Autocompletado Inteligente**: Sugerencias en tiempo real
- **Búsqueda por Segmento UUID**: Permite buscar con primeros 8 caracteres
- **Filtros Avanzados**: Por región, comuna, tipo de usuario

### **Endpoints de Búsqueda**
- `GET /api/search` - Búsqueda general
- `GET /sugerir` - Autocompletado de usuarios
- `GET /api/usuario/<uuid_segment>` - Redirección por segmento UUID
- `GET /profile/<uuid>` - Perfil público

## 📊 Sistema de Clasificación Botánica

### **Botanical Chart - Visualización Interactiva**
- **Gráficos Dinámicos**: Barras horizontales con porcentajes
- **Composición de Polen**: Visualización por especies
- **Carrusel de Lotes**: Navegación interactiva
- **Datos en Tiempo Real**: Actualización sin recargar página

### **Características**
- **Responsive Design**: Adaptable a móviles y tablets
- **Loading States**: Indicadores visuales durante carga
- **Cache de Composición**: Optimización de rendimiento
- **Acceso Público**: Sin autenticación para visualización

## 🏷️ Sistema de QR Codes

### **Generación Automática**
- **Perfiles Públicos**: QR único por usuario
- **Formato PNG**: Alta calidad para impresión
- **Enlace Directo**: Redirección al perfil público
- **API REST**: Generación programática

### **Endpoints QR**
- `GET /api/qr/<user_id>` - Generar QR de perfil
- `GET /api/qr/download/<user_id>` - Descargar QR

## 🎨 Frontend - Diseño y UX

### **Tecnologías**
- **Tailwind CSS**: Framework utility-first
- **JavaScript Vanilla**: Sin frameworks pesados
- **HTML5 Semántico**: Estructura accesible
- **Mobile-First**: Diseño responsive prioritario

### **Componentes Principales**
- **Botanical Chart**: Visualización de datos botánicos
- **Lotes Carousel**: Carrusel interactivo de lotes
- **Search Interface**: Búsqueda con autocompletado
- **Profile Cards**: Tarjetas de perfil optimizadas
- **Formularios Dinámicos**: Edición en tiempo real

## 🚀 Deployment y DevOps

### **Vercel Configuration**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### **Variables de Entorno Requeridas**
```bash
# Supabase
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon_key]

# Google OAuth
GOOGLE_CLIENT_ID=[client_id]
GOOGLE_CLIENT_SECRET=[client_secret]

# Flask
SECRET_KEY=[random_secret]
FLASK_ENV=production
```

### **Deployment Commands**
```bash
# Local development
python app.py

# Vercel deployment
vercel --prod
```

## 📈 Rendimiento y Optimización

### **Optimizaciones Implementadas**
- **Singleton Pattern**: Cliente Supabase único
- **Cache de Composición**: Datos botánicos cacheados
- **Lazy Loading**: Carga asíncrona de componentes
- **Compression**: Respuestas JSON comprimidas
- **CDN Ready**: Assets optimizados para CDN

### **Monitoreo**
- **Logging Estructurado**: Niveles DEBUG, INFO, ERROR
- **Health Checks**: Endpoints de estado
- **Performance Metrics**: Tiempos de respuesta
- **Error Tracking**: Logs centralizados

## 🔒 Seguridad

### **Medidas de Seguridad**
- **HTTPS Enforcement**: Solo conexiones seguras
- **CSRF Protection**: Tokens de seguridad
- **Input Validation**: Sanitización de datos
- **Rate Limiting**: Límites de solicitudes
- **Secure Headers**: Headers de seguridad HTTP

### **RLS Policies**
- **Políticas de Lectura Pública**: Para perfiles y lotes
- **Restricción de Escritura**: Solo usuarios autenticados
- **CASCADE DELETE**: Eliminación en cascada
- **Data Validation**: Reglas de integridad

## 🧪 Testing y QA

### **Estrategia de Testing**
- **Unit Tests**: Funciones individuales
- **Integration Tests**: Flujos completos
- **End-to-End**: Tests de usuario
- **Performance**: Carga y estrés

### **Herramientas de QA**
- **Postman**: Testing de API
- **Browser DevTools**: Debugging frontend
- **Supabase Dashboard**: Verificación de datos
- **Vercel Analytics**: Monitoreo en producción

## 📊 Métricas y KPIs

### **Métricas de Uso**
- **Usuarios Registrados**: Tracking por fecha
- **Búsquedas Realizadas**: Volumen y términos
- **Perfiles Vistos**: Interacción con perfiles
- **QR Codes Generados**: Uso del sistema QR

### **Performance Metrics**
- **Tiempo de Respuesta**: < 200ms para búsquedas
- **Uptime**: 99.9% objetivo
- **Error Rate**: < 0.1%
- **Cache Hit Rate**: > 80%

## 🔄 Flujos de Trabajo Principales

### **1. Registro de Nuevo Usuario**
1. Usuario accede a /register
2. Redirección a Google OAuth
3. Autenticación exitosa
4. Creación automática de perfil
5. Redirección a /editar-perfil

### **2. Búsqueda de Apicultores**
1. Usuario accede a página principal
2. Uso del buscador con autocompletado
3. Selección de resultado
4. Visualización de perfil público
5. Acceso a información de contacto

### **3. Gestión de Lotes**
1. Apicultor accede a /gestionar-lote
2. Creación/edición de lotes
3. Asignación de composición botánica
4. Generación de QR para lote
5. Publicación de información

## 🆘 Soporte y Troubleshooting

### **Problemas Comunes**
- **Error de Conexión**: Verificar variables de entorno
- **UUID Operator Error**: Ya resuelto en searcher.py
- **OAuth Callback**: Verificar URLs de redirección
- **Cache Issues**: Limpiar caché del navegador

### **Recursos de Soporte**
- **Logs de Aplicación**: Disponibles en consola
- **Supabase Logs**: Dashboard de Supabase
- **Vercel Logs**: Panel de Vercel
- **Community**: Documentación y foros

## 🚀 Roadmap Futuro

### **Características Planificadas**
- **Sistema de Reviews**: Valoraciones de apicultores
- **Chat en Tiempo Real**: Comunicación directa
- **Mapa Interactivo**: Visualización geográfica
- **App Móvil**: Versión nativa para iOS/Android
- **Analytics Dashboard**: Métricas para apicultores

### **Mejoras de Performance**
- **CDN Global**: Distribución de assets
- **Database Sharding**: Escalabilidad horizontal
- **Caching Strategy**: Redis para cache avanzado
- **Image Optimization**: WebP y lazy loading

---

## 📞 Contacto y Soporte

**Proyecto**: MeliAPP v3  
**Versión**: 3.0.0  
**Última Actualización**: 21 de agosto de 2025  
**Estado**: Producción Activa  
**URL Principal**: https://meli-app-v3.vercel.app  

**Equipo de Desarrollo**:  
- Backend: Flask + Supabase  
- Frontend: Tailwind CSS + JavaScript  
- Infraestructura: Vercel + Supabase  

---

*Este informe representa el estado actual completo del proyecto MeliAPP v3, incluyendo todas las optimizaciones, características y arquitectura implementadas hasta la fecha.*
