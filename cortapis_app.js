/**
 * Cortapis Security App - JavaScript/Web Version
 * Browser-based encryption with @ marker system for AI indexing protection
 */

class CortapisApp {
  constructor() {
    this.marker = '@';
    this.encryptedTexts = {};
    this.encryptionKey = null;
  }

  /**
   * Generate encryption key from password
   */
  async generateEncryptionKey(password) {
    if (!password) {
      throw new Error('Password required for key generation');
    }

    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    this.encryptionKey = hashBuffer;
    return hashBuffer;
  }

  /**
   * Mark sensitive content with @ symbols in Markdown format
   * Example: admin@example.com -> [@@]admin@example.com
   */
  markSensitiveContent(text, markers = []) {
    let markedText = text;

    // Email pattern: word@domain -> [@@]word@domain
    const emailPattern = /([a-zA-Z0-9._-]+)@([a-zA-Z0-9._-]+)/g;
    markedText = markedText.replace(emailPattern, '[@@]$1@$2');

    // Add markers for custom sensitive content
    markers.forEach(phrase => {
      markedText = markedText.replace(
        new RegExp(phrase, 'g'),
        `[@@]${phrase}`
      );
    });

    return markedText;
  }

  /**
   * Obfuscate text to appear corrupted to alphabetical searches
   * Scatter @ markers throughout to disrupt AI indexing
   */
  obfuscateForIndexing(text) {
    const words = text.split(/\s+/);
    const obfuscatedWords = words.map((word, i) => {
      if (i % 3 === 0 && !word.includes('@')) {
        return `${word}@`;
      }
      return word;
    });

    return obfuscatedWords.join(' ');
  }

  /**
   * Encrypt text using SubtleCrypto API
   */
  async encryptText(text) {
    if (!this.encryptionKey) {
      throw new Error('Encryption key not set');
    }

    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      this.encryptionKey,
      data
    );

    // Combine IV + ciphertext and encode as base64
    const combined = new Uint8Array(iv.length + ciphertext.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(ciphertext), iv.length);

    return btoa(String.fromCharCode(...combined));
  }

  /**
   * Decrypt text using SubtleCrypto API
   */
  async decryptText(encryptedText) {
    if (!this.encryptionKey) {
      throw new Error('Encryption key not set');
    }

    try {
      const combined = Uint8Array.from(atob(encryptedText), c => c.charCodeAt(0));
      const iv = combined.slice(0, 12);
      const ciphertext = combined.slice(12);

      const plaintext = await crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        this.encryptionKey,
        ciphertext
      );

      return new TextDecoder().decode(plaintext);
    } catch (error) {
      throw new Error(`Decryption failed: ${error.message}`);
    }
  }

  /**
   * Remove @ markers (Markdown pseudo-links)
   * Converts "[@@]content" back to "content"
   */
  removeMarkers(markedText) {
    return markedText.replace(/\[@@\]/g, '');
  }

  /**
   * Save file with security layers
   */
  async saveToFile(filename, text, encrypt = true, obfuscate = true) {
    // Step 1: Mark content
    const markedText = this.markSensitiveContent(text);

    // Step 2: Obfuscate if requested
    const obfuscatedText = obfuscate
      ? this.obfuscateForIndexing(markedText)
      : markedText;

    // Step 3: Encrypt if requested
    let encryptedText = obfuscatedText;
    if (encrypt) {
      if (!this.encryptionKey) {
        throw new Error('Encryption key not set');
      }
      encryptedText = await this.encryptText(obfuscatedText);
    }

    // Store in memory
    this.encryptedTexts[filename] = {
      content: encryptedText,
      isEncrypted: encrypt,
      isObfuscated: obfuscate
    };

    return {
      filename,
      marked: markedText,
      obfuscated: obfuscatedText,
      encrypted: encrypt ? encryptedText : null,
      status: 'saved'
    };
  }

  /**
   * Open "call window" (Matrix-style decrypt)
   * Temporarily expose content for viewing/editing
   */
  async openCallWindow(filename) {
    if (!this.encryptedTexts[filename]) {
      throw new Error(`File ${filename} not found`);
    }

    const fileData = this.encryptedTexts[filename];
    let content = fileData.content;

    // Decrypt if encrypted
    if (fileData.isEncrypted) {
      content = await this.decryptText(content);
    }

    // Remove markers
    content = this.removeMarkers(content);

    return content;
  }

  /**
   * Export as Markdown format
   */
  async exportMarkdown(filename) {
    const content = await this.openCallWindow(filename);

    return `# Cortapis Protected Content

## Original Content
\`\`\`markdown
${content}
\`\`\`

## Security Info
- Protected with Cortapis security system
- @ markers prevent AI indexing
- Markdown format maintains readability
- Encrypted for cloud storage

---
*Generated by Cortapis Security App*
`;
  }
}

// Export for use in Node.js or modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CortapisApp;
}
