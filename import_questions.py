import os
import django
import csv
from django.conf import settings

# Настройка Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychoproject.settings')
django.setup()

from main.models import Questions

def import_questions():
    csv_path = os.path.join(BASE_DIR, 'data', 'questions.csv')
    
    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        # Читаем CSV с разделителем ';'
        reader = csv.reader(csvfile, delimiter=';')
        
        for row in reader:
            if not row:  # Пропускаем пустые строки
                continue
                
            try:
                # Парсим строку (ваш формат: "1. Текст вопроса;1;1;")
                question_text = row[0].split('.', 1)[1].strip()  # Удаляем номер перед точкой
                num = int(row[0].split('.', 1)[0])  # Номер из начала строки
                
                # Обрабатываем значения y/n (могут быть пустыми)
                y_value = float(row[1]) if row[1] else 0.0
                n_value = float(row[2]) if row[2] else 0.0
                
                Questions.objects.update_or_create(
                    num=num,
                    defaults={
                        'quest': question_text,
                        'y': y_value,
                        'n': n_value
                    }
                )
                print(f"Добавлен вопрос №{num}")
                
            except Exception as e:
                print(f"Ошибка при обработке строки: {row}")
                print(f"Подробности: {str(e)}")
                continue

    print(f"Импорт завершен. Всего вопросов: {Questions.objects.count()}")

if __name__ == "__main__":
    import_questions()