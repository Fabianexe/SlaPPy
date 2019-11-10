"""
Entrypoint for WSGI server like gunicorn
"""

from slappy import generate_app

app = generate_app().server
"""The entrypoint can be called as "slappy.wsgi:app". """
