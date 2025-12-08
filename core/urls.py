from django.contrib.auth import views as auth_views
from . import views  # for your signup view
from django.urls import path

urlpatterns = [
    # ... other urls ...
     path('signup/', views.signup, name='signup'),
path('', auth_views.LoginView.as_view(), name='login'),

    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # ... maybe others ...
]
