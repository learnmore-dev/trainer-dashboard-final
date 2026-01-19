from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
#<<<<<<< HEAD
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Batch, WorkSession, Attendance, TrainerAttendance
import json
from datetime import datetime, timedelta






# training/views.py

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect



    
#=======
from .models import Batch, WorkSession, Attendance
import json
from datetime import datetime, timedelta

#>>>>>>> origin/main
# ✅ TIMEZONE FUNCTIONS
def get_indian_time():
    """Get current time in Indian timezone"""
    from pytz import timezone as tz
    try:
        indian_tz = tz('Asia/Kolkata')
        return datetime.now(indian_tz)
    except:
        return timezone.now()

def convert_to_indian_time(utc_time):
    """Convert UTC time to Indian time"""
    from pytz import timezone as tz
    if utc_time:
        try:
            indian_tz = tz('Asia/Kolkata')
            return utc_time.astimezone(indian_tz)
        except:
            return utc_time
    return None

def convert_string_to_utc(date_time_str):
    """
    Convert Indian time string (YYYY-MM-DD HH:MM:SS) to UTC datetime
    """
    try:
        # Parse the string
        local_dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        
        # Assume it's in Indian timezone
        from pytz import timezone as tz
        indian_tz = tz('Asia/Kolkata')
        utc_tz = tz('UTC')
        
        # Localize to Indian time and convert to UTC
        localized_dt = indian_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(utc_tz)
        return utc_dt
    except Exception as e:
        print(f"Time conversion error: {e}")
        return timezone.now()

# ✅ GET ACTIVE LOGIN FOR TODAY
def check_today_login(user):
    """Check if user has an active login for today (Indian time)"""
    today = timezone.now().date()
    
    # Get all today's attendances
    today_attendances = Attendance.objects.filter(
        user=user,
        login_time__date=today
    ).order_by('-login_time')
    
    # Find the one without logout
    for attendance in today_attendances:
        if attendance.logout_time is None:
            return attendance
    
    return None

# ==================== ATTENDANCE VIEWS ====================

@login_required
def attendance_home(request):
    # Check if user already logged in today
    today_login = check_today_login(request.user)
    
    if today_login:
        # Convert stored UTC to Indian time
        login_time_indian = convert_to_indian_time(today_login.login_time)
        login_time_str = login_time_indian.strftime('%H:%M:%S') if login_time_indian else None
    else:
        login_time_str = None
    
    context = {
        'already_logged_in': today_login is not None,
        'login_time': login_time_str,
        'login_address': today_login.login_address if today_login else None,
    }
    return render(request, 'training/attendance.html', context)

