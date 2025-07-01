# Transportation System by Django

A comprehensive **University Transportation Management System** built using Django. This system helps manage bus schedules, routes, and student access efficiently.

## Features

- **Super Admin Panel**
  - Manage bus routes and schedules
  - Track student login activity
  - Generate reports on transportation data

- **Supervisor Panel**
  - Assign buses to routes daily
  - Oversee transportation schedules

- **Student Portal**
  - View bus schedules, routes, and timings
  - Automatic login via student ID (session-based authentication)

## Technologies Used

- **Backend:** Django, Django REST Framework
- **Database:** MySQL
- **Frontend:** Django Templates (Integrated), External Frontend Collaboration
- **Authentication:** Session-based auto-login for students

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AbrarZaved/Transportation_System_by_Django.git
   cd Transportation_System_by_Django
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**
   - Ensure MySQL is installed and running
   - Update `settings.py` with your database credentials
   
5. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser (for Admin Access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the System**
   - Admin Panel: `http://127.0.0.1:8000/admin/`
   - Student Portal: `http://127.0.0.1:8000/`



## Contributions

We welcome contributions! Follow these steps:
1. Fork the repository
2. Create a new branch (`feature-branch`)
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is open-source and available under the [MIT License](LICENSE).

---

Made with ❤️ by Abrar Zaved & Team

