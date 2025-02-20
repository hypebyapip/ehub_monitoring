# routes/__init__.py
from .monitoring import monitoring_bp
# from .api import api_bp
from .settings import settings_bp

__all__ = ['monitoring_bp', 'api_bp']