@login_required
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            address = data.get('address', '')
            dateTime = data.get('dateTime', '')
            
            # ✅ Check if user already logged in TODAY
            today_login = check_today_login(request.user)
            
            if today_login:
                login_time_indian = convert_to_indian_time(today_login.login_time)
                login_time_str = login_time_indian.strftime('%H:%M:%S') if login_time_indian else None
                
                return JsonResponse({
                    'status': 'error', 
                    'error': f'You are already logged in today at {login_time_str}'
                })
            
            # Convert Indian time string to UTC for storage
            if dateTime:
                utc_login_time = convert_string_to_utc(dateTime)
            else:
                utc_login_time = timezone.now()
                # Get current Indian time for response
                current_indian_time = get_indian_time()
                dateTime = current_indian_time.strftime('%H:%M:%S')
            
            # Create attendance record
            attendance = Attendance.objects.create(
                user=request.user,
                login_time=utc_login_time,
                login_lat=lat,
                login_lon=lon,
                login_address=address
            )
            
            # Return Indian time (extract time part from the received dateTime)
            try:
                time_part = dateTime.split(' ')[1] if ' ' in dateTime else dateTime
            except:
                time_part = attendance.login_time.strftime('%H:%M:%S')
            
            return JsonResponse({
                'status': 'success',
                'login_time': time_part,
                'address': address
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Invalid request'})

@login_required
def logout_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            address = data.get('address', '')
            dateTime = data.get('dateTime', '')
            
            # ✅ Get today's login (using the updated function)
            attendance = check_today_login(request.user)
            
            if attendance:
                print(f"Found attendance: {attendance.id}, Login: {attendance.login_time}")
                
                # Convert Indian time string to UTC for storage
                if dateTime:
                    utc_logout_time = convert_string_to_utc(dateTime)
                    print(f"Logout time from frontend: {dateTime}")
                    print(f"Converted to UTC: {utc_logout_time}")
                else:
                    utc_logout_time = timezone.now()
                    current_indian_time = get_indian_time()
                    dateTime = current_indian_time.strftime('%H:%M:%S')
                    print(f"Using current time: {utc_logout_time}")
                
                attendance.logout_time = utc_logout_time
                attendance.logout_lat = lat
                attendance.logout_lon = lon
                attendance.logout_address = address
                
                # ✅ Calculate total time CORRECTLY
                if attendance.login_time and attendance.logout_time:
                    print(f"Login time: {attendance.login_time}")
                    print(f"Logout time: {attendance.logout_time}")
                    
                    # Make sure both are timezone aware
                    from pytz import timezone as tz
                    utc_tz = tz('UTC')
                    
                    # Ensure both times are in UTC
                    if attendance.login_time.tzinfo is None:
                        attendance.login_time = utc_tz.localize(attendance.login_time)
                    if attendance.logout_time.tzinfo is None:
                        attendance.logout_time = utc_tz.localize(attendance.logout_time)
                    
                    attendance.total_time = attendance.logout_time - attendance.login_time
                    print(f"Total time calculated: {attendance.total_time}")
                
                attendance.save()
                
                # ✅ Format total time properly
                if attendance.total_time:
                    total_seconds = attendance.total_time.total_seconds()
                    total_hours = int(total_seconds // 3600)
                    total_minutes = int((total_seconds % 3600) // 60)
                    total_time_str = f"{total_hours}h {total_minutes}m"
                    print(f"Formatted total time: {total_time_str}")
                else:
                    total_time_str = "0h 0m"
                    print("No total time calculated")
                
                # Return Indian time (extract time part)
                try:
                    time_part = dateTime.split(' ')[1] if ' ' in dateTime else dateTime
                except:
                    time_part = attendance.logout_time.strftime('%H:%M:%S')
                
                return JsonResponse({
                    'status': 'success',
                    'logout_time': time_part,
                    'total_time': total_time_str
                })
            else:
                return JsonResponse({'status': 'error', 'error': 'No active login found for today'})
                
        except Exception as e:
            print(f"Error in logout_view: {str(e)}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Invalid request'})

# ==================== OTHER VIEWS ====================

@login_required
def trainer_dashboard(request):
    trainer = request.user
#<<<<<<< HEAD

    batches = Batch.objects.all() if request.user.is_superuser else Batch.objects.filter(trainer=trainer)

    recent_sessions = WorkSession.objects.filter(
        trainer=trainer
    ).order_by('-session_date')[:10]

    # ✅ Total worked hours
    total_worked_hours = sum(
        s.hours_taken for s in WorkSession.objects.filter(trainer=trainer)
    )

    # ✅ Weekly hours (date based)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    weekly_sessions = WorkSession.objects.filter(
        trainer=trainer,
        session_date__gte=start_of_week
    )

    weekly_hours = sum(s.hours_taken for s in weekly_sessions)

    attendance_status = check_today_login(trainer)

    context = {
        'batches': batches,
        'sessions': recent_sessions,
        'total_hours': total_worked_hours,
        'hours_week': weekly_hours,
#=======
    
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=trainer)
    
    sessions = WorkSession.objects.filter(trainer=trainer).order_by('-start_time')[:10]
    
    total_hours = 0
    all_sessions = WorkSession.objects.filter(trainer=trainer)
    for session in all_sessions:
        total_hours += session.hours_spent
    
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    sessions_this_week = WorkSession.objects.filter(
        trainer=trainer,
        start_time__gte=start_of_week
    )
    
    hours_week = 0
    for session in sessions_this_week:
        hours_week += session.hours_spent
    
    attendance_status = check_today_login(trainer)
    
    context = {
        'batches': batches,
        'sessions': sessions,
        'total_hours': round(total_hours, 2),
        'hours_week': round(hours_week, 2),
#>>>>>>> origin/main
        'attendance_status': attendance_status,
    }
    return render(request, 'training/trainer_dashboard.html', context)

#<<<<<<< HEAD
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

@login_required
def admin_dashboard(request):
    # ❌ Trainer ko yahan aane hi mat do
    if not request.user.is_superuser:
        return redirect('trainer_dashboard')

    User = get_user_model()

    # ✅ All batches (admin only)
    batches = Batch.objects.select_related('trainer').all()

    # ✅ Trainers = jo Batch me assigned hain
    trainers = User.objects.filter(
        batches__isnull=False
    ).distinct()

    # 🔍 Trainer filter
    trainer_filter = request.GET.get('trainer')
    if trainer_filter and trainer_filter != 'all':
        batches = batches.filter(trainer_id=trainer_filter)

    total_sessions = WorkSession.objects.count()

#=======
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('trainer_dashboard')
    
    #from django.contrib.auth.models import User
    from django.contrib.auth import get_user_model
    User = get_user_model()
    batches = Batch.objects.all()
    trainers = User.objects.filter(is_staff=True)
    total_sessions = WorkSession.objects.count()
    
#>>>>>>> origin/main
    context = {
        'batches': batches,
        'trainers': trainers,
        'total_sessions': total_sessions,
#<<<<<<< HEAD
        'selected_trainer': trainer_filter,
#=======
#>>>>>>> origin/main
    }
    return render(request, 'training/admin_dashboard.html', context)

@login_required
def batch_list(request):
#<<<<<<< HEAD
    batches = Batch.objects.all() if request.user.is_superuser else Batch.objects.filter(trainer=request.user)
#=======
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=request.user)
    
#>>>>>>> origin/main
    return render(request, 'training/batch_list.html', {'batches': batches})

@login_required
def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
#<<<<<<< HEAD

    if not request.user.is_superuser and batch.trainer != request.user:
        return redirect('batch_list')

    sessions = batch.sessions.all().order_by('-session_date')

    used_hours = sum(session.hours_taken for session in sessions)
    remaining_hours = batch.total_hours - used_hours

    context = {
        'batch': batch,
        'sessions': sessions,
        'used_hours': round(used_hours, 2),
        'remaining_hours': round(remaining_hours, 2),
        'delay_hours': abs(remaining_hours) if remaining_hours < 0 else 0,
    }
    return render(request, 'training/batch_detail.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Batch, WorkSession


@login_required
def session_create(request, batch_id=None):
    # Get trainer's batches
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=request.user)
    
    # If batch_id provided in URL, pre-select that batch
    selected_batch = None
    if batch_id:
        selected_batch = get_object_or_404(Batch, id=batch_id)
        
        # Permission check
        if not request.user.is_superuser and selected_batch.trainer != request.user:
            return render(request, 'training/session_form.html', {  # 👈 Yahan change kiya
                'error': 'Permission denied',
                'batches': batches
            })

    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        session_date = request.POST.get('session_date')
        hours_taken = request.POST.get('hours_taken')
        description = request.POST.get('description', '')

        try:
            batch = get_object_or_404(Batch, id=batch_id)
            
            # Permission check
            if not request.user.is_superuser and batch.trainer != request.user:
                return render(request, 'training/session_form.html', {  # 👈 Yahan change kiya
                    'error': 'Permission denied',
                    'batches': batches,
                    'selected_batch': selected_batch
                })

            # Convert data
            session_date = datetime.strptime(session_date, '%Y-%m-%d').date()
            hours_taken = float(hours_taken)

            # Save session
            WorkSession.objects.create(
                trainer=request.user,
                batch=batch,
                session_date=session_date,
                hours_taken=hours_taken,
                description=description
            )

            # Redirect to batch detail
            return redirect('training:batch_detail', batch_id=batch.id)

        except Exception as e:
            return render(request, 'training/session_form.html', {  # 👈 Yahan change kiya
                'error': str(e),
                'batches': batches,
                'selected_batch': selected_batch
            })

    # GET request
    return render(request, 'training/session_form.html', {  # 👈 Yahan change kiya
        'batches': batches,
        'selected_batch': selected_batch
    })    # GET request
    

# ==================== TRAINER ATTENDANCE VIEWS ====================

@login_required
def trainer_attendance_page(request):
    return render(request, "training/attendance_page.html")

@login_required
def trainer_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    action = request.POST.get("attendance")
    photo = request.FILES.get("photo")
    lat = request.POST.get("latitude")
    lng = request.POST.get("longitude")
    accuracy = request.POST.get("accuracy")

    if accuracy and float(accuracy) > 500:
        return JsonResponse(
        {"error": "Fake GPS detected"},
        status=403
    )

    if not action or not lat or not lng:
        return JsonResponse({"error": "Missing data"}, status=400)

    user = request.user
    today = timezone.localdate()

    attendance, created = TrainerAttendance.objects.get_or_create(
        trainer=user,
        date=today
    )

    # ---------- MARK IN ----------
    if action == "mark_in":

        if attendance.mark_in_time:
            return JsonResponse(
                {"error": "Already marked in today"},
                status=400
            )

        attendance.mark_in_time = timezone.now()
        attendance.photo_in = photo
        attendance.latitude = lat
        attendance.longitude = lng
        attendance.save()

        return JsonResponse({
            "status": "Marked In",
            "time": timezone.localtime(
                attendance.mark_in_time
            ).strftime("%H:%M:%S")
        })

    # ---------- MARK OUT ----------
    if action == "mark_out":

        if not attendance.mark_in_time:
            return JsonResponse(
                {"error": "Mark in first"},
                status=400
            )

        if attendance.mark_out_time:
            return JsonResponse(
                {"error": "Already marked out"},
                status=400
            )

        attendance.mark_out_time = timezone.now()
        attendance.photo_out = photo

        duration = attendance.mark_out_time - attendance.mark_in_time
        attendance.working_duration = duration
        attendance.save()

        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)

        return JsonResponse({
            "status": "Marked Out",
            "time": timezone.localtime(
                attendance.mark_out_time
            ).strftime("%H:%M:%S"),
            "working_hours": f"{hours}h {minutes}m"
        })

    return JsonResponse({"error": "Invalid action"}, status=400)

@login_required
def attendance_history(request):
    records = TrainerAttendance.objects.filter(
        trainer=request.user
    ).order_by("-date")

    data = []

    for r in records:
        data.append({
            "date": r.date.strftime("%d-%m-%Y"),
            "mark_in": (
                timezone.localtime(r.mark_in_time).strftime("%H:%M:%S")
                if r.mark_in_time else "--"
            ),
            "mark_out": (
                timezone.localtime(r.mark_out_time).strftime("%H:%M:%S")
                if r.mark_out_time else "--"
            ),
            "working_hours": (
                f"{int(r.working_duration.total_seconds()//3600)}h "
                f"{int((r.working_duration.total_seconds()%3600)//60)}m"
                if r.working_duration else "--"
            ),
            "status": "OUT" if r.mark_out_time else "IN",
            "photo_in": r.photo_in.url if r.photo_in else ""
        })

    return JsonResponse({"data": data})

@login_required
def monthly_attendance_report(request):
    if not request.user.is_superuser:
        return redirect('training:trainer_dashboard')
    
    now = timezone.now()
    month = int(request.GET.get("month", now.month))
    year = int(request.GET.get("year", now.year))
    trainer_id = request.GET.get("trainer", None)

    User = get_user_model()
    all_users = User.objects.filter(is_active=True)

    qs = TrainerAttendance.objects.filter(
        date__month=month,
        date__year=year
    ).select_related("trainer")

    if trainer_id:
        qs = qs.filter(trainer_id=trainer_id)

    report = {}

    for r in qs:
        user = r.trainer
        report.setdefault(user.id, {
            "name": user.get_full_name() or user.username,
            "records": []
        })

        # ✅ YE ADD KARO - Duration calculate karo
        duration = "--"
        if r.mark_in_time and r.mark_out_time:
            time_diff = r.mark_out_time - r.mark_in_time
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            duration = f"{hours}h {minutes}m"
        
        # ✅ Dictionary format me data pass karo
        report[user.id]["records"].append({
            'date': r.date,
            'status': 'OUT' if r.mark_out_time else 'IN',
            'mark_in_time': (
                timezone.localtime(r.mark_in_time).strftime("%I:%M %p")
                if r.mark_in_time else "--"
            ),
            'mark_out_time': (
                timezone.localtime(r.mark_out_time).strftime("%I:%M %p")
                if r.mark_out_time else "--"
            ),
            'duration': duration,  # ✅ YE IMPORTANT HAI
            'location_name': r.location_name or "--"
        })

    # ✅ Years list for dropdown
    current_year = now.year
    years = list(range(current_year - 2, current_year + 1))

    return render(request, "training/admin_monthly_report.html", {
        "report": report.values(),
        "month": month,
        "year": year,
        "trainers": all_users,
        "selected_trainer": trainer_id,  # ✅ Template me use hoga
        "years": years  # ✅ Template me years dropdown ke liye
    })

# views.py
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

@staff_member_required
def admin_batch_list(request):
    # Base queryset
    batches = Batch.objects.select_related('trainer')
    
    # Get filter parameters
    course_query = request.GET.get('course', '').strip()
    trainer_query = request.GET.get('trainer', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Apply course name filter
    if course_query:
        batches = batches.filter(name__icontains=course_query)
    
    # Apply trainer name filter (username OR full name)
    if trainer_query:
        batches = batches.filter(
            Q(trainer__username__icontains=trainer_query) |
            Q(trainer__first_name__icontains=trainer_query) |
            Q(trainer__last_name__icontains=trainer_query)
        )
    
    # Apply status filter
    if status_filter == 'ontime':
        # Filter batches where delay_hours <= 0
        batches = [b for b in batches if b.delay_hours == 0]
    elif status_filter == 'delay':
        # Filter batches where delay_hours > 0
        batches = [b for b in batches if b.delay_hours > 0]
    
    return render(request, 'training/admin_batch_list.html', {
        'batches': batches
    })


# views.py
from django.contrib.auth.decorators import login_required



@login_required
def trainer_batch_list(request):
    trainer = request.user

    # ❗ trainer sirf apne batches dekhe
    batches = Batch.objects.filter(trainer=trainer)

    context = {
        'batches': batches
    }

    return render(request, 'training/batch_list.html', context)




    # Add this to your views.py

@login_required
def get_trainer_batches(request):
    """API endpoint to get trainer's batches"""
#=======
    
    if not request.user.is_superuser and batch.trainer != request.user:
        return redirect('batch_list')
    
    sessions = batch.sessions.all().order_by('-start_time')
    
    total_hours = 0
    for session in sessions:
        total_hours += session.hours_spent
    
    context = {
        'batch': batch,
        'sessions': sessions,
        'total_hours': round(total_hours, 2),
    }
    return render(request, 'training/batch_detail.html', context)

@login_required
def session_create(request):
    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        description = request.POST.get('description', '')
        
        try:
            batch = Batch.objects.get(id=batch_id)
            
            if not request.user.is_superuser and batch.trainer != request.user:
                return render(request, 'training/session_create.html', {
                    'error': 'You do not have permission to add sessions to this batch',
                    'batches': Batch.objects.filter(trainer=request.user)
                })
            
            from datetime import datetime
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            
            session = WorkSession.objects.create(
                trainer=request.user,
                batch=batch,
                start_time=start_time,
                end_time=end_time,
                description=description
            )
            
            return redirect('batch_detail', batch_id=batch_id)
            
        except Exception as e:
            return render(request, 'training/session_form.html', {
                'error': str(e),
                'batches': Batch.objects.filter(trainer=request.user) if not request.user.is_superuser else Batch.objects.all()
            })
    
#>>>>>>> origin/main
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=request.user)
    
#<<<<<<< HEAD
    batch_list = [
        {
            'id': batch.id,
            'name': batch.name
        }
        for batch in batches
    ]
    
    return JsonResponse({'batches': batch_list})



def leave_create(request):
    return render(request, 'training/leave_create.html')


def session_form(request, batch_id=None):
    return session_create(request, batch_id)
#=======
    return render(request, 'training/session_form.html', {'batches': batches})
#>>>>>>> origin/main
