"""
WSGI config for point_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import sys
import os
from django.core.wsgi import get_wsgi_application

# Asegúrate de que el directorio del proyecto esté en PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'point_system.point_system.settings')

application = get_wsgi_application()
