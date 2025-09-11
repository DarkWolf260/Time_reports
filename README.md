# Time Reports - Aplicación de Reportes Meteorológicos

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg) ![Flet](https://img.shields.io/badge/Flet-0.24.0%2B-green.svg) ![License](https://img.shields.io/badge/License-Uso%20Interno-red.svg) ![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

Una aplicación moderna y elegante creada con Flet para generar reportes del estado del tiempo de Protección Civil Municipales.

## 🚀 Características

- **Interfaz moderna**: Diseño limpio inspirado en Windows 11
- **Tema claro/oscuro**: Soporte completo para temas con persistencia
- **Gestión de operadores**: Sistema completo para administrar operadores
- **Generación automática**: Reportes con formato profesional y fecha/hora actual
- **Copia rápida**: Un clic para copiar el reporte al portapapeles
- **Arquitectura limpia**: Código bien estructurado y mantenible

## 🌟 Futuras Mejoras

- [ ] **Notificaciones**: Alertas de escritorio para que no olvides los reportes.

## 📁 Estructura del Proyecto

```
time_reports/
├── src/
│   ├── assets/              # Iconos y otros recursos
│   ├── config.py            # Configuración y constantes
│   ├── main.py              # Aplicación principal
│   ├── models.py            # Lógica de datos y modelos
│   ├── styles.py            # Estilos y temas
│   └── ui_components.py     # Componentes de UI reutilizables
├── storage/
│   ├── municipios.json      # Lista de municipios
│   └── operadores.json      # Base de datos de operadores
├── README.md                # Documentación
└── pyproject.toml           # Configuración del proyecto
```

## 🛠️ Instalación

1. **Instalar Python 3.8 o superior**

2. **Instalar Flet**:
   ```bash
   pip install flet
   ```

3. **Ejecutar la aplicación**:
   ```bash
   python src/main.py
   ```

## 📱 Uso de la Aplicación

### Generar un Reporte

1. **Seleccionar estado del tiempo**: Usa el dropdown superior para elegir las condiciones meteorológicas actuales
2. **Seleccionar operador**: Escoge quién realiza el reporte
3. **Copiar reporte**: Haz clic en "Copiar al Portapapeles" para obtener el reporte formateado

### Gestionar Operadores

1. **Abrir gestión**: Haz clic en "Gestionar operadores"
2. **Agregar operador**: 
   - Completa nombre, cédula, cargo y jerarquía
   - Haz clic en "Añadir"
3. **Eliminar operador**:
   - Selecciona el operador en el dropdown inferior
   - Haz clic en "Eliminar"

### Cambiar Tema

- Haz clic en el botón de sol/luna en la esquina superior derecha
- El tema se guarda automáticamente para futuras sesiones

## 🏗️ Arquitectura

### Separación de Responsabilidades

- **`config.py`**: Todas las constantes y configuraciones centralizadas
- **`models.py`**: Lógica de negocio, manejo de datos y estado de la aplicación
- **`styles.py`**: Sistema completo de temas y estilos reutilizables
- **`ui_components.py`**: Componentes de interfaz modulares y reutilizables
- **`main.py`**: Orquestación de la aplicación y configuración principal

### Clases Principales

#### `AppState`
Maneja el estado global de la aplicación, incluyendo:
- Gestión de operadores
- Estado actual del tiempo
- Operador seleccionado
- Tema actual

#### `OperadorManager`
Sistema completo para gestionar operadores:
- Carga y guardado en JSON
- Validaciones de datos
- Búsquedas por nombre/cédula
- Operaciones CRUD

#### `ReportGenerator`
Generador de reportes con:
- Formato profesional
- Fecha y hora automática
- Conversión de markdown a texto enriquecido

### Componentes UI

- **`ThemeToggleButton`**: Botón inteligente para cambio de tema
- **`ReportDisplay`**: Visualización de reportes con formato rico
- **`WeatherSelector`**: Selector de estados meteorológicos
- **`OperatorSelector`**: Selector de operadores con actualización automática
- **`OperatorManagementDialog`**: Diálogo completo para gestión de operadores
- **`ActionButtons`**: Botones de acción principales

## 🎨 Sistema de Estilos

### Temas
- **Tema claro**: Colores suaves y profesionales
- **Tema oscuro**: Diseño moderno con buen contraste
- **Persistencia**: El tema se guarda automáticamente

### Componentes Estilizados
- Botones con hover effects
- Inputs con focus states
- Contenedores con sombras sutiles
- Tipografía consistente (Segoe UI)

## 📊 Formato del Reporte

Los reportes generados siguen este formato estándar:

```
*PROTECCIÓN CIVIL MUNICIPIO GUANTA* 🚨

*·   REPORTE DEL ESTADO DEL TIEMPO:* [emoji]
*·   FECHA:* [dd/mm/yyyy]
*·   HORA:* [hh:mm] HLV

*·   DESCRIPCIÓN:* [estado meteorológico]

*·   NOVEDAD:* Sin novedades para la hora.

*·   REPORTA:* [cargo] [jerarquía] [nombre] [cédula]

*SOLO QUEREMOS SALVAR VIDAS 🚨🚑*
```

## 💾 Persistencia de Datos

- **Operadores**: Guardados automáticamente en `operadores.json`
- **Tema**: Almacenado en el storage del cliente
- **Formato**: JSON con encoding UTF-8 para soporte de caracteres especiales

## 🔧 Configuración

Todas las configuraciones se encuentran en `config.py`:

- Estados del tiempo disponibles
- Cargos y jerarquías
- Configuración de ventana
- Rutas de archivos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 👨‍💻 Autor

**Rubén Rojas** - Desarrollo y refactorización

## 📄 Licencia

Este proyecto está bajo una licencia de uso interno.

## 🆕 Mejoras en la Refactorización

### ✅ Código Limpio
- Separación clara de responsabilidades
- Clases y funciones con propósito único
- Nombres descriptivos y consistentes
- Documentación completa

### ✅ Arquitectura Mejorada
- Patrón MVC implementado
- Componentes reutilizables
- Estado centralizado
- Manejo de errores robusto

### ✅ Mantenibilidad
- Código modular y extensible
- Fácil agregar nuevos estados meteorológicos
- Sistema de estilos centralizado
- Testing preparado

### ✅ Experiencia de Usuario
- Interfaz más responsive
- Feedback visual mejorado
- Tema persistente
- Validaciones de datos

---

*Aplicación creada para facilitar la generación de reportes meteorológicos de manera rápida y profesional.*
