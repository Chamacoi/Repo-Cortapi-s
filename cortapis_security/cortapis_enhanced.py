"""
Cortapis Security System - Enhanced Version v2.0
Enhanced security with industry best practices
"""

import re
import base64
import hashlib
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
from typing import List, Tuple, Dict, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CortapisSecurityEngineV2:
    """Enhanced engine for text obfuscation and encryption against AI indexing"""
    
    def __init__(self, encryption_key: str = None, max_text_length: int = 1_000_000):
        """
        Initialize the Cortapis engine
        
        Args:
            encryption_key: Optional Fernet key for encryption. If None, generates new one.
            max_text_length: Maximum allowed text length to prevent DoS
        """
        if encryption_key:
            try:
                self.cipher = Fernet(encryption_key)
                self.key = encryption_key
            except Exception as e:
                logger.error(f"Invalid encryption key: {str(e)}")
                raise ValueError(f"Invalid encryption key: {str(e)}")
        else:
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
        
        self.max_text_length = max_text_length
        logger.info("Cortapis Security Engine v2.0 initialized")
    
    def get_encryption_key(self) -> str:
        """Return the encryption key for storage"""
        return self.key.decode() if isinstance(self.key, bytes) else self.key
    
    def _validate_input(self, text: str, max_length: int = None) -> bool:
        """Validate input to prevent DoS attacks and injection"""
        if max_length is None:
            max_length = self.max_text_length
        
        if not isinstance(text, str):
            logger.warning(f"Invalid input type: {type(text)}")
            raise TypeError("Text must be a string")
        
        if len(text) == 0:
            logger.warning("Empty text provided")
            raise ValueError("Text cannot be empty")
        
        if len(text) > max_length:
            logger.warning(f"Text exceeds maximum length: {len(text)} > {max_length}")
            raise ValueError(f"Text exceeds maximum length of {max_length} characters")
        
        return True
    
    def mark_sensitive_tokens(self, text: str, patterns: List[str] = None) -> Tuple[str, Dict]:
        """
        Mark sensitive content with @ symbols (like email autocomplete)
        
        Args:
            text: Input text to process
            patterns: List of regex patterns to match sensitive content
            
        Returns:
            Tuple of (marked_text, token_map)
        """
        self._validate_input(text)
        
        if patterns is None:
            patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{16}\b',  # Credit card
                r'\b(?:password|pwd|api[_-]?key|secret)\s*[=:]\s*[^\s]+',  # Credentials
            ]
        
        token_map = {}
        marked_text = text
        token_counter = 0
        
        for pattern in patterns:
            try:
                matches = list(re.finditer(pattern, marked_text, re.IGNORECASE))
                for match in matches:
                    original = match.group(0)
                    token_id = f"@token_{token_counter}@"
                    token_map[token_id] = original
                    marked_text = marked_text.replace(original, token_id, 1)
                    token_counter += 1
            except re.error as e:
                logger.error(f"Invalid regex pattern: {str(e)}")
                raise ValueError(f"Invalid regex pattern: {str(e)}")
        
        logger.info(f"Marked {token_counter} sensitive tokens")
        return marked_text, token_map
    
    def obfuscate_text(self, text: str) -> str:
        """
        Add @ symbols throughout text to make it appear corrupted to indexers
        """
        self._validate_input(text)
        
        words = text.split()
        obfuscated = []
        
        for i, word in enumerate(words):
            if i % 3 == 0 and len(word) > 3:
                mid = len(word) // 2
                word = word[:mid] + '@' + word[mid:]
            obfuscated.append(word)
        
        return ' '.join(obfuscated)
    
    def write_mode(self, text: str, patterns: List[str] = None) -> Dict:
        """WRITE MODE: Process text for secure storage"""
        self._validate_input(text)
        
        try:
            marked_text, token_map = self.mark_sensitive_tokens(text, patterns)
            obfuscated = self.obfuscate_text(marked_text)
            encrypted = self.cipher.encrypt(obfuscated.encode())
            
            result = {
                'encrypted_content': base64.b64encode(encrypted).decode(),
                'token_map': token_map,
                'status': 'encrypted',
                'mode': 'write',
                'timestamp': datetime.utcnow().isoformat(),
                'checksum': hashlib.sha256(text.encode()).hexdigest()  # Para integridad
            }
            
            logger.info(f"Text encrypted successfully. Tokens: {len(token_map)}")
            return result
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise RuntimeError(f"Encryption failed: {str(e)}")
    
    def read_mode(self, encrypted_data: Dict) -> str:
        """READ MODE: Opens the call window to expose decrypted content"""
        
        if not isinstance(encrypted_data, dict):
            logger.error("Encrypted data is not a dictionary")
            raise TypeError("Encrypted data must be a dictionary")
        
        if 'encrypted_content' not in encrypted_data:
            logger.error("Missing encrypted_content in data")
            raise ValueError("Missing encrypted_content")
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data['encrypted_content'])
            decrypted = self.cipher.decrypt(encrypted_bytes).decode()
            
            cleaned = re.sub(r'@(?!token_\d+@)', '', decrypted)
            
            token_map = encrypted_data.get('token_map', {})
            restored = cleaned
            for token_id, original in token_map.items():
                restored = restored.replace(token_id, original)
            
            logger.info("Text decrypted successfully")
            return restored
            
        except InvalidToken:
            logger.error("Decryption failed: Invalid token")
            raise RuntimeError("Decryption failed: Invalid token or corrupted data")
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise RuntimeError(f"Decryption error: {str(e)}")
    
    def verify_integrity(self, text: str, checksum: str) -> bool:
        """Verify text integrity using checksum"""
        computed_checksum = hashlib.sha256(text.encode()).hexdigest()
        return computed_checksum == checksum
    
    def export_to_markdown(self, original_text: str, encrypted_data: Dict, 
                          include_key: bool = False) -> str:
        """
        Export encrypted content as Markdown with metadata
        
        Args:
            original_text: Original text for reference
            encrypted_data: Encrypted data from write_mode
            include_key: Whether to include encryption key (NOT RECOMMENDED)
        
        Returns:
            Markdown formatted content
        """
        key_section = ""
        if include_key:
            key_section = f"\n## ⚠️ Encryption Key\n```\n{self.get_encryption_key()}\n```\n"
        
        markdown = f"""# Cortapis Protected Document

## Status
🔒 **Encrypted & Protected Against Indexing**

## Metadata
- Created: {encrypted_data.get('timestamp', 'N/A')}
- Checksum: {encrypted_data.get('checksum', 'N/A')}
- Tokens: {len(encrypted_data.get('token_map', {}))}
{key_section}
## Protected Content
```
{encrypted_data['encrypted_content']}
```

---

*This document is protected by Cortapis Security System v2.0*
"""
        return markdown
