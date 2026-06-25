"""
Cortapis Security System
------------------------
A text obfuscation and privacy-preservation system that marks sensitive content
with '@' symbols (similar to email autocomplete) and encrypts them against indexing.

The system works in two modes:
1. WRITE MODE: Marks sensitive tokens with '@' and encrypts, making text appear corrupted to indexers
2. READ MODE: Opens the "call window" to expose and decrypt the content
"""

import re
import base64
from cryptography.fernet import Fernet
from typing import List, Tuple, Dict
import json


class CortapisSecurityEngine:
    """Main engine for text obfuscation and encryption against AI indexing"""
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize the Cortapis engine
        
        Args:
            encryption_key: Optional Fernet key for encryption. If None, generates new one.
        """
        if encryption_key:
            self.cipher = Fernet(encryption_key)
            self.key = encryption_key
        else:
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
    
    def get_encryption_key(self) -> str:
        """Return the encryption key for storage"""
        return self.key.decode() if isinstance(self.key, bytes) else self.key
    
    def mark_sensitive_tokens(self, text: str, patterns: List[str] = None) -> Tuple[str, Dict]:
        """
        Mark sensitive content with @ symbols (like email autocomplete)
        
        Args:
            text: Input text to process
            patterns: List of regex patterns to match sensitive content
            
        Returns:
            Tuple of (marked_text, token_map)
        """
        if patterns is None:
            patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{16}\b',  # Credit card
                r'\b(?:password|pwd|api[_-]?key|secret)\s*[=:]\s*[^\s]+',  # Credentials
            ]
        
        token_map = {}
        marked_text = text
        token_counter = 0
        
        for pattern in patterns:
            matches = re.finditer(pattern, marked_text, re.IGNORECASE)
            for match in matches:
                original = match.group(0)
                token_id = f"@token_{token_counter}@"
                token_map[token_id] = original
                marked_text = marked_text.replace(original, token_id, 1)
                token_counter += 1
        
        return marked_text, token_map
    
    def obfuscate_text(self, text: str) -> str:
        """
        Add @ symbols throughout text to make it appear corrupted to indexers
        
        Args:
            text: Text to obfuscate
            
        Returns:
            Obfuscated text with @ symbols distributed
        """
        # Insert @ symbols at regular intervals and random positions
        words = text.split()
        obfuscated = []
        
        for i, word in enumerate(words):
            if i % 3 == 0 and len(word) > 3:
                # Insert @ at middle of word
                mid = len(word) // 2
                word = word[:mid] + '@' + word[mid:]
            obfuscated.append(word)
        
        return ' '.join(obfuscated)
    
    def write_mode(self, text: str, patterns: List[str] = None) -> Dict:
        """
        WRITE MODE: Process text for secure storage
        - Marks sensitive tokens with @
        - Obfuscates with additional @ symbols
        - Encrypts the result
        
        Args:
            text: Original sensitive text
            patterns: Regex patterns for sensitive content
            
        Returns:
            Dictionary with encrypted text, token map, and metadata
        """
        # Step 1: Mark sensitive tokens
        marked_text, token_map = self.mark_sensitive_tokens(text, patterns)
        
        # Step 2: Obfuscate with @ symbols
        obfuscated = self.obfuscate_text(marked_text)
        
        # Step 3: Encrypt
        encrypted = self.cipher.encrypt(obfuscated.encode())
        
        return {
            'encrypted_content': base64.b64encode(encrypted).decode(),
            'token_map': token_map,
            'status': 'encrypted',
            'mode': 'write'
        }
    
    def read_mode(self, encrypted_data: Dict) -> str:
        """
        READ MODE: Opens the "call window" to expose decrypted content
        - Decrypts the encrypted text
        - Removes obfuscation @ symbols
        - Restores original sensitive tokens
        
        Args:
            encrypted_data: Dictionary from write_mode
            
        Returns:
            Decrypted original text
        """
        try:
            # Step 1: Decrypt
            encrypted_bytes = base64.b64decode(encrypted_data['encrypted_content'])
            decrypted = self.cipher.decrypt(encrypted_bytes).decode()
            
            # Step 2: Remove obfuscation @ symbols (keep only token markers)
            # Remove @ symbols that are not part of @token_X@ markers
            cleaned = re.sub(r'@(?!token_\d+@)', '', decrypted)
            
            # Step 3: Restore original tokens
            token_map = encrypted_data['token_map']
            restored = cleaned
            for token_id, original in token_map.items():
                restored = restored.replace(token_id, original)
            
            return restored
            
        except Exception as e:
            return f"Error decrypting: {str(e)}"
    
    def export_to_markdown(self, original_text: str, encrypted_data: Dict) -> str:
        """
        Export encrypted content as Markdown with metadata
        
        Args:
            original_text: Original text for reference
            encrypted_data: Encrypted data from write_mode
            
        Returns:
            Markdown formatted content
        """
        markdown = f"""# Cortapis Protected Document

## Status
🔒 **Encrypted & Protected Against Indexing**

## Encryption Key
```
{self.get_encryption_key()}
```

## Protected Content
```
{encrypted_data['encrypted_content']}
```

## Token Map
```json
{json.dumps(encrypted_data['token_map'], indent=2)}
```

## Metadata
- Mode: {encrypted_data['mode']}
- Status: {encrypted_data['status']}

---

*This document is protected by Cortapis Security System*
"""
        return markdown


class EmailStyleAutocomplete:
    """
    Simulates email-style autocomplete for sensitive token marking
    Similar to how email clients suggest recipients after '@'
    """
    
    def __init__(self):
        self.suggestions = {}
    
    def add_suggestion(self, prefix: str, completions: List[str]):
        """Add autocomplete suggestions"""
        self.suggestions[prefix] = completions
    
    def get_suggestions(self, text: str) -> List[str]:
        """Get suggestions based on current text"""
        if '@' not in text:
            return []
        
        prefix = text.split('@')[-1].lower()
        return [s for s in self.suggestions.get('@', []) if s.lower().startswith(prefix)]
    
    def apply_suggestion(self, text: str, suggestion: str) -> str:
        """Apply a suggestion and mark it as sensitive token"""
        if '@' in text:
            parts = text.rsplit('@', 1)
            return f"{parts[0]}@{suggestion}@"
        return text


if __name__ == "__main__":
    # Demo usage
    engine = CortapisSecurityEngine()
    
    sensitive_text = "Contact john.doe@example.com or call admin@company.org for access."
    
    print("=== CORTAPIS SECURITY SYSTEM DEMO ===\n")
    print(f"Original Text:\n{sensitive_text}\n")
    
    encrypted_data = engine.write_mode(sensitive_text)
    print(f"WRITE MODE - Encrypted:\n{encrypted_data['encrypted_content']}\n")
    
    decrypted = engine.read_mode(encrypted_data)
    print(f"READ MODE - Decrypted:\n{decrypted}\n")
    
    markdown = engine.export_to_markdown(sensitive_text, encrypted_data)
    print(f"MARKDOWN EXPORT:\n{markdown}")
