import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from borrowing.models import BorrowRecord
from library.models import Author, Book, Category
from reviews.models import Review


class Command(BaseCommand):
    help = "Seed the database with realistic demo data (categories, authors, books, users, borrows, reviews)."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)  # deterministic-ish for repeatability; change or remove for more randomness

        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        categories = self._create_categories()
        authors = self._create_authors()
        books = self._create_books(authors, categories)
        users = self._create_users()
        borrow_records = self._create_borrows(users, books)
        self._create_reviews(borrow_records)

        self.stdout.write(self.style.SUCCESS("Done seeding demo data."))

    # --- Builders ---------------------------------------------------------

    def _create_categories(self):
        names = [
            "Information Technology",
            "History",
            "Science",
            "Novels",
            "Artificial Intelligence",
            "Medicine",
            "Business",
            "Psychology",
            "Philosophy",
            "Design",
        ]
        categories = []
        for name in names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)
        return categories

    def _create_authors(self):
        names = [
            "Amelia Carter",
            "Noah Sullivan",
            "Olivia Bennett",
            "Liam Thompson",
            "Sophia Reyes",
            "Ethan Wallace",
            "Isabella Park",
            "Mason Rivera",
            "Mia Coleman",
            "Lucas Patel",
            "Charlotte Kim",
            "Elijah Brooks",
            "Harper Lewis",
            "James Gardner",
            "Ava Hughes",
            "Benjamin Scott",
            "Emily Foster",
            "Alexander Ward",
            "Abigail Torres",
            "Michael Price",
            "Ella Murphy",
            "Henry Sanders",
            "Victoria Ross",
            "Samuel Perry",
            "Grace Howard",
            "Daniel Hayes",
            "Natalie Cooper",
            "Jack Morgan",
            "Zoe Bryant",
        ]
        authors = []
        for full_name in names:
            author, _ = Author.objects.get_or_create(full_name=full_name)
            authors.append(author)
        return authors

    def _create_books(self, authors, categories):
        title_prefixes = ["The Art of", "Mastering", "Exploring", "Foundations of", "Advanced", "Practical"]
        title_subjects = [
            "Machine Learning",
            "Data Structures",
            "Deep History",
            "Cognitive Science",
            "Modern Medicine",
            "Creative Writing",
            "Business Strategy",
            "Cloud Computing",
            "Quantum Physics",
            "Cyber Security",
            "Product Design",
            "Psychological Safety",
            "Financial Literacy",
            "Green Energy",
            "AI Ethics",
        ]

        books = []
        existing = Book.objects.count()
        target = max(60, existing + 60)  # ensure at least 60 total
        while Book.objects.count() < target and len(books) < 100:
            title = f"{random.choice(title_prefixes)} {random.choice(title_subjects)}"
            author = random.choice(authors)
            category = random.choice(categories)
            language = random.choice(["English", "Arabic"])
            pages = random.randint(80, 600)
            total_copies = random.randint(1, 5)

            book, created = Book.objects.get_or_create(
                title=title,
                author=author,
                category=category,
                defaults={
                    "description": f"A comprehensive look at {title.lower()}.",
                    "language": language,
                    "publication_year": random.randint(1995, 2024),
                    "pages": pages,
                    "total_copies": total_copies,
                    "available_copies": total_copies,
                },
            )
            if created:
                books.append(book)

        if not books:
            books = list(Book.objects.all())
        return books

    def _create_users(self):
        User = get_user_model()
        usernames = [
            "alex", "sara", "mohamed", "fatima", "john", "linda", "omar", "nora", "david", "emma",
            "liam", "sophia", "youssef", "layla", "mason", "amelia", "hassan", "maria", "ethan", "hana",
            "samir", "oliver", "yasmin", "adam", "salma", "james", "farah"
        ]

        users = []
        for username in usernames:
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )
            if created:
                user.set_password("password123")
                user.first_name = username.capitalize()
                user.last_name = random.choice(["Smith", "Khan", "Hassan", "Brown", "Lee", "Garcia", "Youssef", "Ali"])
                user.save()
            users.append(user)
        return users

    def _create_borrows(self, users, books):
        borrow_records = []
        remaining = {b.id: b.available_copies for b in books}
        for user in users:
            active_slots = random.randint(0, 4)  # keep under limit 5
            chosen_books = random.sample(books, min(len(books), active_slots + random.randint(0, 3)))
            active_count = 0

            for book in chosen_books:
                if active_count >= 5:
                    break
                # ensure availability before borrowing (use tracked remaining to avoid overdraw)
                if remaining.get(book.id, 0) <= 0:
                    continue

                borrowed_at = timezone.now() - timedelta(days=random.randint(0, 25))
                due_at = borrowed_at + timedelta(days=14)

                record = BorrowRecord.objects.create(
                    user=user,
                    book=book,
                    borrowed_at=borrowed_at,
                    due_at=due_at,
                )
                borrow_records.append(record)
                active_count += 1
                remaining[book.id] = remaining.get(book.id, 0) - 1

                # Some will be returned
                if random.random() < 0.6:
                    record.returned_at = borrowed_at + timedelta(days=random.randint(1, 20))
                    record.save(update_fields=["returned_at"])
                    remaining[book.id] = remaining.get(book.id, 0) + 1
        return borrow_records

    def _create_reviews(self, borrow_records):
        comments = [
            "Great reference, very clear.",
            "Enjoyed the examples.",
            "Dense but rewarding.",
            "Perfect for beginners.",
            "Could use more diagrams.",
            "Loved the real-world cases.",
            "Well structured and concise.",
            "Challenging but insightful.",
        ]

        for record in borrow_records:
            if record.returned_at is None:
                continue  # only review returned books

            if Review.objects.filter(user=record.user, book=record.book).exists():
                continue

            stars = random.randint(3, 5) if random.random() < 0.7 else random.randint(1, 5)
            comment = random.choice(comments)

            Review.objects.create(
                user=record.user,
                book=record.book,
                stars=stars,
                comment=comment,
            )
