---
título: "Plan Estratégico - Nuevo Diseño de Plantillas MeliAPP v2"
fecha: "2025-08-11"
autor: "askna"
descripción: "Plan estratégico para crear nuevas plantillas originales inspiradas en el análisis previo"
---

# 📋 Plan Estratégico - Nuevo Diseño de Plantillas

**Fecha:** 11 de agosto de 2025  
**Autor:** askna  
**Versión:** Estratégica  

## 🎯 Visión General

**Objetivo:** Crear un sistema de plantillas **completamente originales** que mantenga la simplicidad del backend mientras ofrece una experiencia visual moderna y coherente.

**Enfoque:** Diseño modular, inspirado en las mejores prácticas observadas, pero sin reutilizar código directamente.

---

## 🔍 Análisis de Inspiración

### 📊 Lecciones Aprendidas del Análisis Previo

| Elemento Observado | Inspiración para Nuevo Diseño |
|-------------------|------------------------------|
| **Tailwind CSS** actual | Mantener utility-first, pero con sistema de colores propio |
| **Bootstrap 5** en backups | Estructura modular, pero sin sobrecarga de clases |
| **Sistema de navegación** | Header sticky minimalista |
| **Cards de usuario** | Diseño de tarjetas más limpio |
| **Códigos QR** | Integración elegante sin complejidad |
| **Formularios** | Simplicidad máxima con validación visual |

---

## 🎨 Principios de Diseño

### 🎯 Principios Fundamentales

1. **Simplicidad Radical**
   - Una sola acción principal por página
   - Sin elementos decorativos innecesarios
   - Carga visual mínima

2. **Consistencia Visual**
   - Paleta de colores unificada
   - Tipografía única (Inter)
   - Espaciado basado en 8px grid

3. **Mobile-First**
   - Diseño primero para móvil
   - Escalado progresivo
   - Touch targets mínimos 44x44px

4. **Accesibilidad**
   - Contraste WCAG 2.1 AA
   - Navegación por teclado
   - Screen reader friendly

---

## 🏗️ Arquitectura de Plantillas

### 📁 Estructura Modular

```
templates/
├── base/
│   └── layout.html              # Plantilla base universal
├── pages/
│   ├── home.html                # Landing page
│   ├── search.html              # Buscador
│   ├── profile.html             # Perfil público
│   └── error.html               # Página de error
├── components/
│   ├── header.html              # Navegación responsive
│   ├── footer.html              # Footer minimalista
│   ├── search_form.html         # Formulario universal
│   └── user_card.html           # Tarjeta de usuario
└── layouts/
    └── minimal.html             # Layout sin navegación
```

---

## 🎨 Sistema de Diseño

### 🌈 Paleta de Colores

**Colores Principales:**
- **Fondo:** `#f8fafc` (slate-50)
- **Fondo Oscuro:** `#0f172a` (slate-900)
- **Primario:** `#f59e0b` (amber-500)
- **Secundario:** `#10b981` (emerald-500)
- **Texto Principal:** `#1e293b` (slate-800)
- **Texto Secundario:** `#64748b` (slate-500)

**Estados:**
- **Hover:** `amber-600`
- **Active:** `amber-700`
- **Disabled:** `slate-300`

### 🔤 Tipografía

**Familia:** Inter (Google Fonts)
**Pesos:** 400, 500, 600, 700
**Tamaños:**
- **H1:** 2.5rem (40px)
- **H2:** 2rem (32px)
- **H3:** 1.5rem (24px)
- **Body:** 1rem (16px)
- **Small:** 0.875rem (14px)

### 📏 Sistema de Espaciado

**Base:** 8px (0.5rem)
**Escalas:**
- **xs:** 0.25rem (2px)
- **sm:** 0.5rem (4px)
- **md:** 1rem (8px)
- **lg:** 1.5rem (12px)
- **xl:** 2rem (16px)
- **2xl:** 3rem (24px)
- **3xl:** 4rem (32px)

---

## 📄 Plantillas a Diseñar

### 1️⃣ `layout.html` - Plantilla Base

**Propósito:** Base universal para todas las páginas
**Elementos:**
- Header minimalista con logo
- Sistema de notificaciones
- Footer simple
- Meta tags SEO

**Decisiones de Diseño:**
- Header sticky con blur effect
- Logo texto "MeliAPP" en amber-500
- Menú hamburguesa en móvil
- Footer con links esenciales

### 2️⃣ `home.html` - Página Principal

**Propósito:** Landing page impactante
**Elementos:**
- Hero con gradiente sutil
- Buscador prominente
- Estadísticas simples
- CTA secundario

