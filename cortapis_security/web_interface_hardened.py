"""
Cortapis Web Interface - Hardened Version v2.0
Flask-based web application with security best practices
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cortapis_enhanced import CortapisSecurityEngineV2
from security_config import SecurityConfig, HeadersConfig, CORSConfig
import os
import logging
from datetime import datetime, timedelta
from functools import wraps
import json

# Configure logging
logging.basicConfig(
    level=SecurityConfig.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SecurityConfig.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['JSON_SORT_KEYS'] = False

# Disable debug mode in production
app.debug = SecurityConfig.DEBUG

# Validate security configuration
config_errors = SecurityConfig.validate_config()
if config_errors:
    logger.warning("Security warnings:")
    for error in config_errors:
        logger.warning(f"  - {error}")

# Initialize CORS with security settings
CORS(
    app,
    resources={r"/api/*": {
        "origins": SecurityConfig.CORS_ORIGINS,
        "methods": CORSConfig.CORS_METHODS,
        "allow_headers": CORSConfig.CORS_HEADERS,
        "max_age": CORSConfig.CORS_MAX_AGE
    }}
)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{SecurityConfig.RATE_LIMIT_REQUESTS}/{SecurityConfig.RATE_LIMIT_PERIOD//60}m"]
)

# Initialize security engine with key from environment
encryption_key = SecurityConfig.ENCRYPTION_KEY
if not encryption_key:
    logger.error("CRITICAL: CORTAPIS_ENCRYPTION_KEY not set in environment variables")
    raise ValueError("CORTAPIS_ENCRYPTION_KEY environment variable must be set")

try:
    engine = CortapisSecurityEngineV2(encryption_key=encryption_key)
    logger.info("Cortapis Security Engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize engine: {str(e)}")
    raise

# Session storage with expiration
encrypted_sessions = {}
session_cleanup_interval = SecurityConfig.CLEAN_SESSIONS_INTERVAL
last_cleanup = datetime.utcnow()


def cleanup_expired_sessions():
    """Remove expired sessions from memory"""
    global last_cleanup
    
    now = datetime.utcnow()
    if (now - last_cleanup).seconds > session_cleanup_interval:
        expired_count = 0
        for session_id in list(encrypted_sessions.keys()):
            session_data = encrypted_sessions[session_id]
            session_time = datetime.fromisoformat(session_data.get('created_at', now.isoformat()))
            
            if (now - session_time) > SecurityConfig.SESSION_EXPIRATION:
                del encrypted_sessions[session_id]
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")
        last_cleanup = now


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SecurityConfig.API_KEY_REQUIRED:
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            logger.warning(f"Unauthorized access attempt from {get_remote_address()}")
            return jsonify({'error': 'Missing API key'}), 401
        
        if api_key not in SecurityConfig.API_KEYS:
            logger.warning(f"Invalid API key from {get_remote_address()}")
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def add_security_headers(f):
    """Decorator to add security headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Add security headers
        for header, value in HeadersConfig.HEADERS.items():
            response.headers[header] = value
        
        return response
    
    return decorated_function


@app.before_request
def check_https():
    """Enforce HTTPS if required"""
    if SecurityConfig.ENFORCE_HTTPS and not request.is_secure:
        logger.warning(f"Non-HTTPS request from {get_remote_address()}")
        return jsonify({'error': 'HTTPS required'}), 403


@app.after_request
def add_headers_to_response(response):
    """Add security headers to every response"""
    for header, value in HeadersConfig.HEADERS.items():
        response.headers[header] = value
    return response


@app.route('/')
def index():
    """Main interface - Call window to Cortapis"""
    cleanup_expired_sessions()
    return render_template('index.html')


