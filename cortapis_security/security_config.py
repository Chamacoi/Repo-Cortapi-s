"""
Security Configuration Module
Best practices for securing Cortapis
"""

import os
from datetime import timedelta


class SecurityConfig:
    """Security configuration for Cortapis"""
    
    # === ENCRYPTION ===
    # Store encryption key in environment variable, NEVER in code
    ENCRYPTION_KEY = os.environ.get('CORTAPIS_ENCRYPTION_KEY')
    
    # === SESSION MANAGEMENT ===
    SESSION_EXPIRATION = timedelta(hours=1)  # Sessions expire after 1 hour
    MAX_SESSION_DURATION = timedelta(hours=24)  # Max session lifetime
    CLEAN_SESSIONS_INTERVAL = 300  # Clean expired sessions every 5 minutes (seconds)
    
    # === INPUT VALIDATION ===
    MAX_TEXT_LENGTH = 1_000_000  # 1MB maximum
    MIN_TEXT_LENGTH = 1  # Minimum 1 character
    
    # === RATE LIMITING ===
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100  # 100 requests
    RATE_LIMIT_PERIOD = 3600  # per hour
    
    # === CORS ===
    CORS_ORIGINS = os.environ.get('CORTAPIS_CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # === HTTPS ===
    ENFORCE_HTTPS = os.environ.get('CORTAPIS_ENFORCE_HTTPS', 'True').lower() == 'true'
    
    # === AUTHENTICATION ===
    API_KEY_REQUIRED = os.environ.get('CORTAPIS_API_KEY_REQUIRED', 'True').lower() == 'true'
    API_KEYS = os.environ.get('CORTAPIS_API_KEYS', '').split(',')  # Comma-separated
    
    # === LOGGING ===
    LOG_LEVEL = os.environ.get('CORTAPIS_LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('CORTAPIS_LOG_FILE', 'cortapis.log')
    
    # === DATABASE (Future) ===
    DATABASE_URL = os.environ.get('CORTAPIS_DATABASE_URL', 'sqlite:///cortapis.db')
    
    # === DEBUG ===
    # NEVER enable debug mode in production
    DEBUG = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    @staticmethod
    def validate_config():
        """Validate security configuration"""
        errors = []
        
        if not SecurityConfig.ENCRYPTION_KEY:
            errors.append("⚠️ ENCRYPTION_KEY not set in environment variables")
        
        if not SecurityConfig.API_KEYS or SecurityConfig.API_KEYS[0] == '':
            errors.append("⚠️ API_KEYS not configured")
        
        if SecurityConfig.DEBUG:
            errors.append("⚠️ DEBUG mode is enabled (should be False in production)")
        
        if not SecurityConfig.ENFORCE_HTTPS:
            errors.append("⚠️ HTTPS is not enforced")
        
        return errors


class CORSConfig:
    """CORS Security Settings"""
    CORS_HEADERS = 'Content-Type,Authorization'
    CORS_METHODS = ['GET', 'POST', 'DELETE']
    CORS_MAX_AGE = 3600


class CSRFConfig:
    """CSRF Protection Settings"""
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = 'cortapis_csrf_token'


class HeadersConfig:
    """Security Headers"""
    HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
    }
