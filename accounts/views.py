from datetime import datetime

from django.db.models import Q
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User

from employee_panel.forms import LeaveForm, ProfileUpdateForm, PasswordRecoveryForm
from myadmin.models import Leave, LeaveType, Employee, Department


def employee_login(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # First, try to authenticate normally (username/password)
        user = authenticate(request, username=username, password=password)

        if not user:
            # If normal authentication fails, try to match empcode or email
            try:
                employee = Employee.objects.get(Q(empcode=username) | Q(user__email=username))
                user = authenticate(request, username=employee.user.username, password=password)
            except Employee.DoesNotExist:
                user = None

        if user:
            if not user.is_active:
                error = "Your user account is inactive. Contact admin."
            elif not hasattr(user, 'employee'):
                error = "This account is not associated with an employee."
            elif user.employee.status != 'Active':
                error = "Your employee status is not active. Contact admin."
            else:
                login(request, user)
                return redirect('employee_panel:apply_leave')
        else:
            error = "Invalid username/email or password."

    return render(request, 'accounts/employee_login.html', {'error': error})

def recover_password(request):
    if request.method == 'POST':
        form = PasswordRecoveryForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            empcode = form.cleaned_data['empcode']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if new_password == confirm_password:
                try:
                    employee = Employee.objects.get(email=email, empcode=empcode)
                    user = employee.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Your password has been recovered/changed. Enter new credentials to continue.")
                    return redirect('myadmin:employee_login')
                except Employee.DoesNotExist:
                    messages.error(request, "Sorry, invalid details.")
            else:
                messages.error(request, "New Password and Confirm Password do not match.")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = PasswordRecoveryForm()

    return render(request, 'employee/change_password.html', {'form': form})