**Decisiones de Diseño:**
- Hero ocupando 80vh
- Buscador centrado con icono
- Estadísticas en cards minimalistas
- Sin carrusel ni animaciones complejas

### 3️⃣ `search.html` - Buscador

**Propósito:** Interfaz de búsqueda intuitiva
**Elementos:**
- Barra de búsqueda fija
- Filtros colapsables
- Resultados en grid
- Paginación simple

**Decisiones de Diseño:**
- Búsqueda en tiempo real (sin página)
- Filtros como tags removibles
- Resultados en tarjetas uniformes
- Loading skeleton

### 4️⃣ `profile.html` - Perfil Público

**Propósito:** Tarjeta de presentación digital
**Elementos:**
- Foto avatar circular
- Información jerárquica
- Ubicación en mapa
- Código QR elegante
- Botón de contacto

**Decisiones de Diseño:**
- Avatar con iniciales si no hay foto
- Información en secciones colapsables
- Mapa estático de Google Maps
- QR con marco decorativo

---

## 🧩 Componentes Reutilizables

### 🔍 `search_form.html`
**Función:** Formulario de búsqueda universal
**Elementos:**
- Input con icono de lupa
- Placeholder contextual
- Botón de búsqueda solo en desktop
- Focus states elegantes

### 👤 `user_card.html`
**Función:** Tarjeta de usuario estándar
**Elementos:**
- Avatar circular
- Nombre y ubicación
- Tags de especialidad
- Hover effect sutil

### 📱 `mobile_menu.html`
**Función:** Menú móvil off-canvas
**Elementos:**
- Overlay oscuro
- Links principales
- Cierre con swipe
- Animación suave

---

## 📱 Responsive Strategy

### 📊 Breakpoints
- **Mobile:** < 640px
- **Tablet:** 640px - 768px
- **Desktop:** 768px - 1024px
- **Large:** > 1024px

### 🎯 Adaptaciones por Dispositivo

| Dispositivo | Layout | Navegación | Contenido |
|-------------|--------|------------|-----------|
| **Mobile** | Single column | Bottom nav | Cards apiladas |
| **Tablet** | 2 columnas | Sidebar colapsable | Grid 2x2 |
| **Desktop** | 3 columnas | Top nav fijo | Grid 3x3 |

---

## 🚀 Plan de Implementación

### 📅 Fase 1: Diseño (3 días)
**Día 1:** Sistema de diseño y layout base
**Día 2:** Página principal y componentes
**Día 3:** Páginas restantes y responsive

### 📅 Fase 2: Desarrollo (4 días)
**Día 4:** HTML base y Tailwind setup
**Día 5:** Componentes reutilizables
**Día 6:** Integración con endpoints
**Día 7:** Testing responsive

### 📅 Fase 3: Optimización (3 días)
**Día 8:** Performance y accesibilidad
**Día 9:** Cross-browser testing
**Día 10:** Documentación final

---

## 📋 Checklist de Diseño

### ✅ Diseño Visual
- [ ] Definir sistema de colores final
- [ ] Crear component library
- [ ] Diseñar iconografía
- [ ] Establecer guidelines de espaciado

### ✅ Experiencia de Usuario
- [ ] Mapear flujos de usuario
- [ ] Definir estados de carga
- [ ] Planear mensajes de error
- [ ] Diseñar feedback visual

### ✅ Responsive
- [ ] Wireframes mobile
- [ ] Wireframes tablet
- [ ] Wireframes desktop
- [ ] Prototipo interactivo

### ✅ Accesibilidad
- [ ] Auditoría de contraste
- [ ] Navegación por teclado
- [ ] Screen reader testing
- [ ] Documentación de accesibilidad

---

## 🎯 Métricas de Éxito

### 📊 KPIs de Diseño
- **Lighthouse Score:** > 95
- **Mobile First:** Diseño optimizado para móvil
- **Tiempo de carga:** < 2 segundos
- **Accesibilidad:** WCAG 2.1 AA

### 🎨 Coherencia Visual
- **Consistencia de colores:** 100%
- **Consistencia tipográfica:** 100%
- **Consistencia de espaciado:** 100%
- **Responsive coverage:** 100%

---

## 📝 Próximos Pasos

1. **Aprobación del plan:** Validar dirección con usuario
2. **Diseño de wireframes:** Crear prototipos básicos
3. **Sistema de diseño:** Documentar decisiones
4. **Implementación progresiva:** Comenzar con layout base

**Nota:** Este plan mantiene la filosofía de simplicidad del backend mientras crea una experiencia visual moderna y coherente.
