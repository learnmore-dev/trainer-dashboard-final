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