"""qt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from qt_auth.urls import auth_urlpatterns
from qt_billing.urls import billing_urlpatterns
from qt_security.urls import security_urlpatterns
from qt_utils.urls import utils_urlpatterns

api_patterns = [
    path("auth/", include(auth_urlpatterns)),
    path("billing/", include(billing_urlpatterns)),
    path("security/", include(security_urlpatterns)),
    path("utils/", include(utils_urlpatterns)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("v1/", include(api_patterns)),
]
