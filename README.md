# 🏛️ Planificador Municipal

Aplicación web construida con **Flask** que ayuda a municipios a realizar diagnósticos, construir Árbol de Problemas, Marco Lógico, y generar planes municipales. También incluye cursos y herramientas para funcionarios y estudiantes.

---

## 🚀 Funcionalidades principales

- 📊 Diagnóstico automático por municipio
- 🌳 Árbol de Problemas y Árbol de Objetivos interactivo
- 📐 Matriz de Marco Lógico editable
- 📥 Exportación a PDF y Word
- 🎓 Cursos en línea con videos y PDFs
- 🤖 Chatbot inteligente entrenado con documentos PDF
- 🔐 Registro, login y control de acceso

---

## 📦 Requisitos

- Python 3.8 o superior
- Git
- Virtualenv (opcional pero recomendado)

---

## ⚙️ Instalación local

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/planificador-municipal.git
cd planificador-municipal

# 2. Crea entorno virtual (opcional)
python -m venv venv
venv\Scripts\activate     # En Windows
# source venv/bin/activate  # En Linux/Mac

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Ejecuta la aplicación
python app.py
