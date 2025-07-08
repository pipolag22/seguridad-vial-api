# 🚀 API de Gestión de Cursos de Seguridad Vial

Este proyecto implementa una API HTTP RESTful utilizando FastAPI para gestionar datos relacionados con cursos de seguridad vial. Permite la administración de personas, cursos, inspectores, jueces, inscripciones a cursos y usuarios, incluyendo un robusto sistema de autenticación y autorización basado en roles.


## 📋 Tabla de Contenidos

* [Introducción](#-introducción)
* [Características](#-características)
* [Tecnologías Utilizadas](#-tecnologías-utilizadas)
* [Estructura del Proyecto](#-estructura-del-proyecto)
* [Configuración e Instalación Local](#-configuración-e-instalación-local)
    * [Prerrequisitos](#prerrequisitos)
    * [Clonar el Repositorio](#clonar-el-repositorio)
    * [Configurar el Entorno Virtual](#configurar-el-entorno-virtual)
    * [Instalar Dependencias](#instalar-dependencias)
    * [Inicializar la Base de Datos](#inicializar-la-base-de-datos)
    * [Crear Usuario Administrador](#crear-usuario-administrador)
* [Ejecutar la Aplicación](#-ejecutar-la-aplicación)
* [Documentación de la API](#-documentación-de-la-api)
* [Autenticación y Autorización](#-autenticación-y-autorización)
* [Lógica de Negocio / Transformación de Datos](#-lógica-de-negocio--transformación-de-datos)
* [Pruebas](#-pruebas)
* [Proceso de Desarrollo y Decisiones de Diseño](#-proceso-de-desarrollo-y-decisiones-de-diseño)
* [Futuras Mejoras](#-futuras-mejoras)
* [Autor](#-autor)

---

## 💡 Introducción

El objetivo es una API de cursos de seguridad vial, donde los usuarios pueden realizar el curso en línea y presentar ante un juez (que previamente se lo solicita para regularizar algunas infracciones de tránsito) y ante inspectores de seguridad (que se lo pueden solicitar para renovación de licencia de conducir por vencimiento de licencia o para obtener por primera vez la licencia de conducir como principiante). El sistema gestiona las inscripciones a estos cursos, aplicando reglas de negocio sobre su **validez y vencimiento**, y permite a los actores clave (inspectores, jueces) interactuar con su estado.

---

---

## ✨ Características

Características

* **API RESTful:** Implementada con FastAPI para endpoints claros y eficientes.
* **Gestión de Datos:** Operaciones CRUD completas para:
    * Personas
    * Cursos de Seguridad Vial
    * Inspectores
    * Jueces
    * Inscripciones a Cursos
    * Usuarios
* **Base de Datos:** SQLite utilizada como base de datos ligera para desarrollo, con un diseño desde cero usando SQLModel.
* **Autenticación:** Implementación de JWT (JSON Web Tokens) a través de OAuth2 Password Bearer.
* **Autorización Basada en Roles:** Control de acceso a los endpoints según el rol del usuario (Admin, Inspector, Juez, Normal).
* **Modularidad:** Código organizado en módulos separados para routers, servicios, modelos y configuración.
* **Validación de Datos:** Uso de Pydantic/SQLModel para validación automática de datos de entrada y salida.
* **Documentación Interactiva:** Generación automática de Swagger UI (`/docs`) y ReDoc (`/redoc`).
* **Healthcheck:** Endpoint para verificar la salud del servicio y la conexión a la base de datos.
* **Contenedorización:** `Dockerfile` incluido para facilitar el despliegue en entornos Docker.
* **Lógica de Vencimiento de Inscripciones:** Implementación de reglas de negocio para el cálculo automático y la gestión del vencimiento y finalización de inscripciones a cursos.

## 🛠️ Tecnologías Utilizadas

* **Python:** Lenguaje de programación principal.
* **FastAPI:** Framework web para construir la API.
* **SQLModel:** Librería para interactuar con la base de datos (ORMs y modelos Pydantic).
* **Uvicorn:** Servidor ASGI para ejecutar la aplicación FastAPI.
* **SQLite:** Base de datos relacional ligera (archivo `.db`).
* **Passlib & bcrypt:** Para el hashing seguro de contraseñas.
* **python-jose[cryptography]:** Para la gestión de JWT.
* **python-dotenv:** Para la gestión de variables de entorno (aunque no se use directamente en `main`, es buena práctica tenerla para futuras configs).
* **Git & GitHub:** Control de versiones y alojamiento del código.

---

## 📁 Estructura del Proyecto

El proyecto sigue una estructura modular para una mejor organización y separación de responsabilidades:
├── app/
│   ├── init.py
│   ├── config/             # Configuración de la aplicación (ej. base de datos)
│   │   ├── init.py
│   │   └── database.py
│   ├── models/             # Definiciones de modelos de datos (SQLModel y Pydantic)
│   │   ├── init.py
│   │   ├── person.py
│   │   ├── traffic_safety_course.py
│   │   ├── inspector.py
│   │   ├── judge.py
│   │   ├── course_enrollment.py
│   │   └── user.py
│   ├── routers/            # Endpoints de la API (APIRouter)
│   │   ├── init.py
│   │   ├── person_router.py
│   │   ├── traffic_safety_course_router.py
│   │   ├── course_enrollment_router.py
│   │   ├── inspector_router.py
│   │   ├── judge_router.py
│   │   └── user_router.py
│   ├── services/           # Lógica de negocio y operaciones de DB (funciones CRUD)
│   │   ├── init.py
│   │   ├── traffic_safety_course_service.py
│   │   ├── user_service.py
│   │   └── # ... otros servicios (person_service.py, etc.)
│   ├── security/           # Lógica de seguridad (hashing, JWT)
│   │   ├── init.py
│   │   └── security.py
│   │    tests/
│   │       └── test_main.py
│   └── main.py             # Punto de entrada de la aplicación FastAPI
├── create_admin.py         # Script para inicializar un usuario administrador
├── Dockerfile              # Archivo para construir la imagen Docker
├── requirements.txt        # Dependencias del proyecto
└── README.md               

## 📊 Lógica de Negocio / Transformación de Datos

Uno de los requisitos clave del desafío es la implementación de una **transformación de datos basada en un requisito de negocio**. En este proyecto, se ha implementado la siguiente lógica:

### Gestión Automática y Manual de Vencimientos de Inscripciones

Las inscripciones a cursos (`CourseEnrollment`) ahora manejan un ciclo de vida con fechas de vencimiento dinámicas, aplicando las siguientes reglas:

1.  **Vencimiento Inicial (90 días):** Al crear una nueva inscripción (`POST /course-enrollments/`), si no se especifica una `expiration_date`, esta se calcula automáticamente 90 días después de la `enrollment_date`.
2.  **Vencimiento por Finalización (60 días post-completado):** Cuando un Inspector o Juez marca una inscripción como `COMPLETED` (`PUT /course-enrollments/{id}/complete`), la `completion_date` se establece al día actual y la `expiration_date` se recalcula automáticamente a 60 días después de la `completion_date`. Esto simula un período de validez del curso una vez finalizado.
3.  **Vencimiento por Acción Directa (Inspector/Juez):** Un Inspector o Juez puede forzar el estado de una inscripción a `EXPIRED` (`PUT /course-enrollments/{id}/expire-by-action`), estableciendo la `expiration_date` al día actual.

### Reporte de Inscripciones Próximas a Vencer o Vencidas

Se ha implementado un endpoint específico que actúa como una **transformación de datos de negocio**:

* **Endpoint:** `GET /course-enrollments/reports/expiring-or-expired`
* **Descripción:** Este endpoint genera un informe de todas las inscripciones a cursos que están próximas a vencer (por defecto, en los próximos 30 días, configurable mediante un parámetro `days_until_expiration`) o que ya han vencido.
* **Transformación:** Para cada inscripción, el reporte combina y presenta datos de múltiples entidades:
    * Detalles de la inscripción (`id`, `enrollment_date`, `expiration_date`, `status`, `notes`).
    * Detalles completos de la **Persona** inscrita (nombre, apellido, DNI, etc.).
    * Detalles completos del **Curso de Seguridad Vial** (nombre, descripción, etc.).
    * Calcula y añade campos auxiliares como `days_until_expiration` (días restantes para vencer) y `is_expired` (booleano que indica si ya venció), proporcionando una visión consolidada y útil para el negocio.
* **Roles:** Este reporte es accesible por usuarios con rol `ADMIN` o `INSPECTOR`.

## 🚧 Proceso de Desarrollo y Decisiones de Diseño

El desarrollo de esta API siguió un enfoque iterativo y modular, priorizando la claridad del código y el cumplimiento de los requisitos clave del desafío.

1.  **Fase Inicial (Setup y Base CRUD):**
    * **Configuración del Repositorio:** Se inició con la creación de un repositorio de GitHub y la configuración inicial del proyecto.
    * **Base de Datos y Modelos:** Se diseñó el esquema de la base de datos con al menos 4 tablas (Persona, Curso, Inscripción, Usuario, Inspector, Juez) utilizando SQLModel, lo que permitió definir tanto los modelos ORM como los esquemas Pydantic para la API.
    * **Operaciones CRUD Básicas:** Se implementaron los endpoints y servicios CRUD para las entidades principales, asegurando la funcionalidad básica de la API (crear, leer, actualizar, eliminar).

2.  **Seguridad (Autenticación y Autorización):**
    * Se integró un sistema robusto de autenticación basado en JWT y OAuth2 Password Bearer.
    * Se definieron y aplicaron roles de usuario (Admin, Inspector, Juez, Normal) para controlar el acceso a los diferentes endpoints, garantizando que solo usuarios autorizados puedan realizar ciertas operaciones.
    * Se creó un script `create_admin.py` para la fácil inicialización del primer usuario administrador.

3.  **Contenedorización y Despliegue:**
    * Se desarrolló un `Dockerfile` para empaquetar la aplicación y sus dependencias, facilitando la ejecución consistente en cualquier entorno Docker. Se incluyeron herramientas de compilación (`git`, `build-essential`) para asegurar la correcta instalación de todas las dependencias dentro del contenedor.

4.  **Implementación de Lógica de Negocio Avanzada / Transformación de Datos:**
    * Se abordó el requisito obligatorio de "transformación de datos de negocio" con la implementación de un sistema de gestión de vencimientos para las inscripciones a cursos. Esto incluyó:
        * Cálculo automático de la fecha de vencimiento inicial (90 días).
        * Actualización de la fecha de vencimiento al completar el curso (60 días post-finalización).
        * Funcionalidad para que roles específicos (Inspector, Juez) puedan marcar una inscripción como expirada directamente.
    * Se creó un endpoint de reporte (`/course-enrollments/reports/expiring-or-expired`) que consolida información de múltiples tablas y aplica lógica de filtrado de fechas, demostrando la capacidad de transformar y presentar datos complejos de manera útil para el negocio.

5.  **Próximos Pasos Identificados:**
    * La siguiente fase crítica del proyecto es la implementación de pruebas unitarias y de integración, tal como se detalla en la sección de [Pruebas](#-pruebas), para asegurar la calidad y el comportamiento esperado de la API.
    * Refinar la documentación OpenAPI generada automáticamente (`/docs`) añadiendo `summary` y `description` más detallados a todos los endpoints.

**Decisiones de Diseño Clave:**

* **Modularidad:** La separación en `routers`, `services`, `models`, y `security` promueve un código limpio, mantenible y escalable.
* **SQLModel:** Elegido por su capacidad de combinar ORM y validación Pydantic, reduciendo la redundancia y mejorando la consistencia entre la base de datos y la API.
* **Autenticación por Roles:** Implementación manual para tener control total sobre la lógica y demostrar comprensión de OAuth2 y JWT.
* **Transformación de Datos en Servicio:** La lógica compleja de negocio se encapsula en la capa de servicios, manteniendo los routers "delgados" y enfocados en la orquestación HTTP.