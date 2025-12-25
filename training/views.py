from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Batch, WorkSession, Attendance
import json
from datetime import datetime, timedelta

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
        'attendance_status': attendance_status,
    }
    return render(request, 'training/trainer_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('trainer_dashboard')
    
    from django.contrib.auth.models import User
    batches = Batch.objects.all()
    trainers = User.objects.filter(is_staff=True)
    total_sessions = WorkSession.objects.count()
    
    context = {
        'batches': batches,
        'trainers': trainers,
        'total_sessions': total_sessions,
    }
    return render(request, 'training/admin_dashboard.html', context)

@login_required
def batch_list(request):
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=request.user)
    
    return render(request, 'training/batch_list.html', {'batches': batches})

@login_required
def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    
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
    
    if request.user.is_superuser:
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(trainer=request.user)
    
    return render(request, 'training/session_form.html', {'batches': batches})