@app.route('/api/encrypt', methods=['POST'])
@limiter.limit("20/hour")
@require_api_key
def encrypt_text():
    """
    API endpoint: WRITE MODE
    Encrypts text with sensitive token marking
    """
    try:
        cleanup_expired_sessions()
        
        data = request.json
        text = data.get('text', '').strip() if data else ''
        patterns = data.get('patterns', None) if data else None
        
        if not text:
            logger.warning(f"Empty text from {get_remote_address()}")
            return jsonify({'error': 'No text provided'}), 400
        
        # Validate input
        if len(text) > SecurityConfig.MAX_TEXT_LENGTH:
            logger.warning(f"Text too large from {get_remote_address()}: {len(text)} bytes")
            return jsonify({'error': f'Text exceeds maximum length'}), 413
        
        encrypted_data = engine.write_mode(text, patterns)
        
        # Store encrypted session with metadata
        session_id = os.urandom(16).hex()
        encrypted_sessions[session_id] = {
            **encrypted_data,
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'ip_address': get_remote_address()
        }
        
        logger.info(f"Encryption success. Session: {session_id[:8]}... from {get_remote_address()}")
        
        # NEVER expose token_map in response
        return jsonify({
            'success': True,
            'session_id': session_id,
            'encrypted_content': encrypted_data['encrypted_content'],
            'token_count': len(encrypted_data['token_map']),
            'expires_at': (datetime.utcnow() + SecurityConfig.SESSION_EXPIRATION).isoformat(),
            'message': 'Text encrypted and protected against indexing'
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': 'Invalid input'}), 400
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/decrypt', methods=['POST'])
@limiter.limit("10/hour")
@require_api_key
def decrypt_text():
    """
    API endpoint: READ MODE
    Opens the call window to decrypt and expose content
    """
    try:
        cleanup_expired_sessions()
        
        data = request.json
        session_id = data.get('session_id', '').strip() if data else ''
        
        if not session_id:
            logger.warning(f"Missing session ID from {get_remote_address()}")
            return jsonify({'error': 'Session ID required'}), 400
        
        if session_id not in encrypted_sessions:
            logger.warning(f"Session not found: {session_id[:8]}... from {get_remote_address()}")
            return jsonify({'error': 'Session not found or expired'}), 404
        
        encrypted_data = encrypted_sessions[session_id]
        
        # Check session expiration
        created_at = datetime.fromisoformat(encrypted_data['created_at'])
        if (datetime.utcnow() - created_at) > SecurityConfig.SESSION_EXPIRATION:
            del encrypted_sessions[session_id]
            logger.warning(f"Session expired: {session_id[:8]}...")
            return jsonify({'error': 'Session expired'}), 401
        
        decrypted = engine.read_mode(encrypted_data)
        
        logger.info(f"Decryption success. Session: {session_id[:8]}... from {get_remote_address()}")
        
        return jsonify({
            'success': True,
            'decrypted_content': decrypted,
            'message': 'Content exposed - Call window is open'
        })
        
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({'error': 'Decryption failed'}), 500


@app.route('/api/mark-sensitive', methods=['POST'])
@limiter.limit("30/hour")
@require_api_key
def mark_sensitive():
    """
    API endpoint: Mark specific text as sensitive
    """
    try:
        data = request.json
        text = data.get('text', '').strip() if data else ''
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > SecurityConfig.MAX_TEXT_LENGTH:
            return jsonify({'error': 'Text exceeds maximum length'}), 413
        
        marked_text, token_map = engine.mark_sensitive_tokens(text)
        
        logger.info(f"Marked {len(token_map)} tokens from {get_remote_address()}")
        
        return jsonify({
            'success': True,
            'marked_text': marked_text,
            'tokens_found': len(token_map)
        })
        
    except Exception as e:
        logger.error(f"Mark sensitive error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/obfuscate', methods=['POST'])
@limiter.limit("30/hour")
@require_api_key
def obfuscate():
    """
    API endpoint: Obfuscate text with @ symbols
    """
    try:
        data = request.json
        text = data.get('text', '').strip() if data else ''
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > SecurityConfig.MAX_TEXT_LENGTH:
            return jsonify({'error': 'Text exceeds maximum length'}), 413
        
        obfuscated = engine.obfuscate_text(text)
        
        logger.info(f"Obfuscation success from {get_remote_address()}")
        
        return jsonify({
            'success': True,
            'obfuscated': obfuscated,
            'message': 'Text obfuscated against indexers'
        })
        
    except Exception as e:
        logger.error(f"Obfuscate error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/export-markdown', methods=['POST'])
@limiter.limit("10/hour")
@require_api_key
def export_markdown():
    """
    API endpoint: Export encrypted content as Markdown
    """
    try:
        cleanup_expired_sessions()
        
        data = request.json
        session_id = data.get('session_id', '').strip() if data else ''
        original_text = data.get('original_text', '').strip() if data else ''
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if session_id not in encrypted_sessions:
            logger.warning(f"Session not found for export: {session_id[:8]}...")
            return jsonify({'error': 'Session not found'}), 404
        
        encrypted_data = encrypted_sessions[session_id]
        markdown = engine.export_to_markdown(original_text, encrypted_data, include_key=False)
        
        logger.info(f"Markdown exported. Session: {session_id[:8]}...")
        
        return jsonify({
            'success': True,
            'markdown': markdown,
            'filename': f'cortapis_protected_{session_id[:8]}.md'
        })
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500


@app.route('/api/sessions', methods=['GET'])
@require_api_key
def list_sessions():
    """
    List all active encrypted sessions
    """
    try:
        cleanup_expired_sessions()
        
        sessions_list = []
        for session_id, data in encrypted_sessions.items():
            created_at = datetime.fromisoformat(data['created_at'])
            age = (datetime.utcnow() - created_at).total_seconds()
            
            sessions_list.append({
                'session_id': session_id[:16] + '...',  # Don't expose full ID
                'token_count': len(data['token_map']),
                'status': data['status'],
                'age_seconds': int(age),
                'expires_in_seconds': int((SecurityConfig.SESSION_EXPIRATION.total_seconds()) - age)
            })
        
        logger.info(f"Sessions listed: {len(sessions_list)}")
        
        return jsonify({
            'success': True,
            'sessions': sessions_list,
            'total': len(sessions_list),
            'cleanup_interval': session_cleanup_interval
        })
        
    except Exception as e:
        logger.error(f"List sessions error: {str(e)}")
        return jsonify({'error': 'Failed to list sessions'}), 500


@app.route('/api/clear-session', methods=['DELETE'])
@limiter.limit("20/hour")
@require_api_key
def clear_session():
    """
    Clear a specific session
    """
    try:
        data = request.json
        session_id = data.get('session_id', '').strip() if data else ''
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if session_id in encrypted_sessions:
            del encrypted_sessions[session_id]
            logger.info(f"Session cleared: {session_id[:8]}...")
            return jsonify({'success': True, 'message': 'Session cleared'})
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        logger.error(f"Clear session error: {str(e)}")
        return jsonify({'error': 'Failed to clear session'}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded from {get_remote_address()}")
    return jsonify({'error': 'Rate limit exceeded'}), 429


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Cortapis Security System v2.0 starting...")
    logger.info(f"Debug mode: {app.debug}")
    logger.info(f"HTTPS enforcement: {SecurityConfig.ENFORCE_HTTPS}")
    logger.info(f"Rate limiting: {SecurityConfig.RATE_LIMIT_ENABLED}")
    
    # Use gunicorn in production: gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:5000 cortapis_security.web_interface_hardened:app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.debug,
        use_reloader=False
    )
