from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('books/', views.books, name='books'),
    path('books/add/', views.add_book, name='add_book'),
    path('issue/', views.issue_book, name='issue_book'),
    path('return/', views.return_book, name='return_book'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/update/<int:book_id>/', views.update_stock, name='update_stock'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
]