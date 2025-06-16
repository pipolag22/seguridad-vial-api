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

 El objetivo es una API de cursos de seguridad vial, donde los usuarios pueden realizar el curso en linea y presentar ante un juez(que previamente se lo solicita para regularizar algunas infracciones de transito) y ante inspectores de seguridad (que se lo pueden solicitar para renovacion de licencia de conducir por vencimiento de licencia o para obtener por primera vez la licencia de conducir como principiante)

---

## ✨ Características

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

---

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