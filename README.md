# Task Manager API
A powerful Django-based REST API for managing projects and tasks with user authentication, role-based permissions, and comprehensive API documentation.
## 📋 Overview
Task Manager is a collaborative project management system that allows users to:
- Create and manage projects
- Assign team members to projects
- Create, assign, and track tasks with different statuses and priorities
- Manage task assignments and due dates
- Control access with role-based permissions

## 🛠️ Technologies
- **Backend Framework**: Django & Django REST Framework
- **Authentication**: Token-based authentication
- **Documentation**: OpenAPI/Swagger (drf-spectacular)
- **Database**: PostgreSQL (recommended) / SQLite (development)

## 🏗️ Project Structure
The project consists of three main Django apps:
1. **users**: User management and authentication
2. **project**: Project creation, member management, and permissions
3. **task**: Task creation, assignment, and status tracking

## 🔍 Key Features
### Users
- User registration and authentication
- Token-based API access
- User profile management

### Projects
- Create and manage projects
- Add/remove team members
- Role-based access control (owner vs. members)

### Tasks
- Create, update, and delete tasks
- Set task status (To Do, In Progress, Done)
- Assign priorities (Low, Medium, High)
- Set due dates
- Assign tasks to specific users
- Filter tasks by project, status, and priority

## 🚀 Getting Started
### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation
1. Clone the repository:
``` bash
git clone https://github.com/milad-sol/task-manager.git
cd task-manager
```
1. Create and activate a virtual environment:
``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
1. Install dependencies:
``` bash
pip install -r requirements.txt
```
1. Run migrations:
``` bash
python manage.py migrate
```
1. Create a superuser:
``` bash
python manage.py createsuperuser
```
1. Start the development server:
``` bash
python manage.py runserver
```
The API will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
## 📚 API Documentation
API documentation is available through Swagger UI. After starting the server, visit:
``` 
http://127.0.0.1:8000/api/schema/swagger-ui/
```
## 🔐 Authentication
The API uses token-based authentication. To get your token:
1. Register a new user or login with an existing one
2. Make a POST request to `/api/users/token/` with your username and password
3. Use the returned token in the `Authorization` header as `Token <your_token>`

## 🔄 API Endpoints
### Users
- `POST /api/users/register/` - Register a new user
- `POST /api/users/token/` - Get authentication token
- `GET /api/users/me/` - Get current user details

### Projects
- `GET /api/projects/` - List all accessible projects
- `POST /api/projects/` - Create a new project
- `GET /api/projects/{id}/` - Retrieve project details
- `PUT/PATCH /api/projects/{id}/` - Update a project (owner only)
- `DELETE /api/projects/{id}/` - Delete a project (owner only)
- `PATCH /api/projects/{id}/members/` - Add/remove project members

### Tasks
- `GET /api/tasks/` - List all accessible tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}/` - Retrieve task details
- `PUT/PATCH /api/tasks/{id}/` - Update a task
- `DELETE /api/tasks/{id}/` - Delete a task

## 🧪 Running Tests
The project includes comprehensive tests. To run them:
``` bash
python manage.py test
```
To run tests for a specific app:
``` bash
python manage.py test task
```
## 👨‍💻 Development
### Setting Up Development Environment
For local development, it's recommended to use Postgresql:
``` python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'task',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
For production, configure PostgreSQL or another production-ready database.
### Running with Debug
For development, ensure `DEBUG = True` is set in settings.py.
## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
## 👥 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

