# 🔒 Cortapis Security System

**Cortapis** es un sistema avanzado de encriptación y ofuscación de texto diseñado para proteger contenido sensible contra la indexación por IA y buscadores.

## 📋 Conceptos Principales

### El Problema
La reciente comercialización masiva de la IA ha llevado a que se indexe prácticamente toda la web sin ningún tipo de delicadeza. Contenido privado, sensible y personal queda expuesto a búsquedas y análisis no autorizados.

### La Solución: Cortapis
Cortapis utiliza un sistema de **marcado de tokens con '@'** (similar al autocompletado de correo electrónico) combinado con **encriptación y ofuscación** para crear un contenido que:

1. **Aparece corrupto** a los indexadores de búsqueda
2. **Se encripta** para protección adicional
3. **Se puede recuperar** mediante una "ventana de llamada" (call window)

## 🎯 Características

### ✅ WRITE MODE (Modo Escritura)
Protege contenido al guardarlo:
- Marca tokens sensibles con símbolo '@'
- Ofusca el texto con caracteres adicionales
- Encripta el resultado
- Genera session ID único

### ✅ READ MODE (Modo Lectura)
Abre la "ventana de llamada" para acceder al contenido:
- Desencripta contenido
- Elimina ofuscación
- Restaura texto original
- Solo exposición temporal

### ✅ OBFUSCACIÓN CON '@'
- Simula autocompletado de email
- Distribuye '@' por todo el texto
- Hace que aparezca corrupto
- No afecta al texto real (cuando se encripta)

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## 💻 Uso

### Interfaz Web

```bash
# Ejecutar servidor Flask
python cortapis_security/web_interface.py
```

Luego abre: `http://localhost:5000`

### Python Script

```python
from cortapis_security.cortapis import CortapisSecurityEngine

engine = CortapisSecurityEngine()
text = "Contact admin@company.com"
encrypted_data = engine.write_mode(text)
decrypted = engine.read_mode(encrypted_data)
print(decrypted)
```

## 🔐 Seguridad

- **Encriptación Fernet (AES-128)**
- **Ofuscación contra indexadores**
- **Detección automática de patrones sensibles**
- **Session management**

## 📱 API Endpoints

- `POST /api/encrypt` - Encriptar contenido
- `POST /api/decrypt` - Desencriptar contenido
- `POST /api/mark-sensitive` - Marcar tokens sensibles
- `GET /api/sessions` - Listar sesiones activas

---

**🔐 Privacidad y Seguridad Primero**
