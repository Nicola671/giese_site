# giese_site/settings.py
import os
from pathlib import Path

# ========== Carga .env (no rompe si falta) ==========
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ========== Paths básicos ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== Seguridad / entorno ==========
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DEBUG = os.getenv("DEBUG", "False").strip().lower() == "true"

# hosts separados por coma
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv(
        "ALLOWED_HOSTS",
        "giese-site.onrender.com,localhost,127.0.0.1"
    ).split(",") if h.strip()
]

# ========== Apps ==========
INSTALLED_APPS = [
    # Media en la nube (solo si se define CLOUDINARY_URL)
    "cloudinary",
    "cloudinary_storage",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tu app
    "core",
]

# ========== Middleware ==========
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Sirve archivos estáticos en producción
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "giese_site.urls"

# ========== Templates ==========
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "giese_site.wsgi.application"

# ========== Base de datos ==========
# Si hay DATABASE_URL => Postgres (Render). Si no, usa MySQL local.
DB_URL = os.getenv("DATABASE_URL", "").strip()
if DB_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=DB_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DATABASE", "giese_db"),
            "USER": os.getenv("MYSQL_USER", "root"),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
            "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        }
    }

# ========== Localización ==========
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# ========== Archivos estáticos (WhiteNoise) ==========
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Solo agrega la carpeta si existe en el repo (útil para local)
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

# ========== Archivos de media ==========
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Si hay CLOUDINARY_URL en el entorno (Render), usá Cloudinary para MEDIA.
if os.getenv("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    # (STATIC sigue con WhiteNoise; no uses Cloudinary para static)

# ========== Proxy/Seguridad detrás de Render ==========
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF: confiar en tus hosts (excepto localhost y 127.0.0.1)
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
