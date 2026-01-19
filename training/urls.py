from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = "training"

urlpatterns = [
    # urls.py
    path('admin/batches/', views.admin_batch_list, name='admin_batch_list'),

    # ================= AUTH =================
    path('django-logout/', LogoutView.as_view(next_page='login'), name='django_logout'),

    # ================= DASHBOARDS =================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
   path(
        "trainer/dashboard/",
        views.trainer_dashboard,
        name="trainer_dashboard"
    ),
    # Add this to urlpatterns in urls.py
    path('api/trainer-batches/', views.get_trainer_batches, name='get_trainer_batches'),

    # ================= BATCH =================
    path('batches/', views.batch_list, name='batch_list'),
    path('batch/<int:batch_id>/', views.batch_detail, name='batch_detail'),

    # ================= SESSION =================
    path('session/add/<int:batch_id>/', views.session_form, name='session_create'),
    path('session/add/', views.session_form, name='session_create_standalone'),


    # ================= USER ATTENDANCE =================
    path('attendance/', views.attendance_home, name='attendance'),
    path('attendance/login/', views.login_view, name='attendance_login'),
    path('attendance/logout/', views.logout_view, name='attendance_logout'),

    # ================= TRAINER ATTENDANCE =================
    path('trainer-attendance/', views.trainer_attendance_page, name='trainer_attendance_page'),
    path('trainer-attendance/api/', views.trainer_attendance, name='trainer_attendance_api'),
    path('trainer-attendance/history/', views.attendance_history, name='trainer_attendance_history'),
    path('monthly-attendance-report/', views.monthly_attendance_report, name='monthly_attendance_report'),
    path('leave/create/', views.leave_create, name='leave_create'),

]