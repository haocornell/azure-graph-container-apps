import os
import secrets

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('AZURE_SECRET_KEY') or secrets.token_hex()

DEBUG = False
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
