# 🔄 Renombrado de Proyecto: MeliAPP v3 → MeliAPP Cloud

## ✅ Cambios Realizados

### 1. Archivos de Configuración
- ✅ `.env` - BASE_URL actualizada a `https://meliapp-cloud.vercel.app`
- ✅ `app.py` - Dominio personalizado y mensaje de bienvenida
- ✅ `vercel.json` - Sin cambios necesarios (agnóstico al nombre)

### 2. Documentación
- ✅ `docs/CONFIGURACION_PRODUCCION.md` - Todas las URLs y referencias actualizadas
- ✅ `docs/CHECKLIST_DESPLIEGUE.md` - URLs y nombre del proyecto actualizados
- ✅ `verify_production_config.py` - Script de verificación actualizado

### 3. Templates
- ✅ `templates/pages/home.html` - Título cambiado a "MeliAPP Cloud"

### 4. Código Backend
- ✅ `app.py` - Función `get_base_url()` con nuevo dominio
- ✅ `app.py` - Mensaje de bienvenida actualizado

---

## 📋 ACCIONES REQUERIDAS EN SERVICIOS EXTERNOS

### 🔴 CRÍTICO: Configuración de Supabase Dashboard

1. **Authentication → URL Configuration**
   ```
   Site URL: https://meliapp-cloud.vercel.app
   ```

2. **Redirect URLs** (agregar todas):
   ```
   https://meliapp-cloud.vercel.app/auth/callback
   https://meliapp-cloud.vercel.app/auth/callback-js
   http://localhost:3000/auth/callback (desarrollo)
   http://localhost:3000/auth/callback-js (desarrollo)
   ```

---

### 🔴 CRÍTICO: Configuración de Vercel

#### Opción A: Renombrar Proyecto Existente
1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Selecciona el proyecto actual
3. Settings → General → Project Name
4. Cambiar a: **meliapp-cloud**
5. Save

#### Opción B: Crear Nuevo Proyecto
1. Crear nuevo proyecto en Vercel con nombre **meliapp-cloud**
2. Conectar al mismo repositorio GitHub
3. Configurar TODAS las variables de entorno (ver abajo)
4. Deploy

#### Variables de Entorno Requeridas:
```bash
BASE_URL=https://meliapp-cloud.vercel.app
SUPABASE_URL=https://jrduviahstserdwtfkft.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZHV2aWFoc3RzZXJkd3Rma2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2NDAxMDQsImV4cCI6MjA2MjIxNjEwNH0.YkDb2yXbYeaQp2G8tEsoysjfTeBynUzUFjnIkqdW3FY
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZHV2aWFoc3RzZXJkd3Rma2Z0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjY0MDEwNCwiZXhwIjoyMDYyMjE2MTA0fQ.JSHyvSbalhzKy6zFfsZJiSdtqjgnz_q6cxIx2-1NKOQ
SECRET_KEY=79be58ff754c48a08433c5cb552a389bf42f43ba6d814cb350707a7ec13596c1
FLASK_ENV=production
RESEND_API_KEY=re_MZ9Ld2pS_ML5DtuXUV4PWgaFg5DKUgbyZ
```

---

### 🟡 OPCIONAL: Google OAuth Console

Solo si usas Google OAuth:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edita tus credenciales OAuth 2.0
3. **Authorized redirect URIs** - AGREGAR (mantén las anteriores también):
   ```
   https://meliapp-cloud.vercel.app/auth/callback
   https://meliapp-cloud.vercel.app/auth/callback-js
   ```

⚠️ **NOTA:** Puedes mantener las URLs antiguas de `meli-app-v3` por un tiempo para no romper nada.

---

## 🚀 Proceso de Despliegue

### Paso 1: Commit y Push
```bash
git add .
git commit -m "Renombrado: MeliAPP v3 → MeliAPP Cloud"
git push origin main
```

### Paso 2: Configurar Vercel
- Renombrar proyecto O crear uno nuevo (ver arriba)
- Configurar variables de entorno
- Esperar auto-deploy

### Paso 3: Configurar Supabase
- Actualizar Site URL
- Agregar Redirect URLs

### Paso 4: Verificar
```bash
python verify_production_config.py
```

### Paso 5: Testing
- Visitar: https://meliapp-cloud.vercel.app
- Probar registro de usuario
- Probar login
- Probar OAuth (si aplica)

---

## 📊 URLs Antes y Después

| Servicio | URL Anterior | URL Nueva |
|----------|-------------|-----------|
| Producción | `https://meli-app-v3.vercel.app` | `https://meliapp-cloud.vercel.app` |
| Desarrollo | `http://127.0.0.1:3000` | `http://127.0.0.1:3000` (sin cambios) |
| Callback OAuth | `/auth/callback` | `/auth/callback` (sin cambios) |

---

## ⚠️ IMPORTANTE: Transición Sin Downtime

Si quieres evitar downtime durante la transición:

1. **Crear NUEVO proyecto** en Vercel con nombre `meliapp-cloud`
2. **Mantener proyecto antiguo** `meli-app-v3` activo temporalmente
3. **Configurar Supabase** para aceptar AMBAS URLs:
   - `https://meli-app-v3.vercel.app/*`
   - `https://meliapp-cloud.vercel.app/*`
4. **Testing completo** en nuevo dominio
5. **Cuando todo funcione**, eliminar proyecto antiguo

---

## ✅ Checklist Final

### En Código (Completado)
- [x] `.env` actualizado
- [x] `app.py` actualizado
- [x] Documentación actualizada
- [x] Templates actualizados
- [x] Script de verificación actualizado

### En Vercel (Pendiente)
- [ ] Proyecto renombrado o creado
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso
- [ ] URL funcional

### En Supabase (Pendiente)
- [ ] Site URL actualizada
- [ ] Redirect URLs actualizadas
- [ ] Configuración guardada

### Testing (Pendiente)
- [ ] Home page carga
- [ ] Registro funciona
- [ ] Login funciona
- [ ] OAuth funciona (si aplica)

---

**Creado:** Noviembre 2025  
**Proyecto:** MeliAPP Cloud  
**Documentos relacionados:**
- `docs/CONFIGURACION_PRODUCCION.md`
- `docs/CHECKLIST_DESPLIEGUE.md`
