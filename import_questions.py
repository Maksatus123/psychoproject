import os
import django
import csv
from main.models import Questions 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychoproject.settings')
django.setup()

def import_questions():
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'questions.csv')
    
    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Questions.objects.update_or_create(
                num=int(row['num']),
                defaults={
                    'quest': row['quest'],
                    'y': float(row['y']),
                    'n': float(row['n'])
                }
            )

    print(f"Импорт завершен. Проверьте таблицу Questions.")

if __name__ == "__main__":
    import_questions()