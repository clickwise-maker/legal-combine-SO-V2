"""
Security Utilities — Encryption, Rate Limiting, Validation
"""
import hashlib
import hmac
import time
import re
from functools import wraps
from typing import Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException, status
from ..config import Config


# Simple in-memory rate limiting store
_rate_limit_store: Dict[str, list] = {}


class Security:
    """Security utility class"""

    @staticmethod
    def encrypt_password(password: str) -> str:
        """Encrypt password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_signature(data: str, secret: str) -> str:
        """Generate HMAC signature"""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_signature(data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        expected = Security.generate_signature(data, secret)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input (basic)"""
        return re.sub(r'<[^>]*>', '', text)

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[0-9]{10,15}$'
        return re.match(pattern, phone) is not None


def rate_limit(requests: int = None, period: int = None):
    """
    Rate limiting decorator
    """
    if requests is None:
        requests = Config.RATE_LIMIT_REQUESTS
    if period is None:
        period = Config.RATE_LIMIT_PERIOD

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            
            if request:
                client_ip = request.client.host
                current_time = time.time()
                key = f"{client_ip}:{func.__name__}"
                
                if key not in _rate_limit_store:
                    _rate_limit_store[key] = []
                
                _rate_limit_store[key] = [t for t in _rate_limit_store[key] if current_time - t < period]
                
                if len(_rate_limit_store[key]) >= requests:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Limit: {requests} requests per {period} seconds."
                    )
                
                _rate_limit_store[key].append(current_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
