import sys
import logging

logging.basicConfig(level=logging.DEBUG, filename='/var/www/html/webformFactory/logs/webforms.log', format='%(asctime)s %(message)s')
sys.path.insert(0, '/var/www/html/webformFactory')
sys.path.insert(0, '/var/www/html/flask-app/venv/lib/python3.10/site-packages')
from application import app as application
