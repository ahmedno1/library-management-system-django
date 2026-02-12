from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.http import urlencode
from django import forms

from .models import Author, Book, Category
from borrowing.models import BorrowRecord
from reviews.models import Review
from .models import ContactMessage


def home(request):
    """
    Public landing page showing hero, latest books, top rated picks, and site stats.
    Queries are kept narrow with select_related/annotations to avoid N+1s.
    """
    latest_books = (
        Book.objects.select_related("author", "category")
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        )
        .order_by("-created_at")[:6]
    )

    top_rated_books = (
        Book.objects.select_related("author", "category")
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        )
        .filter(review_count__gt=0)
        .order_by("-avg_rating", "-review_count", "-created_at")[:3]
    )

    User = get_user_model()
    stats = {
        "books": Book.objects.count(),
        "authors": Author.objects.count(),
        "categories": Category.objects.count(),
        "users": User.objects.count(),
    }

    context = {
        "latest_books": latest_books,
        "top_rated_books": top_rated_books,
        "stats": stats,
    }
    return render(request, "library/home.html", context)


def book_list(request):
    """
    Public list of books with search, category filter, sort, and pagination.
    Uses annotations for ratings to keep sorting and display efficient.
    """
    books_qs = (
        Book.objects.select_related("author", "category")
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        )
    )

    query = request.GET.get("q", "").strip()
    if query:
        books_qs = books_qs.filter(
            Q(title__icontains=query) | Q(author__full_name__icontains=query)
        )

    category_param = request.GET.get("category")
    category_obj = None
    if category_param:
        category_obj = Category.objects.filter(slug=category_param).first()
        if not category_obj and category_param.isdigit():
            category_obj = Category.objects.filter(id=category_param).first()
        if category_obj:
            books_qs = books_qs.filter(category=category_obj)

    sort_param = request.GET.get("sort", "newest")
    if sort_param == "oldest":
        books_qs = books_qs.order_by("created_at")
    elif sort_param == "rating":
        books_qs = books_qs.order_by("-avg_rating", "-review_count", "-created_at")
    else:
        sort_param = "newest"
        books_qs = books_qs.order_by("-created_at")

    paginator = Paginator(books_qs, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.order_by("name")

    base_querydict = request.GET.copy()
    base_querydict.pop("page", None)
    preserved_query = urlencode([(k, v) for k, v in base_querydict.items() if v])

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_obj,
        "query": query,
        "sort": sort_param,
        "preserved_query": preserved_query,
    }
    return render(request, "library/book_list.html", context)


def book_detail(request, pk):
    """
    Public book detail page with metadata, availability, rating, and recent reviews.
    """
    book = get_object_or_404(
        Book.objects.select_related("author", "category").annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        ),
        pk=pk,
    )

    reviews = (
        book.reviews.select_related("user")
        .order_by("-created_at")
    )

    already_borrowed = False
    can_borrow = False
    user_review = None
    can_review = False
    has_returned = False
    if request.user.is_authenticated:
        already_borrowed = BorrowRecord.objects.filter(
            user=request.user, book=book, returned_at__isnull=True
        ).exists()
        active_count = BorrowRecord.objects.filter(
            user=request.user, returned_at__isnull=True
        ).count()
        can_borrow = book.available_copies > 0 and not already_borrowed and active_count < 5

        user_review = Review.objects.filter(user=request.user, book=book).first()
        has_returned = BorrowRecord.objects.filter(
            user=request.user, book=book, returned_at__isnull=False
        ).exists()
        can_review = has_returned and user_review is None

    context = {
        "book": book,
        "reviews": reviews,
        "already_borrowed": already_borrowed,
        "can_borrow": can_borrow,
        "user_review": user_review,
        "can_review": can_review,
        "has_returned": has_returned,
    }
    return render(request, "library/book_detail.html", context)


# Categories
def category_list(request):
    categories = Category.objects.annotate(
        book_count=Count("books")
    ).order_by("name")
    return render(request, "library/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    books = (
        category.books.select_related("author", "category")
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        )
        .order_by("-created_at")
    )
    return render(
        request,
        "library/category_detail.html",
        {"category": category, "books": books},
    )


# Authors
def author_list(request):
    authors = Author.objects.annotate(book_count=Count("books")).order_by("full_name")
    return render(request, "library/author_list.html", {"authors": authors})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = (
        author.books.select_related("author", "category")
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__stars", output_field=DecimalField(max_digits=3, decimal_places=1)),
                Value(0, output_field=DecimalField(max_digits=3, decimal_places=1)),
            ),
            review_count=Count("reviews"),
        )
        .order_by("-created_at")
    )
    return render(request, "library/author_detail.html", {"author": author, "books": books})


# Contact
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "How can we help?"}),
        }


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks! Your message has been sent.")
            return redirect("library:contact")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    contact_info = {
        "email": "support@elibrary.local",
        "phone": "+1 (555) 123-4567",
        "address": "123 Library Lane, Booktown, USA",
    }
    return render(request, "library/contact.html", {"form": form, "contact_info": contact_info})
