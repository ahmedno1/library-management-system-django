from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from borrowing.models import BorrowRecord


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    book = models.ForeignKey(
        "library.Book",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="unique_review_per_user_book")
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.user} -> {self.book} ({self.stars} stars)"

    def clean(self):
        super().clean()
        if self.user_id and self.book_id:
            has_borrowed_and_returned = BorrowRecord.objects.filter(
                user_id=self.user_id,
                book_id=self.book_id,
                returned_at__isnull=False,
            ).exists()
            if not has_borrowed_and_returned:
                raise ValidationError(
                    "User must have borrowed and returned this book before submitting a review."
                )
