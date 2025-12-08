from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batch/<int:batch_id>/', views.batch_detail, name='batch_detail'),
    path('session/add/', views.session_create, name='session_create'),
]
