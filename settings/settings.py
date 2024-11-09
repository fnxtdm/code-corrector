import os
from pathlib import Path

# 构建项目根目录的绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全设置
SECRET_KEY = 'your-secret-key-here'  # 请务必替换为你的实际密钥
DEBUG = True  # 在生产环境中应设置为 False
ALLOWED_HOSTS = ['*']  # 在生产环境中应限制为特定的主机名或 IP 地址列表

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 你的应用
    'src',
    # 第三方应用
    # 'rest_framework',  # 如果使用 Django REST framework
    # 'corsheaders',     # 如果需要跨域资源共享
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 自定义中间件（如果有）
    # 'src.middleware.MyCustomMiddleware',
]

ROOT_URLCONF = 'settings.urls'  # 项目 URL 配置文件的路径

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 模板文件夹路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'  # WSGI 应用的路径

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 数据库引擎
        'NAME': BASE_DIR / 'db.sqlite3',  # 数据库文件路径（SQLite）
        # 如果使用其他数据库，如 PostgreSQL，请配置相应的连接参数
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'yourdbname',
        # 'USER': 'yourdbuser',
        # 'PASSWORD': 'yourdbpassword',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
    }
}

# 密码验证配置
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化和本地化
LANGUAGE_CODE = 'en-us'  # 默认语言
TIME_ZONE = 'UTC'  # 默认时区
USE_I18N = True  # 是否支持国际化
USE_L10N = True  # 是否支持本地化
USE_TZ = True  # 是否使用 UTC 时间

# 静态文件配置
STATIC_URL = '/static/'  # 静态文件访问的 URL 前缀
STATICFILES_DIRS = [BASE_DIR / 'static']  # 静态文件夹路径列表

# 媒体文件配置
MEDIA_URL = '/media/'  # 媒体文件访问的 URL 前缀
MEDIA_ROOT = BASE_DIR / 'media'  # 媒体文件存储的根目录

# 自定义设置
# 你可以在这里添加任何自定义的设置变量
# 例如：
# MY_CUSTOM_SETTING = 'some_value'

# Django Debug Toolbar（如果你使用它）
# 请确保你已经安装了 debug_toolbar 包
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# DEBUG_TOOLBAR_CONFIG = {
#     'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
#     'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
# }
# INTERNAL_IPS = ['127.0.0.1']

# 第三方服务配置（如电子邮件、云存储等）
# 例如，配置电子邮件后端：
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'

# 安全和会话设置
# 在生产环境中，你应该考虑启用以下设置来提高安全性
# SESSION_COOKIE_SECURE = True  # 在 HTTPS 上设置会话 cookie 为安全
# CSRF_COOKIE_SECURE = True     # 在 HTTPS 上设置 CSRF cookie 为安全
# SECURE_BROWSER_XSS_FILTER = True  # 启用 XSS 过滤
# X_FRAME_OPTIONS = 'DENY'      # 防止点击劫持攻击
# SECURE_SSL_REDIRECT = True    # 将所有 HTTP 请求重定向到 HTTPS
# SECURE_HSTS_SECONDS = 31536000  # HSTS 头部中的 max-age 值（以秒为单位）
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # 是否将 HSTS 策略应用于子域
# SECURE_HSTS_PRELOAD = True    # 是否将站点预加载到 HSTS 列表中

# 其他配置...
# 根据你的项目需求添加其他配置