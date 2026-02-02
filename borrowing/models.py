from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class BorrowRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrow_records",
    )
    book = models.ForeignKey(
        "library.Book",
        on_delete=models.PROTECT,
        related_name="borrow_records",
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]
        indexes = [
            models.Index(fields=["user", "returned_at"]),
            models.Index(fields=["book", "returned_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        status = self.status
        return f"{self.user} -> {self.book} ({status})"

    # Properties
    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    @property
    def is_overdue(self) -> bool:
        return self.is_active and timezone.now() > self.due_at

    @property
    def remaining_days(self) -> int:
        if not self.is_active:
            return 0
        delta = self.due_at - timezone.now()
        return max(delta.days, 0)

    @property
    def status(self) -> str:
        if not self.is_active:
            return "returned"
        if self.is_overdue:
            return "overdue"
        return "active"

    # Validation
    def clean(self):
        super().clean()
        if self.pk is None:
            if self.user_id:
                active_count = (
                    BorrowRecord.objects.filter(user=self.user, returned_at__isnull=True)
                    .exclude(pk=self.pk)
                    .count()
                )
                if active_count >= 5:
                    raise ValidationError("User has reached the maximum of 5 active borrows.")

                if (
                    BorrowRecord.objects.filter(
                        user=self.user, book=self.book, returned_at__isnull=True
                    )
                    .exclude(pk=self.pk)
                    .exists()
                ):
                    raise ValidationError("User already has an active borrow for this book.")

    # Core actions
    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self.pk is None

            if is_new:
                now = timezone.now()
                if not self.borrowed_at:
                    self.borrowed_at = now

                duration_days = getattr(settings, "BORROW_DURATION_DAYS", 14)  # Change duration in config/settings.py
                if not self.due_at:
                    self.due_at = self.borrowed_at + timedelta(days=duration_days)

                # Lock the book row to ensure availability is accurate.
                book = (
                    self.book.__class__.objects.select_for_update()
                    .only("id", "available_copies")
                    .get(pk=self.book_id)
                )
                if book.available_copies <= 0:
                    raise ValidationError({"book": "No copies are currently available for this title."})

                # Run validations after we have book context.
                self.full_clean()

                # Reserve a copy.
                book.available_copies -= 1
                book.save(update_fields=["available_copies"])

                super().save(*args, **kwargs)
                return

            # Updating an existing record
            previous = (
                BorrowRecord.objects.select_for_update()
                .only("returned_at", "book_id")
                .get(pk=self.pk)
            )
            returning_now = previous.returned_at is None and self.returned_at is not None

            self.full_clean()
            super().save(*args, **kwargs)

            if returning_now:
                book = (
                    self.book.__class__.objects.select_for_update()
                    .only("id", "available_copies")
                    .get(pk=self.book_id)
                )
                book.available_copies += 1
                book.save(update_fields=["available_copies"])

    def mark_returned(self):
        if not self.is_active:
            return
        self.returned_at = timezone.now()
        self.save(update_fields=["returned_at"])
