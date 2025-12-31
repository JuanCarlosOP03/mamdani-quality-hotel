# 📊 Sistema de Evaluación de Calidad de Servicio Hotelero con Lógica Difusa

Este proyecto implementa una **aplicación web desarrollada con Flask** que evalúa la **calidad del servicio hotelero** mediante un **controlador difuso (Fuzzy Logic Controller)**, utilizando encuestas estructuradas y un motor de inferencia basado en **scikit-fuzzy**.

El sistema permite:

* Capturar evaluaciones de usuarios a través de una encuesta web.
* Procesar los datos usando lógica difusa.
* Obtener un índice numérico (crisp) y una interpretación lingüística.
* Visualizar resultados individuales y globales mediante un módulo administrativo.

---

## 🧠 Fundamento del Proyecto

El modelo se basa en **cinco dimensiones de calidad del servicio**, evaluadas en una escala del 1 al 10:

* **Desempeño**
* **Eficiencia**
* **Eficacia**
* **Estabilidad**
* **Prevención de riesgos**

Estas variables se transforman en conjuntos difusos (bajo, medio, alto) y, mediante una **base de reglas lingüísticas**, se obtiene un nivel global de calidad del servicio hotelero.

---

## 🗂️ Estructura del Proyecto

```text
.
├── app.py
├── instance
│   └── encuesta_fuzzy.db
├── requirements.txt
└── templates
    ├── base.html
    ├── form.html
    ├── login.html
    ├── result.html
    └── results_global.html
```

### 📁 Descripción de Archivos

* **`app.py`**
  Archivo principal de la aplicación. Contiene:

  * Configuración de Flask y SQLAlchemy
  * Definición del modelo de datos
  * Motor de inferencia difusa
  * Rutas de la aplicación
  * Sistema de autenticación básica

* **`instance/encuesta_fuzzy.db`**
  Base de datos SQLite donde se almacenan las respuestas de la encuesta.

* **`requirements.txt`**
  Lista de dependencias necesarias para ejecutar el proyecto.

* **`templates/`**
  Plantillas HTML:

  * `base.html`: estructura general
  * `form.html`: formulario de encuesta
  * `result.html`: resultados individuales
  * `results_global.html`: resultados generales (admin)
  * `login.html`: acceso administrativo

---

## ⚙️ Tecnologías Utilizadas

* **Python 3**
* **Flask 3.1.2**
* **Flask-SQLAlchemy**
* **SQLite**
* **scikit-fuzzy**
* **NumPy**
* **SciPy**

---

## 🚀 Instalación y Ejecución

### 1️⃣ Clonar el proyecto

### 2️⃣ Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en:

```
http://localhost:5003
```

---

## 🧪 Funcionamiento del Sistema Difuso

### 🔹 Entradas (Antecedentes)

Cada dimensión se calcula como el **promedio** de sus reactivos:

* Desempeño → A1–A4
* Eficiencia → B1–B3
* Eficacia → C1–C3
* Estabilidad → D1–D2
* Prevención → E1–E2

### 🔹 Salida (Consecuente)

* **Calidad del servicio hotelero**
* Valores lingüísticos:

  * Muy bajo
  * Bajo
  * Medio
  * Alto
  * Muy alto

### 🔹 Resultado

El sistema entrega:

* Un valor **crisp** (numérico)
* Una **interpretación lingüística**
* El detalle de las entradas utilizadas

---

## 🔐 Módulo Administrativo

El sistema cuenta con un acceso protegido para visualizar resultados globales.

* **Ruta:** `/login`
* **Contraseña:**

```text
NdN6d.!d£5o6]NY
```

Desde el panel administrativo se pueden consultar:

* Correos de los participantes
* Fecha de respuesta
* Valor crisp
* Etiqueta difusa
* Promedios por dimensión

