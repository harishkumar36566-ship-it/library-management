# library/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# ======================
# Helper function for default return date
# ======================
def default_return_date():
    """Return date 7 days from today"""
    return timezone.now().date() + timedelta(days=7)

# ======================
# Book Model
# ======================
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

# ======================
# IssueBook Model with Fine Calculation
# ======================
class IssueBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=255)
    buyer_phone = models.CharField(max_length=20)
    buyer_email = models.EmailField()
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(default=default_return_date)  # Use helper function
    returned = models.BooleanField(default=False)
    fine_per_day = 5  # ₹5 fine per day

    @property
    def fine(self):
        """
        Calculate fine dynamically based on overdue days.
        Fine = fine_per_day * overdue_days
        Returns 0 if not overdue or already returned.
        """
        if self.returned:
            return 0
        today = timezone.now().date()
        overdue_days = (today - self.return_date).days
        if overdue_days > 0:
            return overdue_days * self.fine_per_day
        return 0

    def __str__(self):
        return f"{self.book.title} issued to {self.user.username}"