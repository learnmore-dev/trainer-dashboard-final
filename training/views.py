from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import Batch, WorkSession
from datetime import timedelta

# -----------------------
# User role checks
# -----------------------
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_trainer(user):
    return user.is_authenticated and user.role == 'trainer'

# -----------------------
# Admin dashboard
# -----------------------
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    trainers_data = []
    one_week_ago = timezone.now() - timedelta(days=7)

    # Get all trainers assigned to batches
    all_trainers_ids = Batch.objects.values_list('trainer', flat=True).distinct()
    for t_id in all_trainers_ids:
        try:
            t = request.user._meta.model.objects.get(id=t_id)
        except:
            continue

        sessions = t.work_sessions.all()  # all sessions
        total_hours = sum(ws.hours_spent for ws in sessions)
        batches = t.batches.all()
        trainers_data.append({'trainer': t, 'hours_week': total_hours, 'batches': batches})

    return render(request, 'training/admin_dashboard.html', {'trainers': trainers_data})

# -----------------------
# Trainer dashboard
# -----------------------
@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    t = request.user
    one_week_ago = timezone.now() - timedelta(days=7)
    sessions = t.work_sessions.filter(start_time__gte=one_week_ago)
    total_hours = sum(ws.hours_spent for ws in sessions)
    batches = t.batches.all()
    return render(request, 'training/trainer_dashboard.html', {
        'batches': batches,
        'hours_week': total_hours
    })

# -----------------------
# Batch list
# -----------------------
@login_required
def batch_list(request):
    if request.user.role == 'admin':
        batches = Batch.objects.all()
    else:
        batches = request.user.batches.all()
    return render(request, 'training/batch_list.html', {'batches': batches})

# -----------------------
# Batch detail
# -----------------------
@login_required
def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    sessions = batch.sessions.all()
    total_hours = sum(ws.hours_spent for ws in sessions)
    return render(request, 'training/batch_detail.html', {
        'batch': batch,
        'sessions': sessions,
        'total_hours': total_hours
    })

# -----------------------
# Trainer logs work session
# -----------------------
@login_required
@user_passes_test(is_trainer)
def session_create(request):
    batches = request.user.batches.all()  # only assigned batches

    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        start_str = request.POST.get('start_time')
        end_str = request.POST.get('end_time')
        description = request.POST.get('description')

        batch = get_object_or_404(Batch, id=batch_id)

        # ✅ Parse datetime and make timezone aware
        start_dt = parse_datetime(start_str)
        end_dt = parse_datetime(end_str)
        start_dt = timezone.make_aware(start_dt)
        end_dt = timezone.make_aware(end_dt)

        # Save WorkSession
        WorkSession.objects.create(
            trainer=request.user,
            batch=batch,
            start_time=start_dt,
            end_time=end_dt,
            description=description
        )

        return redirect('trainer_dashboard')

    return render(request, 'training/session_form.html', {'batches': batches})
