#!/usr/bin/env python3
"""
Cortapis Security System - Example Usage Script
Demuestra todas las características del sistema Cortapis
"""

from cortapis_security.cortapis import CortapisSecurityEngine, EmailStyleAutocomplete
import json


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def example_basic_usage():
    """Example 1: Basic Write and Read Mode"""
    print_section("EJEMPLO 1: Uso Básico - Write y Read Mode")
    
    # Inicializar motor
    engine = CortapisSecurityEngine()
    
    # Contenido sensible
    sensitive_text = """
    Contact Information:
    - Admin Email: admin@cortapi-security.com
    - Support Email: support@cortapi-security.com
    - API Key: sk_test_4eC39HqLyjWDarhtT657j61F
    """
    
    print("📄 CONTENIDO ORIGINAL:")
    print(sensitive_text)
    
    # WRITE MODE: Encriptar
    print("\n🔒 WRITE MODE: Encriptando contenido...")
    encrypted_data = engine.write_mode(sensitive_text)
    
    print(f"\n✓ Contenido encriptado")
    print(f"  - Tokens encontrados: {len(encrypted_data['token_map'])}")
    print(f"  - Primeros 100 caracteres encriptados:\n    {encrypted_data['encrypted_content'][:100]}...")
    
    # READ MODE: Desencriptar
    print("\n🔓 READ MODE: Abriendo call window...")
    decrypted = engine.read_mode(encrypted_data)
    print(f"\n✓ Contenido desencriptado:")
    print(decrypted)


def example_obfuscation():
    """Example 2: Text Obfuscation"""
    print_section("EJEMPLO 2: Ofuscación de Texto Contra Indexadores")
    
    engine = CortapisSecurityEngine()
    
    original = "This is a secret message that should not be indexed"
    
    print("📝 TEXTO ORIGINAL:")
    print(original)
    
    print("\n🌫️ OFUSCADO (Aparece corrupto a indexadores):")
    obfuscated = engine.obfuscate_text(original)
    print(obfuscated)
    
    print("\n💡 Nota: El texto ofuscado confunde a los buscadores de IA")
    print("   pero puede ser restaurado al desencriptarse")


if __name__ == "__main__":
    print("\n")
    print("█" * 60)
    print("█  CORTAPIS SECURITY SYSTEM - EJEMPLOS DE USO")
    print("█" * 60)
    
    try:
        example_basic_usage()
        example_obfuscation()
        
        print_section("✅ EJEMPLOS COMPLETADOS")
        print("\n🔐 Para más información, consulta el README.md")
        print("🌐 Interfaz Web: python cortapis_security/web_interface.py\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
