from django.urls import path

from .views import NewsletterSubscribers, NewsletterSubscribersItem

utils_urlpatterns = [
    path(
        "newsletter-subscribers/",
        NewsletterSubscribers.as_view(),
        name="newsletter-subscribers",
    ),
    path(
        "newsletter-subscribers/<uuid:uuid>/",
        NewsletterSubscribersItem.as_view(),
        name="newsletter-subscribers-item",
    ),
]
