from django.urls import path
from django.contrib.auth import views as auth_views
from . import views   # <-- THIS WAS MISSING

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),   # 👈 THIS FIXES ROOT "/"
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),  # Using custom logout view
]

