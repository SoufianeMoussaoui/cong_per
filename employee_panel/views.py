from datetime import datetime

from django.db.models import Q
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from employee_panel.forms import LeaveForm, ProfileUpdateForm
from myadmin.models import Leave, LeaveType, Employee, Department, Role, Notification


@login_required
def change_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        new_password = request.POST['newpassword']
        confirm_password = request.POST['confirmpassword']

        user = request.user

        if user.check_password(password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your Password Has Been Updated.')
            else:
                messages.error(request, 'New Password and Confirm Password do not match.')
        else:
            messages.error(request, 'Your current password is wrong.')

    return render(request, 'employee/change_password.html')

@login_required
def leave_history(request):
    # 1) Get the Employee tied to this User
    employee = get_object_or_404(Employee, user=request.user)
    leaves = (
        Leave.objects
        .filter(employee=employee)
        .select_related('leave_type')
        .order_by('-submission_date')
    )

    return render(request, 'employee/leave_history.html', {
        'leave_history': leaves
    })



@login_required
def apply_leave(request):
    
    error = ''
    msg = ''

    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    notifications_list = list(notifications)
    notifications.delete()
    
    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            # 1) Get the currently logged-in user and corresponding employee
            user = request.user
            employee = get_object_or_404(Employee, user=user)

            # 2) Extract form data
            leave_type = form.cleaned_data['leavetype']
            start_date = form.cleaned_data['fromdate']
            end_date   = form.cleaned_data['todate']
            comment    = form.cleaned_data['description']

            # 3) Validate date range
            if (end_date - start_date).days < 0:
                error = "End Date should be after Start Date."
            else:
                # 4) Create the leave request
                Leave.objects.create(
                    employee    = employee,
                    leave_type  = leave_type,
                    start_date  = start_date,
                    end_date    = end_date,
                    comment     = comment,
                    status      = 'PENDING',  # Use string value
                    is_read     = False,
                )
                msg = "Your leave application has been submitted."

        else:
            error = "Please correct the form errors."
    else:
        form = LeaveForm()

    return render(request, 'employee/apply_leave.html', {
        'form': form,
        'error': error,
        'msg': msg,
          'notifications': notifications_list,
        'unread_count': unread_count
    })

    
@login_required()
def logout(request):
    # Clear session data
    request.session.flush()
    return redirect('accounts:employee_login')  # Redirect to the 'index' URL name or any other URL

    
@login_required()
def update_profile(request):
    employee = get_object_or_404(Employee, user=request.user)

    form = ProfileUpdateForm(instance=employee)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_panel:apply_leave')

    return render(request, 'employee/update_profile.html', {'form': form, 'employee': employee})