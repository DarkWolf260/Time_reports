# Time Reports - Aplicación de Reportes Meteorológicos

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg) ![Flet](https://img.shields.io/badge/Flet-0.28.3-green.svg) ![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

Una aplicación moderna y elegante creada con Flet para generar reportes del estado del tiempo de Protección Civil Municipales.

## 🚀 Características

- **Interfaz moderna**: Diseño limpio inspirado en Windows 11.
- **Tema claro/oscuro**: Soporte completo para temas con persistencia.
- **Gestión de operadores**: Sistema completo para administrar operadores.
- **Generación automática**: Reportes con formato profesional y fecha/hora actual.
- **Copia rápida**: Un clic para copiar el reporte al portapapeles.
- **Arquitectura limpia**: Código bien estructurado y mantenible.
- **Ajustes de configuración**: Guarda el municipio y departamento de forma persistente.
- **Diálogo 'Acerca de'**: Información de la versión y créditos.

## 🌟 Futuras Mejoras

- [ ] **Notificaciones**: Alertas de escritorio para que no olvides los reportes.

## 📁 Estructura del Proyecto

```
.
├── .gitignore
├── README.md
├── pyproject.toml
├── requeriments.txt
└── src/
    ├── assets/
    │   ├── icon.png
    │   └── splash_android.png
    ├── config.py
    ├── main.py
    ├── models.py
    ├── styles.py
    └── ui_components.py
```

## 🛠️ Instalación

1.  **Instalar Python 3.9 o superior.**

2.  **Clonar el repositorio e instalar dependencias:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd <NOMBRE-DEL-DIRECTORIO>
    pip install -r requeriments.txt
    ```

3.  **Ejecutar la aplicación**:
    ```bash
    python src/main.py
    ```

## 📱 Uso de la Aplicación

### Configuración Inicial

Antes de generar un reporte, puedes configurar tu municipio y departamento por defecto:

1.  **Abrir Configuración**: Haz clic en el icono de engranaje (⚙️) en la barra superior.
2.  **Establecer valores**: Selecciona tu municipio y departamento en los menús desplegables.
3.  **Guardar**: Haz clic en "Guardar" para aplicar los cambios.

Estos valores se guardarán para futuras sesiones.

### Generar un Reporte

1.  **Seleccionar estado del tiempo**: Usa el dropdown superior para elegir las condiciones meteorológicas actuales.
2.  **Seleccionar operador**: Escoge quién realiza el reporte.
3.  **Copiar reporte**: Haz clic en "Copiar al Portapapeles" para obtener el reporte formateado.

### Gestionar Operadores

1.  **Abrir gestión**: Haz clic en "Gestionar operadores".
2.  **Agregar operador**:
    -   Completa nombre, cédula, cargo y jerarquía.
    -   Haz clic en "Añadir".
3.  **Eliminar operador**:
    -   Selecciona el operador en el dropdown inferior.
    -   Haz clic en "Eliminar".

### Cambiar Tema

-   Haz clic en el botón de sol/luna en la esquina superior derecha.
-   El tema se guarda automáticamente para futuras sesiones.

### Acerca de

-   Para ver la información de la aplicación, haz clic en el icono de información (ℹ️) en la barra superior.
-   Se mostrará una ventana con los créditos y la versión de la aplicación.

## 🏗️ Arquitectura

### Separación de Responsabilidades

-   **`config.py`**: Todas las constantes y configuraciones centralizadas (listas de tiempo, cargos, jerarquías, municipios, etc.).
-   **`models.py`**: Lógica de negocio, manejo de datos y estado de la aplicación.
-   **`styles.py`**: Sistema completo de temas y estilos reutilizables.
-   **`ui_components.py`**: Componentes de interfaz modulares y reutilizables.
-   **`main.py`**: Orquestación de la aplicación y configuración principal.

### Clases Principales

#### `AppState`
Maneja el estado global de la aplicación, incluyendo la gestión de operadores, el estado del tiempo, el operador seleccionado y el tema actual.

#### `OperadorManager`
Sistema para gestionar operadores con carga y guardado a través del almacenamiento del cliente de Flet (`client_storage`).

#### `ReportGenerator`
Generador de reportes con formato profesional y fecha y hora automática.

## 💾 Persistencia de Datos

-   **Operadores y Configuración**: Los datos de los operadores, el tema seleccionado, el municipio y el departamento se guardan en el almacenamiento local del cliente (`client_storage`) que provee Flet. No se utilizan archivos `.json` externos para la persistencia.
-   **Portabilidad**: Gracias al uso de `client_storage`, la configuración es persistente entre sesiones en la misma máquina.

## 🔧 Configuración

Todas las configuraciones principales y listas de datos (estados del tiempo, cargos, jerarquías, municipios) se encuentran centralizadas como listas en `src/config.py`, facilitando su modificación y mantenimiento.

## 🤝 Contribuir

1.  Fork el proyecto.
2.  Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`).
3.  Commit tus cambios (`git commit -m 'Add some AmazingFeature'`).
4.  Push a la rama (`git push origin feature/AmazingFeature`).
5.  Abre un Pull Request.

## 👨‍💻 Autor

**Rubén Rojas** - Desarrollo y refactorización

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
