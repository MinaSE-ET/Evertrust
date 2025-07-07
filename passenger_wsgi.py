import sys
import os

sys.path.insert(0, "/home/evertrust/public_html/app.evertrust.uk")
os.environ["DJANGO_SETTINGS_MODULE"] = "insurance_system.settings"  # 👈 adjust this

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
