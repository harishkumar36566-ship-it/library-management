from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Book, IssueBook
from .forms import BookForm

# =========================
# USER AUTHENTICATION
# =========================
def user_login(request):
    """Handle user login."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "library/login.html")


@login_required
def user_logout(request):
    """Logout the current user."""
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect("login")


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    """Dashboard showing summary of books and issues"""

    total_books = Book.objects.count()
    available_books = Book.objects.filter(available_copies__gt=0).count()
    issued_books_count = IssueBook.objects.filter(returned=False).count()
    overdue_books = IssueBook.objects.filter(returned=False, return_date__lt=timezone.now()).count()

    # Pass **recent issued books** for table
    recent_issued_books = IssueBook.objects.filter(returned=False).order_by('-issue_date')

    context = {
        "total_books": total_books,
        "available_books": available_books,
        "issued_books": issued_books_count,
        "overdue_books": overdue_books,
        "issued_books": recent_issued_books,  # pass queryset, not count
    }
    return render(request, "library/dashboard.html", context)


# =========================
# VIEW BOOKS
# =========================
@login_required
def books(request):
    """List all books with search and stock status."""
    search_query = request.GET.get("q", "")
    if search_query:
        books = Book.objects.filter(title__icontains=search_query) | Book.objects.filter(author__icontains=search_query)
    else:
        books = Book.objects.all()

    # Add stock status dynamically
    for book in books:
        if book.available_copies == 0:
            book.status = "Out of Stock"
        elif book.available_copies <= 2:
            book.status = "Low Stock"
        else:
            book.status = "Available"

    return render(request, "library/books.html", {
        "books": books,
        "search_query": search_query
    })


# =========================
# ISSUE BOOK
# =========================
@login_required
def issue_book(request):
    """Issue a book to a buyer and decrement stock."""
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        buyer_name = request.POST.get("buyer_name")
        buyer_phone = request.POST.get("buyer_phone")
        buyer_email = request.POST.get("buyer_email")

        book = get_object_or_404(Book, id=book_id)

        if book.available_copies <= 0:
            messages.error(request, f"'{book.title}' is out of stock")
            return redirect("issue_book")

        # Create issue entry
        IssueBook.objects.create(
            user=request.user,
            book=book,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            buyer_email=buyer_email,
            issue_date=timezone.now(),
            returned=False
        )

        # Decrement stock
        book.available_copies -= 1
        book.save()

        messages.success(request, f"Book '{book.title}' issued successfully")
        return redirect("issue_book")

    # GET request – show available books
    search_query = request.GET.get("q", "")
    if search_query:
        books = Book.objects.filter(available_copies__gt=0, title__icontains=search_query) | Book.objects.filter(available_copies__gt=0, author__icontains=search_query)
    else:
        books = Book.objects.filter(available_copies__gt=0)

    for book in books:
        book.status = "Low Stock" if book.available_copies <= 2 else "Available"

    return render(request, "library/issue_book.html", {
        "books": books,
        "search_query": search_query
    })


# =========================
# RETURN BOOK
# =========================
@login_required
def return_book(request):
    """Return issued book, calculate fine, and update stock."""
    if request.method == "POST":
        issue_id = request.POST.get("issue_id")
        issue = get_object_or_404(IssueBook, id=issue_id)

        if issue.returned:
            messages.warning(request, "This book is already returned")
        else:
            issue.returned = True
            issue.save()  # Fine handled in model

            # Update book stock
            book = issue.book
            book.available_copies += 1
            book.save()

            if issue.fine > 0:
                messages.success(request, f"Book returned successfully. Fine: ₹{issue.fine}")
            else:
                messages.success(request, "Book returned successfully. No fine")

        return redirect("return_book")

    # GET request – show issued books
    issued_books = IssueBook.objects.filter(returned=False).order_by("-issue_date")

    return render(request, "library/return_book.html", {"issued_books": issued_books})


# =========================
# ADD BOOK
# =========================
@login_required
def add_book(request):
    """Add a new book to library."""
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.quantity
            book.save()
            messages.success(request, "Book added successfully")
            return redirect("books")
    else:
        form = BookForm()

    return render(request, "library/add_book.html", {"form": form})


# =========================
# UPDATE STOCK
# =========================
@login_required
def update_stock(request, book_id):
    """Update stock quantity of a book."""
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        try:
            new_quantity = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            messages.error(request, "Invalid quantity")
            return redirect("update_stock", book_id=book.id)

        if new_quantity < 0:
            messages.error(request, "Quantity cannot be negative")
        else:
            difference = new_quantity - book.quantity
            book.quantity = new_quantity
            book.available_copies += difference
            if book.available_copies < 0:
                book.available_copies = 0
            book.save()
            messages.success(request, "Stock updated successfully")
            return redirect("books")

    return render(request, "library/update_stock.html", {"book": book})


# =========================
# EDIT BOOK
# =========================
@login_required
def edit_book(request, book_id):
    """Edit book details."""
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully")
            return redirect("books")
    else:
        form = BookForm(instance=book)

    return render(request, "library/edit_book.html", {"form": form, "book": book})


# =========================
# DELETE BOOK
# =========================
@login_required
def delete_book(request, book_id):
    """Delete a book from library."""
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("books")

    return render(request, "library/delete_book.html", {"book": book})