import json
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime, parse_date

from myadmin.models import (
    Custome_user, Admin, Department, Employee,
    LeaveType, Leave, LeaveHistory, Notification,
    Report, Calendar, Role
)

class Command(BaseCommand):
    help = "Import old data.json into the new MySQL-backed models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture', '-f',
            help="Path to old SQLite fixture JSON file",
            required=True
        )

    def handle(self, *args, **opts):
        fixture_path = opts['fixture']
        with open(fixture_path, 'r') as fp:
            old = json.load(fp)

        # -- 1) Import users into Custome_user --------------------
        users_map = {}
        for rec in old:
            if rec['model'] == 'auth.user':
                pk = rec['pk']
                f = rec['fields']
                u, created = Custome_user.objects.get_or_create(
                    username=f['username'],
                    defaults={
                        'email':        f['email'],
                        'is_staff':     f.get('is_staff', False),
                        'is_active':    f.get('is_active', True),
                        'is_superuser': f.get('is_superuser', False),
                        'date_joined':  parse_datetime(f['date_joined']),
                        'role':         f.get('role', Role.EMPLOYE),
                    }
                )
                if created:
                    self.stdout.write(f"✔ Created user {u.username}")
                else:
                    self.stdout.write(f"– Skipped existing user {u.username}")
                users_map[pk] = u
        self.stdout.write(self.style.SUCCESS(f'Processed {len(users_map)} users.'))

        # -- 2) Admins ---------------------------------------------
        for rec in old:
            if rec['model'] == 'myadmin.admin':
                f = rec['fields']
                Admin.objects.update_or_create(
                    user=users_map.get(f['user']),
                    defaults={
                        'fullname': f['fullname'],
                        'email':    f['email'],
                        'username': f['username'],
                    }
                )
        self.stdout.write(self.style.SUCCESS('Admins imported.'))

        # -- 3) Departments ---------------------------------------
        dept_map = {}
        for rec in old:
            if rec['model'] == 'myadmin.department':
                f = rec['fields']
                d, _ = Department.objects.get_or_create(
                    department_code=f['department_code'],
                    defaults={
                        'department_name':      f['department_name'],
                        'department_shortname': f['department_shortname'],
                        'CreationDate': parse_date(f['CreationDate']),
                    }
                )
                dept_map[rec['pk']] = d
        self.stdout.write(self.style.SUCCESS(f'Imported {len(dept_map)} departments.'))

        # -- 4) Employees -----------------------------------------
        emp_map = {}
        for rec in old:
            if rec['model'] == 'myadmin.employee':
                f = rec['fields']
                emp, created = Employee.objects.get_or_create(
                    empcode=rec['pk'],
                    defaults={
                        'user':      users_map.get(f['user']),
                        'firstName': f['firstName'],
                        'lastName':  f['lastName'],
                        'email':     f['email'],
                        'password':  f['password'],
                        'department':dept_map.get(f['department']),
                        'address':   f.get('address',''),
                        'city':      f.get('city',''),
                        'country':   f.get('country',''),
                        'mobileno':  f.get('mobileno',''),
                        'status':    f.get('status','Active'),
                    }
                )
                emp_map[rec['pk']] = emp
        self.stdout.write(self.style.SUCCESS(f'Imported {len(emp_map)} employees.'))

        # -- 5) LeaveTypes ----------------------------------------
        lt_map = {}
        for rec in old:
            if rec['model'] == 'myadmin.leavetype':
                f = rec['fields']
                lt, _ = LeaveType.objects.get_or_create(
                    leavetype=f['leavetype'],
                    defaults={
                        'Description': f['Description'],
                        'PostingDate': parse_date(f['PostingDate']),
                    }
                )
                lt_map[rec['pk']] = lt
        self.stdout.write(self.style.SUCCESS(f'Imported {len(lt_map)} leave types.'))

        # -- 6) Leaves --------------------------------------------
        leave_map = {}
        skipped = 0
        for rec in old:
            if rec['model'] == 'myadmin.leave':
                f = rec['fields']
                emp = emp_map.get(f['employee'])
                lt = lt_map.get(f.get('leave_type')) or lt_map.get(f.get('leavetype'))
                if not emp or not lt:
                    skipped += 1
                    self.stdout.write(f"– Skipped leave {rec['pk']} (missing employee or type)")
                    continue
                L, created = Leave.objects.get_or_create(
                    employee=emp,
                    leave_type=lt,
                    start_date=parse_date(f.get('fromdate') or f.get('start_date')),
                    end_date=parse_date(f.get('todate') or f.get('end_date')),
                    defaults={
                        'status':         f.get('status', 0),
                        'comment':        f.get('description',''),
                        'is_read':        bool(f.get('isread',0)),
                        'submission_date': parse_datetime(f.get('posting_date','') + 'T00:00:00Z'),
                    }
                )
                leave_map[rec['pk']] = L
        self.stdout.write(self.style.SUCCESS(f'Imported {len(leave_map)} leaves (skipped {skipped}).'))

        # -- 7) (Optional) Further models ------------------------
        # Similar pattern — check maps, skip when missing, use get_or_create.

        self.stdout.write(self.style.SUCCESS('🎉 Data migration complete!'))
