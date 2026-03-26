from django.contrib import admin
from .models import Book, IssueBook

admin.site.register(Book)
admin.site.register(IssueBook)