import email

from django.contrib.auth.hashers import make_password
import hashlib
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification
from django.contrib import messages
from .forms import EmployeeForm, LeaveTypeForm, EmployeeUpdateForm, AdminForm, LeaveActionForm, DepartmentForm
from .models import Admin, Department, Employee, LeaveType, Leave, Custome_user, Notification, Report
from xhtml2pdf import pisa
from django.shortcuts               import get_object_or_404
from django.http                    import HttpResponse
from django.template.loader         import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import HttpResponseBadRequest
from datetime import datetime
from django.views.decorators.http import require_POST




def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('myadmin:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'admin/admin_login.html')



@login_required
def user_logout(request):
    logout(request)
    return redirect('myadmin:admin_login')


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    leaves = Leave.objects.order_by('-id')[:7]
    pending_leave_count = Leave.objects.filter(status='PENDDING').count()
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    leave_type_count = LeaveType.objects.count()
    employee_count = Employee.objects.count()
    leave_dec = Leave.objects.filter(status='DECLINED').count()
    leave_appr = Leave.objects.filter(status='APPROVED').count()
    departements = Department.objects.all()
    departement_count = Department.objects.all().count()

    context = {
        'page': 'dashboard',
        'leaves': leaves,
        'notifications': notifications,
        'pending_leave_count':pending_leave_count,
        'leave_type_count':leave_type_count,
        'employee_count':employee_count,
        'leave_dec':leave_dec,
        'leave_appr':leave_appr,
        'departement_count':departement_count,
        'pending_leave_count' : pending_leave_count,
        'departements' : departements
    }

    return render(request, 'admin/dashboard.html', context)

@login_required
def add_admin(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        admin = Admin.objects.create(
            user=user,
            fullname=fullname,
            email=email,
            username=username
        )

        messages.success(request, 'New admin has been added successfully')
        return redirect('myadmin:manage_admin')  # Redirect to the same page to show the message

    return render(request, 'admin/add_admin.html')

@login_required
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            # Optional cleanup logic
            Department.objects.filter(
                Q(department_name__isnull=True) | Q(department_shortname__isnull=True)
            ).delete()

            form.save()
            messages.success(request, 'New department has been added successfully')
            return redirect('myadmin:department')
    else:
        form = DepartmentForm()

    return render(request, 'admin/add_department.html', {'form': form})

    

def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            # Create a new User and Employee instance
            user = Custome_user.objects.create_user(
                username=form.cleaned_data['empcode'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['firstName'],
                last_name=form.cleaned_data['lastName'],

            )

            employee = form.save(commit=False)  # Create an Employee instance but don't save it yet
            employee.user = user  # Associate the user with the employee
            employee.save()  # Now save the employee to the database

            # Redirect to a success page or handle success as needed
            messages.success(request, 'New employee has been added successfully')
            return redirect('myadmin:employees')

    else:
        form = EmployeeForm()

    return render(request, 'admin/add_employee.html', {'form': form})

@login_required
def toggle_status(request):

    if request.method == 'POST':
        empcode = request.POST.get('empcode')
        status = request.POST.get('status')
    else:
        # compatibility GET
        empcode = request.GET.get('id') or request.GET.get('inid')
        status = "Active" if request.GET.get('id') else "Inactive" if request.GET.get('inid') else None

    if not empcode or not status:
        messages.error(request, "Missing parameters.")
        return redirect('myadmin:employees')

    try:
        emp = Employee.objects.get(empcode=empcode)
        emp.status = status
        emp.save()
        messages.success(request, f"Employee {emp.empcode} set to {status}.")
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
    return redirect('myadmin:employees')


@login_required
def delete_employee(request):

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method")

    emp_identifier = request.POST.get('empcode') or request.POST.get('del')
    if not emp_identifier:
        messages.error(request, "No employee specified.")
        return redirect('myadmin:employees')

    try:
        with transaction.atomic():
            emp = Employee.objects.get(empcode=emp_identifier)
            emp.delete()
            messages.success(request, f"Employee {emp_identifier} deleted.")
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")

    return redirect('myadmin:employees')


@login_required
def add_leave_type(request):
    if request.method == 'POST':
        leavetype = request.POST['leavetype']
        description = request.POST['Description']

        leavetype = LeaveType(leavetype=leavetype, Description=description)
        leavetype.save()

        # Redirect to a success page or handle success as needed
        messages.success(request, 'New leave has been added successfully')
        return redirect('myadmin:leavetype_list')

    else:
        form = LeaveTypeForm()  # Render an empty form

    return render(request, 'admin/add_leave_type.html', {'form': form})




@login_required
def approved_leaves(request):

    error = None
    msg = None
    approved_leaves = Leave.objects.filter(status='APPROVED')

    if request.method == 'POST':
        query = Leave.objects.all()

        results = query.values()

        leavtypcount = query.count()
    leaves = Leave.objects.filter(status='APPROVED').order_by('-id')

    context = {
        'error': error,
        'msg': msg,
        'approved_leaves': approved_leaves,
    }
    return render(request, 'admin/approved_leaves.html', context)

@login_required
def update_employee(request, empcode):

  employee = get_object_or_404(Employee, empcode=empcode)

  form = EmployeeUpdateForm(instance=employee)

  if request.method == 'POST':
    form = EmployeeUpdateForm(request.POST, instance=employee)
    if form.is_valid():
      form.save()
      return redirect('myadmin:employees')

  return render(request, 'admin/update.html', {'form': form, 'employee': employee})

@login_required
def view_employee(request, empcode):

  employee = get_object_or_404(Employee, empcode=empcode)

  form = EmployeeForm(instance=employee)

  return render(request, 'admin/view.html', {'form': form, 'employee': employee})

@login_required
def employee_leave_details(request, leave_id):
    
    error = ''
    msg = ''
    leave = Leave.objects.get(pk=leave_id)

    if request.method == "POST":
        form = LeaveActionForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            action = form.cleaned_data['action']
            leave.admin_remark = description
            leave.status = action  # Renamed from status to action
            leave.save()
            msg = "Leave updated Successfully"
            Notification.objects.create(
                user=leave.employee.user,
                message=f"Your leave request from {leave.start_date} to {leave.end_date} has been {leave.status}."
            )
        else:
            error = "Please correct the form errors."
    else:
        form = LeaveActionForm(initial={'action': leave.status})  # Renamed from status to action

    context = {
        'form': form,
        'leave': leave,
        'error': error,
        'msg': msg,
    }

    return render(request, 'admin/leave_details.html', context)


@login_required
def declined_leaves(request):
    declined_leaves = Leave.objects.filter(status='DECLINED').order_by('-id')
    context = {
        'declined_leaves': declined_leaves
    }
    return render(request, 'admin/declined_leaves.html', context)


@login_required
def department(request):
    if request.method == "GET" and 'del' in request.GET:
        department_id = request.GET['del']
        try:
            department = Department.objects.get(id=department_id)
            department.delete()
            messages.success(request, "Department deleted successfully")
        except Department.DoesNotExist:
            messages.error(request, "Department not found")

    departments = Department.objects.all()
    return render(request, 'admin/department_list.html', {'departments': departments})


@login_required
def update_department(request, deptid):
    global department
    if not request.session.get('alogin'):
        return redirect('myadmin:admin_login')  # Redirect to the login page if not logged in

    error = None
    msg = None

    if request.method == 'POST':
        deptname = request.POST.get('departmentname')
        deptshortname = request.POST.get('departmentshortname')
        deptcode = request.POST.get('deptcode')

        try:
            department = Department.objects.get(id=deptid)
            department.DepartmentName = deptname
            department.DepartmentShortName = deptshortname
            department.DepartmentCode = deptcode
            department.save()
            msg = "Department updated successfully"
        except Department.DoesNotExist:
            error = "Department not found or already deleted"

    try:
        department = Department.objects.get(id=deptid)
    except Department.DoesNotExist:
        error = "Department not found"

    context = {
        'error': error,
        'msg': msg,
        'department': department,
    }

    return render(request, 'admin/update_department.html', context)
@login_required
def update_leave_type(request, lid):
    global msg
    if not request.user.is_authenticated:
        return redirect('admin_login')  # Redirect to the appropriate URL

    if request.method == 'POST':

        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            leave_type = LeaveType.objects.get(id=lid)
            leave_type.leavetype = form.cleaned_data['leavetype']
            leave_type.Description = form.cleaned_data['Description']
            leave_type.save()

            msg = "Leave type updated successfully"

    else:
        leave_type = LeaveType.objects.get(pk=lid)
        form = LeaveTypeForm(initial={
            'leavetype': leave_type.leavetype,
            'Description': leave_type.Description
        })

    context = {
        'form': form,
        'msg': msg if 'msg' in locals() else None
    }

    return render(request, 'admin/update_leave_type.html', context)


@login_required
def employees(request):

    q = request.GET.get('q', '').strip()
    qs = Employee.objects.select_related('department').all()

    if q:
        # adjust search fields as needed
        qs = qs.filter(
            # empcode is PK (string)
            Q(empcode__icontains=q) |
            Q(firstName__icontains=q) |
            Q(lastName__icontains=q) |
            Q(department__department_name__icontains=q) |
            Q(department__department_shortname__icontains=q)
        )

    # ordering and pagination
    qs = qs.order_by('empcode')
    page = request.GET.get('page', 1)
    per_page = 12
    paginator = Paginator(qs, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Legacy quick GET toggles (not recommended — prefer POST). Keeps compatibility.
    if request.method == 'GET':
        if 'id' in request.GET or 'inid' in request.GET:
            emp_identifier = request.GET.get('id') or request.GET.get('inid')
            emp = get_object_or_404(Employee, empcode=emp_identifier)
            emp.status = "Active" if 'id' in request.GET else "Inactive"
            emp.save()
            messages.success(request, f"Employee {emp.empcode} set to {emp.status}.")
            return redirect('myadmin:employees')

    context = {
        'employees': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'request': request,
    }
    return render(request, 'admin/employees.html', context)



@login_required
def leaves_history(request):     

    leave_history = Leave.objects.select_related('employee').order_by('-id') 
    return render(request, 'admin/leaves_history.html', {'leave_history': leave_history})

@login_required
def leave_type_section(request):
    leave_types = LeaveType.objects.all()  # Query all leave types
    return render(request, 'admin/leave_type_section.html', {'leave_types': leave_types})

@login_required
def leave_deleter(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')  # Redirect to the login page if not authenticated

    if request.method == 'GET' and 'del' in request.GET:
        leave_type_id = request.GET['del']
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id)
            leave_type.delete()
            messages.success(request, 'Leave type record deleted')
        except LeaveType.DoesNotExist:
            messages.error(request, 'Leave type record not found')

    leave_types = LeaveType.objects.all()

    return render(request, 'admin/leave_type_section.html', {'leave_types': leave_types})


@login_required
def manage_admin(request):
    if request.method == "GET" and 'del' in request.GET:
        id = request.GET.get('del')
        try:
            admin = Admin.objects.get(id=id)

            admin.delete()
            messages.success(request, "The selected admin account has been deleted")
        except Admin.DoesNotExist:
            messages.error(request, "Admin account not found")

    admins = Admin.objects.all()
    return render(request, 'admin/manage_admin.html', {'admins': admins})
@login_required
def pending_leaves(request):
    leaves = (
        Leave.objects
            .filter(status='PENDING')
             .select_related('employee', 'leave_type')
             .order_by('-id')
    )

    return render(request, 'admin/pending_history.html', {
        'leaves':     leaves
    })

@login_required
def employee_update(request, empcode):

  employee = get_object_or_404(Employee, empcode=empcode)

  form = EmployeeUpdateForm(instance=employee)

  if request.method == 'POST':
    form = EmployeeUpdateForm(request.POST, instance=employee)
    if form.is_valid():
      form.save()
      return redirect('myadmin:employees')

  return render(request, 'admin/update.html', {'form': form, 'employee': employee})



def count_employees(request):
    employee_count = Employee.objects.count()

    return render(request, 'admin/emp-counter.html', {'employee_count': employee_count})


def count_leave_types(request):
    leave_type_count = LeaveType.objects.count()

    return render(request, 'leavetype-counter.html', {'leave_type_count': leave_type_count})

def is_manager(user):
    return user.is_staff or user.groups.filter(name="Managers").exists()




@login_required
@user_passes_test(is_manager)
def monthly_dept_pdf(request):
    dept_short = request.GET.get('dept')   
    month_str  = request.GET.get('month')  
    if not (dept_short and month_str):
        return HttpResponse("Paramètres manquants", status=400)

    try:
        sep = '/' if '/' in month_str else '-'
        year, month = map(int, month_str.split(sep))
    except ValueError:
        return HttpResponse("Format de mois invalide (attendu YYYY/MM)", status=400)

    leaves = (
        Leave.objects
             .filter(
                 employee__department__department_shortname=dept_short,
                 submission_date__year=year,
                 submission_date__month=month,
             )
             .order_by('submission_date')
    )

    month_label = datetime(year, month, 1).strftime('%m/%Y')
    filename    = f'Congés_{dept_short}_{month_label}.pdf'

    template = get_template('admin/monthly_dept_report.html')
    html     = template.render({
        'department_short': dept_short,
        'leaves':           leaves,
        'month_label':      month_label,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f'Erreur générant le PDF: {pisa_status.err}', status=500)
    return response

@login_required
def update_department(request, deptid):
    department = get_object_or_404(Department, id=deptid)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('myadmin:department')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'admin/update_department.html', {
        'form': form,
        'department': department
    })


@login_required
@require_POST
def delete_department(request):

    deptid = request.POST.get('deptid')
    if not deptid:
        messages.error(request, "No department specified to delete.")
        return redirect('myadmin:department')

    department = get_object_or_404(Department, id=deptid)

    
    if department.employee_set.exists(): 
        messages.error(request, "Cannot delete department with employees.", extra_tags='danger')
        return redirect('myadmin:department')

    department.delete()
    messages.success(request, f"Department '{department.department_name}' deleted.")
    return redirect('myadmin:department')
