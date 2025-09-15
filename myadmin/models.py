import datetime

from django.contrib.auth.models import User,AbstractUser
from django.db import models
from datetime import date

"""
STATUS_CHOICES = (
    (0, 'Pending'),
    (1, 'Approved'),
    (2, 'Declined'),
)
"""

STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('DECLINED', 'Declined'),
)

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)
EMP_CHOICES = (
        ( 'Active', 'Active'),
        ( 'Inactive', 'Inactive'),
        )
UN_CHOICES = (
    ('Union', 'Union'),
    ('Non-Union', 'Non-Union'),
    ('Others', 'Others')
)


class Role(models.TextChoices):
    EMPLOYE = 'EMPLOYE', 'Employé'
    MANAGER = 'MANAGER', 'Manager'

class ReportType(models.TextChoices):
    PDF = 'PDF', 'PDF'
    CSV = 'CSV', 'CSV'

# -- Extend default User to include role --
class Custome_user(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYE)
    # inherits username, email, password, etc.

    def __str__(self):
        return self.get_full_name() or self.username


class Admin(models.Model):
    user = models.OneToOneField(Custome_user, on_delete=models.CASCADE, default=None)
    firstName = models.CharField(max_length=100, default="None")
    lastName = models.CharField(max_length=100, default="None")
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, default="80100")
    city = models.CharField(max_length=100, default="Mombasa")
    country = models.CharField(max_length=100,default="None")
    mobileno = models.CharField(max_length=20,default="0", blank=False, null=False)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)
    CreationDate = models.DateField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # Delete the associated user
        self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.username


class Department(models.Model):

    department_name = models.CharField(max_length=255)
    department_shortname = models.CharField(max_length=50)
    department_code = models.CharField(max_length=10, unique=True)
    CreationDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.department_name


class Employee(models.Model):

    user = models.OneToOneField(Custome_user, on_delete=models.CASCADE, default=None)
    empcode = models.CharField(max_length=10, primary_key=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)

    employee_type = models.CharField(
        max_length=10,
        choices=UN_CHOICES,
        default='Non-Union'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Male'
    )
    dob = models.DateField(auto_now_add=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, default="80100")
    city = models.CharField(max_length=100, default="Mombasa")
    country = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=20, blank=False, null=False)
    status = models.CharField(
        max_length=10,
        choices=EMP_CHOICES,
        default='Active'
    )
    CreationDate = models.DateField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # Delete the associated user
        self.user.delete()
        super().delete(*args, **kwargs)
    def __str__(self):
        return f"{self.empcode} - {self.firstName} {self.lastName}"


class LeaveType(models.Model):
    leavetype = models.CharField(max_length=255)
    Description = models.TextField()

    PostingDate = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.leavetype


class Notification(models.Model):
    user = models.ForeignKey(Custome_user, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Leave(models.Model):  
    employee = models.ForeignKey(Employee, related_name='leave_requests', on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submission_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Leave({self.employee.emp_code}: {self.start_date} to {self.end_date})"


class LeaveHistory(models.Model):
    leave_request = models.ForeignKey(Leave, related_name='history', on_delete=models.CASCADE)
    actor = models.ForeignKey(Custome_user, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"


class Report(models.Model):
    generated_by = models.ForeignKey(Custome_user, limit_choices_to={'role': 'MANAGER'}, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=ReportType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')

    def __str__(self):
        return f"Report {self.id} ({self.type})"
