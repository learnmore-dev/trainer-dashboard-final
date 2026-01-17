from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # create user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            # authenticate user
            user = authenticate(username=username, password=raw_password)

            # login after signup
            if user is not None:
                login(request, user)

            return redirect('login')  # URL NAME
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def logout_user(request):
    logout(request)
    return JsonResponse({
        "status": "success",
        "redirect_url": "/login/"
    })
