import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения, указывающей на файл настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')

# Подключение настроек Celery из файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач в Django приложениях
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'run-scheduled-task': {
        'task': 'loans.tasks.scheduled_task',
        'schedule': crontab(hour=21, minute=22)
    },
}