# 🛠 Leave Management — MyAdmin Module

This is the **Admin Dashboard** of your Leave Management System. It offers administrative control over employees, departments, leave types, and leave requests.

---

## 🚀 Features

- Admin login and authentication
- Dashboard overview (pending/approved/declined leaves, employees, departments)
- Manage employees (CRUD operations)
- Manage departments (add/update/view)
- Manage leave types
- Approve or reject leave requests

---

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SoufianeMoussaoui/Leave-Management.git
cd Leave-Management/myadmin
```

---

### 2. Create a Virtual Environment & Activate

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```bash
pip install -r ../requirements.txt
```

---

### 4. Set Up the Database

```bash
cd ..
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Create an Admin User

```bash
python manage.py createsuperuser
```

---

### 6. Run the Development Server

```bash
python manage.py runserver
```

Then open your browser and go to:

```
http://127.0.0.1:8000/
```

Login with your admin credentials to access the **MyAdmin Dashboard**.

---

## 🧭 How to Use the MyAdmin Interface

1. Sign in with your admin credentials.
2. Use the menu to manage:
   - Departments
   - Employees
   - Leave Types
   - Leave Requests (Approve / Reject)
3. Dashboard displays a live overview of pending, approved, and declined leaves.

---

## 🧰 Folder Structure (myadmin)

```
myadmin/
├── migrations/         # Django migration files
├── templates/          # HTML templates for admin views
├── static/             # CSS, JavaScript, images
├── admin_views.py      # Admin view logic (or views.py)
├── models.py           # Employee, Department, LeaveType, LeaveRequest models
├── forms.py            # Forms used in admin interface
└── urls.py             # URL routing for admin module
```

---

## ✅ Tips & Notes

- Customize `settings.py` if using a different database or static files path.
- If deploying, switch `DEBUG = False` and configure `ALLOWED_HOSTS`.
- Ensure `.gitignore` excludes `venv/`, `.pyc` files, and local database files like `db.sqlite3`.

---

## 📞 Support

For help, feedback or contributions, feel free to open an issue or submit a pull request in the repository.

---

**Enjoy managing leaves more efficiently with the Admin interface!**
