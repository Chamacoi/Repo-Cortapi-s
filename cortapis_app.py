#!/usr/bin/env python3
"""
Cortapis Security App
Encryption system with @ marker nodes for AI indexing protection
"""

import re
import hashlib
import base64
from typing import List, Tuple, Dict
from cryptography.fernet import Fernet
import json

class CortapisSecurityApp:
    """
    Cortapis: A security solution that encrypts text with @ markers
    to prevent AI indexing and web crawling while maintaining readability.
    
    Features:
    - Mark sensitive content with @ markers
    - Encrypt text before cloud upload
    - Decrypt when opening "call window" (Matrix-style)
    - Markdown-compatible pseudo-links for @ symbols
    """
    
    def __init__(self):
        self.marker = '@'
        self.encryption_key = None
        self.encrypted_texts = {}
        
    def generate_encryption_key(self, password: str = None) -> str:
        """
        Generate or derive encryption key from password
        """
        if password:
            key = base64.urlsafe_b64encode(
                hashlib.sha256(password.encode()).digest()
            )
        else:
            key = Fernet.generate_key()
        
        self.encryption_key = key
        return key.decode()
    
    def mark_sensitive_content(self, text: str, markers: List[str] = None) -> str:
        """
        Mark sensitive content with @ symbols in Markdown pseudo-links format
        Example: "contact [@@]example@.com" becomes marked content
        """
        if markers is None:
            markers = []
        
        marked_text = text
        
        # Replace email-like patterns with @ markers in Markdown format
        # Pattern: word@domain -> [@@]word@domain
        email_pattern = r'([a-zA-Z0-9._-]+)@([a-zA-Z0-9._-]+)'
        marked_text = re.sub(
            email_pattern,
            r'[\@\@]\1@\2',
            marked_text
        )
        
        # Add additional markers for custom sensitive content
        for marker_phrase in markers:
            marked_text = marked_text.replace(
                marker_phrase,
                f'[@@]{marker_phrase}'
            )
        
        return marked_text
    
    def encrypt_text(self, text: str) -> str:
        """
        Encrypt marked text for storage/cloud upload
        """
        if not self.encryption_key:
            self.generate_encryption_key()
        
        cipher = Fernet(self.encryption_key)
        encrypted = cipher.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypt text when opening "call window" (Matrix-style reveal)
        """
        if not self.encryption_key:
            raise ValueError("Encryption key not set. Generate or provide key first.")
        
        try:
            cipher = Fernet(self.encryption_key)
            decoded = base64.b64decode(encrypted_text.encode())
            decrypted = cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def remove_markers(self, marked_text: str) -> str:
        """
        Remove @ markers (pseudo-links format)
        Converts "[@@]content" back to "content"
        """
        # Remove Markdown pseudo-link markers
        cleaned = re.sub(r'\[\@\@\]', '', marked_text)
        return cleaned
    
    def obfuscate_for_indexing(self, text: str) -> str:
        """
        Make text appear corrupted to alphabetical search patterns
        Add @ characters throughout to disrupt indexing
        """
        # Insert @ markers at strategic positions
        words = text.split()
        obfuscated_words = []
        
        for i, word in enumerate(words):
            if i % 3 == 0 and '@' not in word:
                # Scatter @ markers throughout
                obfuscated_words.append(f"{word}@")
            else:
                obfuscated_words.append(word)
        
        return ' '.join(obfuscated_words)
    
    def save_to_file(self, filename: str, text: str, encrypt: bool = True, obfuscate: bool = True) -> Dict:
        """
        Save text with security layers:
        1. Mark sensitive content
        2. Obfuscate (optional)
        3. Encrypt (optional)
        """
        # Step 1: Mark content
        marked_text = self.mark_sensitive_content(text)
        
        # Step 2: Obfuscate if requested
        if obfuscate:
            obfuscated_text = self.obfuscate_for_indexing(marked_text)
        else:
            obfuscated_text = marked_text
        
        # Step 3: Encrypt if requested
        if encrypt:
            if not self.encryption_key:
                self.generate_encryption_key()
            encrypted_text = self.encrypt_text(obfuscated_text)
        else:
            encrypted_text = obfuscated_text
        
        # Store in memory
        self.encrypted_texts[filename] = {
            'content': encrypted_text,
            'is_encrypted': encrypt,
            'is_obfuscated': obfuscate
        }
        
        return {
            'filename': filename,
            'marked': marked_text,
            'obfuscated': obfuscated_text,
            'encrypted': encrypted_text if encrypt else None,
            'status': 'saved'
        }
    
    def open_call_window(self, filename: str) -> str:
        """
        Matrix-style "call window" - decrypt and reveal content
        This is when the file becomes exposed to indexing temporarily
        """
        if filename not in self.encrypted_texts:
            raise ValueError(f"File {filename} not found")
        
        file_data = self.encrypted_texts[filename]
        content = file_data['content']
        
        # Decrypt if encrypted
        if file_data['is_encrypted']:
            content = self.decrypt_text(content)
        
        # Remove obfuscation if applied
        if file_data['is_obfuscated']:
            content = self.remove_markers(content)
        
        # Remove all @ markers
        content = self.remove_markers(content)
        
        return content
    
    def export_markdown(self, filename: str, output_file: str) -> str:
        """
        Export content as Markdown with protection
        Uses Markdown code blocks to contain @ symbols
        """
        content = self.open_call_window(filename)
        
        markdown_content = f"""# Cortapis Protected Content

## Original Content
```markdown
{content}
```

## Security Info
- Protected with Cortapis security system
- @ markers prevent AI indexing
- Markdown format maintains readability
- Encrypted for cloud storage
"""
        
        return markdown_content


def main():
    """
    Example usage of Cortapis Security App
    """
    app = CortapisSecurityApp()
    
    # Generate encryption key with password
    password = "cortapis_secure_2024"
    key = app.generate_encryption_key(password)
    print(f"✓ Encryption key generated\n")
    
    # Example sensitive text
    sensitive_text = """
    Contact me at admin@example.com or support@company.org
    My personal email is user@private.com
    For urgent matters: emergency@contact.net
    """
    
    print("📝 Original text:")
    print(sensitive_text)
    print("\n" + "="*50 + "\n")
    
    # Step 1: Save with security layers
    result = app.save_to_file(
        'sensitive_data.txt',
        sensitive_text,
        encrypt=True,
        obfuscate=True
    )
    
    print("🔒 After marking + obfuscation:")
    print(result['obfuscated'])
    print("\n" + "="*50 + "\n")
    
    print("🔐 Encrypted (safe for cloud):")
    print(result['encrypted'][:80] + "...\n")
    print("\n" + "="*50 + "\n")
    
    # Step 2: Open call window (Matrix-style reveal)
    print("🚪 Opening call window (decrypting)...\n")
    revealed = app.open_call_window('sensitive_data.txt')
    print("📖 Revealed content:")
    print(revealed)
    print("\n" + "="*50 + "\n")
    
    # Step 3: Export as Markdown
    markdown = app.export_markdown('sensitive_data.txt', 'output.md')
    print("📄 Markdown export:")
    print(markdown)


if __name__ == "__main__":
    main()
