from django.utils import timezone

from .models import PageVisit


class PageVisitMiddleware:
    """
    Logs lightweight visit info for public pages.
    Skips admin, static, media to avoid noise.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not (path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/")):
            try:
                PageVisit.objects.create(
                    path=path,
                    method=request.method,
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                    created_at=timezone.now(),
                )
            except Exception:
                # Never block the request if logging fails
                pass

        response = self.get_response(request)
        return response
