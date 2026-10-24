from .base import *

DEBUG = os.getenv("DEBUG", "True").lower() in {"true", "1", "yes", "on"}

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


INTERNAL_IPS = [
    "127.0.0.1",
]