"""
Cortapis Web Interface
-----------------------
Flask-based web application for easy access to Cortapis security features
with a "call window" UI similar to Matrix aesthetics
"""

from flask import Flask, render_template, request, jsonify
from cortapis import CortapisSecurityEngine, EmailStyleAutocomplete
import json
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize security engine
engine = CortapisSecurityEngine()
autocomplete = EmailStyleAutocomplete()

# Store for encrypted sessions
encrypted_sessions = {}


@app.route('/')
def index():
    """Main interface - "Call window" to Cortapis"""
    return render_template('index.html', encryption_key=engine.get_encryption_key())


@app.route('/api/encrypt', methods=['POST'])
def encrypt_text():
    """
    API endpoint: WRITE MODE
    Encrypts text with sensitive token marking
    """
    try:
        data = request.json
        text = data.get('text', '')
        patterns = data.get('patterns', None)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        encrypted_data = engine.write_mode(text, patterns)
        
        # Store encrypted session
        session_id = os.urandom(16).hex()
        encrypted_sessions[session_id] = encrypted_data
        encrypted_data['session_id'] = session_id
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'encrypted_content': encrypted_data['encrypted_content'],
            'token_count': len(encrypted_data['token_map']),
            'message': 'Text encrypted and protected against indexing'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/decrypt', methods=['POST'])
def decrypt_text():
    """
    API endpoint: READ MODE
    Opens the "call window" to decrypt and expose content
    """
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if session_id not in encrypted_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        encrypted_data = encrypted_sessions[session_id]
        decrypted = engine.read_mode(encrypted_data)
        
        return jsonify({
            'success': True,
            'decrypted_content': decrypted,
            'message': 'Content exposed - "Call window" is now open'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mark-sensitive', methods=['POST'])
def mark_sensitive():
    """
    API endpoint: Mark specific text as sensitive with @ symbols
    """
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        marked_text, token_map = engine.mark_sensitive_tokens(text)
        
        return jsonify({
            'success': True,
            'marked_text': marked_text,
            'token_map': token_map,
            'tokens_found': len(token_map)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/obfuscate', methods=['POST'])
def obfuscate():
    """
    API endpoint: Obfuscate text with @ symbols for anti-indexing
    """
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        obfuscated = engine.obfuscate_text(text)
        
        return jsonify({
            'success': True,
            'original': text,
            'obfuscated': obfuscated,
            'message': 'Text obfuscated to appear corrupted to indexers'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-markdown', methods=['POST'])
def export_markdown():
    """
    API endpoint: Export encrypted content as Markdown
    """
    try:
        data = request.json
        session_id = data.get('session_id', '')
        original_text = data.get('original_text', '')
        
        if session_id not in encrypted_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        encrypted_data = encrypted_sessions[session_id]
        markdown = engine.export_to_markdown(original_text, encrypted_data)
        
        return jsonify({
            'success': True,
            'markdown': markdown,
            'filename': 'cortapis_protected_document.md'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-key', methods=['GET'])
def get_key():
    """Get the encryption key for reference"""
    return jsonify({
        'encryption_key': engine.get_encryption_key(),
        'message': 'Keep this key safe - it is required for decryption'
    })


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active encrypted sessions"""
    sessions_list = []
    for session_id, data in encrypted_sessions.items():
        sessions_list.append({
            'session_id': session_id,
            'token_count': len(data['token_map']),
            'status': data['status']
        })
    
    return jsonify({
        'sessions': sessions_list,
        'total': len(sessions_list)
    })


@app.route('/api/clear-session', methods=['DELETE'])
def clear_session():
    """Clear a specific session"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if session_id in encrypted_sessions:
            del encrypted_sessions[session_id]
            return jsonify({'success': True, 'message': 'Session cleared'})
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
