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

# Abrir ventana de llamada para leer el contenido de forma segura
desencriptado = app.open_call_window('documento.txt')
print(f"Desencriptado: {desencriptado}")

```
### 🌐 Versión Web (JavaScript)
Abre el archivo cortapis_web.html directamente en cualquier navegador moderno.
 * Interfaz visual inspirada en estética cyberpunk (Matrix-style).
 * Encriptación local directamente en el lado del cliente (Client-Side) usando **Web Crypto API**. No se envían datos a ningún servidor.
 * Exportación directa a Markdown y descarga de contenedores encriptados.
### 🟢 Versión Node.js
Integración nativa para entornos de servidor o scripts en JS.
```javascript
const CortapisApp = require('./cortapis_app.js');

async function run() {
    const app = new CortapisApp();
    await app.generateEncryptionKey('password123');

    const result = await app.saveToFile('datos.txt', 'mi texto sensible');
    console.log('Encriptado:', result.encrypted);
}
run();

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
│    Seguridad para almacenamiento    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 4. Almacenamiento en la Nube        │
│    Protegido de indexación de IA    │
└────────┬────────────────────────────┘
         │
         ▼ (Acceso bajo demanda)
┌─────────────────────────────────────┐
│ 5. Ventana de Llamada               │
│    Desencriptar y revelar           │
│    (exposición temporal protegida)  │
└─────────────────────────────────────┘

```
## 📋 Casos de Uso
 1. **Protección en Google Colab / Jupyter Notebooks:** Permite subir y operar con datasets u hojas de configuración que contienen credenciales o datos sensibles sin miedo a que el entorno de ejecución indexe o filtre los datos en claro.
 2. **Kaggle & Deepnote:** Comparte y colabora en notebooks públicos utilizando datasets cifrados con Cortapis; los colaboradores autorizados solo necesitan la clave para desencriptar en memoria durante la ejecución.
 3. **Almacenamiento Seguro en GitHub:** Sube notas personales o documentación a tus repositorios evitando que los bots de rastreo de código recopilen tus patrones de texto.
## 🛠️ API Endpoints
Si utilizas Cortapis en modo servicio, la aplicación expone los siguientes endpoints:
| Método | Endpoint | Descripción |
|---|---|---|
| POST | /api/encrypt | Encripta el contenido enviado en el cuerpo. |
| POST | /api/decrypt | Desencripta y abre la ventana de llamada (*call window*). |
| POST | /api/mark-sensitive | Aplica el enmascaramiento con marcadores [@@]. |
| POST | /api/obfuscate | Ofusca cadenas de texto plano. |
| GET | /api/sessions | Lista las sesiones activas en memoria. |
| DELETE | /api/clear-session | Limpia la sesión actual y destruye las claves temporales. |
## 🛡️ Limitaciones conocidas
 * Si la clave/contraseña de cifrado se ve comprometida, la seguridad del archivo se pierde por completo.
 * La *Ventana de Llamada* expone temporalmente la información en texto plano en la pantalla/memoria del sistema, por lo que no protege contra ataques de acceso físico o malware espía de pantalla (*screenloggers*).
## 📄 Licencia
Cortapis es software de código abierto distribuido bajo la licencia **Apache 2.0**. Consulta el archivo LICENSE para más detalles.
### ⚠️ Disclaimer (Uso Responsable)
Este software ha sido diseñado con fines legítimos de privacidad personal y protección de datos frente al scraping masivo. El autor no se hace responsable del mal uso de esta herramienta para actividades ilícitas. La privacidad legítima es un derecho; ocultar actividades delictivas no es el propósito de esta aplicación.
**Desarrollado por:** Chamacoi
**Lema:** *"Seguridad y privacidad es lo que importa"*