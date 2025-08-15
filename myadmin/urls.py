from django.urls import path
from . import views
from .views import update_leave_type, employees

app_name = 'myadmin'

urlpatterns = [
    path('add_admin/', views.add_admin, name='add_admin'),
    path('add_department/', views.add_department, name='add_department'),
    path('add_leave_type/', views.add_leave_type, name='add_leave_type'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('approved-leaves/', views.approved_leaves, name='approved_leaves'),
    path('update_employee/<str:empcode>/', views.update_employee, name='update_employee'),
    path('view_employee/<str:empcode>/', views.view_employee, name='view_employee'),
    path('employee-leave-details/<int:leave_id>/', views.employee_leave_details, name='employee_leave_details'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('declined-leaves/', views.declined_leaves, name='declined_leaves'),
    path('update_department/<int:deptid>/', views.update_department, name='update_department'),
    path('update_leave_type/<int:lid>/', views.update_leave_type, name='update_leave_type'),
    path('employees/', views.employees, name='employees'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('leaves_history/', views.leaves_history, name='leave_history'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('manage-admin/', views.manage_admin, name='manage_admin'),
    path('update_employee/',views.employee_update, name='update_employee'),
    path('department', views.department, name='department'),
    path('update_department/<int:deptid>/', views.update_department, name='update_department'),
    path('delete_department/', views.delete_department, name='delete_department'),
    path('pending_leaves/', views.pending_leaves, name='pending_leaves'),
    path('count_employees', views.count_employees, name='count_employees'),
    path('count_leave_types', views.count_leave_types, name='count_leave_types'),
    path('leave_type_section/', views.leave_type_section, name='leave_type_section'),
    path('leave_deleter/', views.leave_deleter, name='leave_deleter'),
    path('export/monthly-department-pdf/',views.monthly_dept_pdf,name='monthly_dept_pdf'),
    path('employees/delete/', views.delete_employee, name='delete_employee'),
    path('employees/toggle-status/', views.toggle_status, name='toggle_status'),


    # Add other URL patterns for your views
]
