import uuid
import hashlib

from django.conf import settings

def confirmation_token(text):
    """Basic hashing function for a text using random unique salt."""
    salt = settings.SECRET_KEY
    return hashlib.sha256(salt.encode() + text.encode()).hexdigest() + ':' + salt

def validate_confirmation_token(hashedText, providedText):
    """Check for the text in the hashed text"""
    _hashedText, salt = hashedText.split(':')
    return _hashedText == hashlib.sha256(salt.encode() + providedText.encode()).hexdigest()
