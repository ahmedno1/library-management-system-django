from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from library.models import Book

from .models import BorrowRecord


@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if book.available_copies <= 0:
        messages.warning(request, "No copies available right now.")
        return redirect(request.META.get("HTTP_REFERER", reverse("library:book_detail", args=[pk])))

    active_borrows = BorrowRecord.objects.filter(user=request.user, returned_at__isnull=True)

    if active_borrows.count() >= 5:
        messages.error(request, "You have reached the maximum of 5 active borrows.")
        return redirect(request.META.get("HTTP_REFERER", reverse("library:book_detail", args=[pk])))

    if active_borrows.filter(book=book).exists():
        messages.info(request, "You already have an active borrow for this book.")
        return redirect(request.META.get("HTTP_REFERER", reverse("library:book_detail", args=[pk])))

    try:
        BorrowRecord.objects.create(user=request.user, book=book)
        messages.success(request, f"You borrowed “{book.title}”.")
    except Exception as exc:  # e.g., ValidationError
        messages.error(request, str(exc))

    return redirect(request.META.get("HTTP_REFERER", reverse("library:book_detail", args=[pk])))


@login_required
def my_borrowed_books(request):
    records = (
        BorrowRecord.objects.select_related("book", "book__author", "book__category")
        .filter(user=request.user, returned_at__isnull=True)
        .order_by("due_at")
    )
    return render(request, "borrowing/my_books.html", {"records": records})


@login_required
def return_book(request, record_id):
    record = get_object_or_404(
        BorrowRecord.objects.select_related("book"), pk=record_id, user=request.user
    )
    if record.returned_at is not None:
        messages.info(request, "This borrow was already returned.")
    else:
        record.mark_returned()
        messages.success(request, f'Returned "{record.book.title}".')
    return redirect(request.META.get("HTTP_REFERER", reverse("borrowing:my_books")))
