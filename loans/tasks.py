from celery import shared_task

from loans.management.commands.bot import send_notification

@shared_task
def scheduled_task():
    # Здесь вы можете добавить свой код для выполнения задачи
    print("Периодическая задача выполнена!")
    send_notification(chat_id=6163834488, text='Проверка прошла успешно')
    
    
@shared_task
def test_task():
    # Здесь вы можете добавить свой код для выполнения задачи
    print("Тестовая задача выполнена!")

