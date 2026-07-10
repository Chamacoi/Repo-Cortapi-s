# 🔐 Cortapis Security App
<!---
Chamacoi/Chamacoi is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
<div align="center">
  <a href="https://primal.net/p/"beigemonkey27@primal.net target="_blank">
    <img src="https://img.shields.io/badge/Zap%20Me%20on%20Primal-⚡-orange?style=for-the-badge&logo=bitcoin&logoColor=white&color=FF9900" alt="Zap Me on Primal">
  </a>
</div>
**AI-Proof Text Encryption & Protection System**

Cortapis es un sistema de seguridad que protege contenido sensible de la indexación de IA mediante el uso de marcadores @ en formato Markdown, ofuscación de texto y encriptación.    
Siempre puedes empezar por el tutorial "Tutorial Cortapi-s.txt" en esta misma Repo.

## 🎯 Objetivo

Proteger documentos sensibles durante su almacenamiento en la nube y servicios online, evitando que sean indexados por sistemas de IA y rastreadores web mientras se mantiene la capacidad de leerlos cuando sea necesario.

## 🔐 Características Principales

### 1. **Marcado de Contenido Sensible**
```
Original: contact@example.com
Marcado:  [@@]contact@example.com
```
- Los símbolos @ se envuelven en pseudo-enlaces Markdown
- Fácil de identificar en archivos de texto
- Compatible con estándares de correo electrónico

### 2. **Ofuscación para Búsquedas Alfabéticas**
- Dispersión de @ marcadores a través del texto
- El contenido aparece corrupto a los patrones de búsqueda
- Disrumpe los algoritmos de indexación alfabética

### 3. **Encriptación AES-256-GCM**
- Encriptación fuerte basada en contraseña
- Segura para almacenamiento en la nube
- Descifrado solo con la contraseña correcta

### 4. **Ventana de Llamada (Matrix-Style)**
- Desencripta contenido cuando sea necesario
- Muestra advertencia cuando el contenido está expuesto
- Permite trabajar con el documento de forma segura

## 🚀 Uso

### Versión Python

```bash
python cortapis_app.py
```

**Ejemplo:**
```python
from cortapis_app import CortapisSecurityApp

app = CortapisSecurityApp()
app.generate_encryption_key("mi_contraseña_segura")

texto = "Contacta a admin@example.com"
resultado = app.save_to_file(
    'documento.txt',
    texto,
    encrypt=True,
    obfuscate=True
)

print(f"Encriptado: {resultado['encrypted']}")

# Abrir ventana de llamada
desencriptado = app.open_call_window('documento.txt')
print(f"Desencriptado: {desencriptado}")
```

### Versión Web/JavaScript

Abrir `cortapis_web.html` en un navegador web moderno.

**Características:**
- Interfaz visual Matrix-style
- Encriptación cliente-side (AES-256-GCM)
- Exportación a Markdown
- Descarga de archivos encriptados

### Versión Node.js

```javascript
const CortapisApp = require('./cortapis_app.js');

const app = new CortapisApp();
await app.generateEncryptionKey('password123');

const result = await app.saveToFile('datos.txt', 'mi texto sensible');
console.log('Encriptado:', result.encrypted);
```

## 🔄 Flujo de Seguridad

```
┌─────────────────┐
│  Texto Original │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Marcar Contenido Sensible        │
│    contact@example.com              │
│    ↓                                │
│    [@@]contact@example.com          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Ofuscación                       │
│    Dispersar @ para confundir       │
│    patrones de búsqueda             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Encriptación AES-256-GCM         │
│    Safe para almacenamiento cloud   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 4. Almacenamiento en la Nube        │
│    Protegido de indexación de IA    │
└────────┬────────────────────────────┘
         │
         ▼ (cuando se necesita acceso)
┌─────────────────────────────────────┐
│ 5. Ventana de Llamada               │
│    Desencriptar y revelar           │
│    (temporalmente expuesto)         │
└─────────────────────────────────────┘
```

## 📋 Casos de Uso

### 1. **Protección en Google Colab**
```python
# Subir datos sensibles sin temor a indexación
from cortapis_app import CortapisSecurityApp
app = CortapisSecurityApp()
app.generate_encryption_key("contraseña")
app.save_to_file('datos_investigacion.txt', contenido_sensible)
```

### 2. **Kaggle Notebooks**
- Subir datasets encriptados
- Colaborar sin comprometer privacidad
- Desencriptar solo cuando sea necesario

### 3. **Deepnote & Notebooks Online**
- Mismo proceso que Colab
- Compatible con todos los servicios de notebooks

### 4. **Almacenamiento en GitHub**
- Archivos encriptados seguros
- Metadata protegida de raspadores
- Reversible con contraseña

## 🔐 Seguridad & Privacidad

### ¿Por qué funciona?

1. **@ Markers** rompem patrones de reconocimiento
   - Los crawlers buscan patrones regulares
   - Los marcadores @ disrumpen regex estándar
   - Los modelos de IA no pueden indexar lo que no pueden parsear

2. **Ofuscación** confunde búsquedas alfabéticas
   - Texto aparece corrupto
   - Métodos heurísticos fallan
   - Requisitos de procesamiento aumentan exponencialmente

3. **Encriptación** protege data en tránsito y almacenamiento
   - AES-256-GCM es estándar militar
   - Sin contraseña = inaccesible
   - No hay backdoors

### Limitaciones

- Si la contraseña se compromete, el contenido se compromete
- La ventana de llamada expone temporalmente el contenido
- No protege contra ataques con acceso físico directo
- Requiere cliente compatible para descifrar

## 🛠️ Requisitos

### Python
```bash
pip install cryptography
```

### Navegador Web
- Navegador moderno con soporte para:
  - Web Crypto API (Chrome 37+, Firefox 34+, Safari 11+, Edge 79+)
  - Async/Await

### Node.js
```bash
npm install crypto-js
```

## 📄 Licencia

Cortapis - Sistema de Seguridad para Protección contra Indexación de IA
Apache 2.0  http://www.apache.org/licenses/

## API Endpoints
POST- Encriptar contenido
```/api/encrypt``` 
POST- Desencriptar (abre call window) 
```/api/decrypt``` 
POST- Marcar tokens 
```/api/mark-sensitive``` 
POST- Ofuscar texto 
```/api/obfuscate``` 
GET- Listar sesiones 
```/api/sessions``` 
DELETE- Limpiar sesión
```/api/clear-session``` 

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## ⚠️ Disclaimer

**USO RESPONSABLE:**
- Este software está diseñado para privacidad legítima
- NO debe usarse para ocultar actividades ilegales
- Los usuarios son responsables de cumplir con leyes locales
- La privacidad legítima ≠ ocultamiento de criminalidad

---

**Desarrollado por:** Chamacoi  
**Propósito:** Proteger privacidad personal y datos sensibles  
**Lema:** *"Seguridad y privacidad es lo que importa"*
