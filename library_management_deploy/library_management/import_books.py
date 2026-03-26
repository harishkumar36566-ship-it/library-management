import os
import django
import csv

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_management.settings")
django.setup()

from library.models import Book

csv_file_path = 'books.csv'

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        quantity = int(row['quantity'])
        book, created = Book.objects.get_or_create(
            isbn=row['isbn'],
            defaults={
                'title': row['title'],
                'author': row['author'],
                'quantity': quantity,
                'available_copies': quantity
            }
        )
        if created:
            print(f"Added book: {book.title}")
        else:
            print(f"Book with ISBN {row['isbn']} already exists.")