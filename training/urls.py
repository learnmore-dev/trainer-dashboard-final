from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    
    # Batch Management
    path('batches/', views.batch_list, name='batch_list'),
    path('batch/<int:batch_id>/', views.batch_detail, name='batch_detail'),
    
    # Session Management
    path('session/add/', views.session_create, name='session_create'),
    
    
    
    # Attendance System
    path('attendance/', views.attendance_home, name='attendance'),
    path('login/', views.login_view, name='login'),  # यह /training/login/ बनेगा
    path('logout/', views.logout_view, name='logout'),  # यह /training/logout/ बनेगा
]