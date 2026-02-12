from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from borrowing.models import BorrowRecord
from library.models import Book

from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    existing = Review.objects.filter(user=request.user, book=book).first()

    has_returned = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        returned_at__isnull=False,
    ).exists()

    if not has_returned:
        messages.error(request, "Return this book before leaving a review.")
        return redirect("library:book_detail", pk=book_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, "Thanks for your review!" if existing is None else "Review updated.")
            return redirect("library:book_detail", pk=book_id)
        messages.error(request, "Please fix the errors below.")
    else:
        form = ReviewForm(instance=existing)

    return render(request, "reviews/add_review.html", {"form": form, "book": book})
