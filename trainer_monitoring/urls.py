<<<<<<< HEAD
# trainer_monitoring/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('training/', include('training.urls')),
    path('', include('core.urls')),          # For user‑signup / login / home (or auth related)

    # ... other URLs
]
=======
"""
URL configuration for trainer_monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include   # <-- path must be imported


urlpatterns = [
    path('admin/', admin.site.urls),
    path('training/', include('training.urls')),
    path('', include('core.urls')),          # For user‑signup / login / home (or auth related)
]


>>>>>>> origin/main
