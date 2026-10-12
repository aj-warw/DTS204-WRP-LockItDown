# Lock IT Down

A working role-based security-awareness training application built with Python, Tkinter and SQLite for DTS204.

## Run

```bash
python main.py
```

No third-party packages are required. Python must include Tkinter.

## Login credentials

The login screen is blank. Credentials are shown only in this README.

All sample accounts use `Password1!`.

- Employee: `employee@company.com`
- Administrator: `admin@company.com`
- Manager Morgan Roberts: `manager.roberts@company.com`
- Manager Priya Shah: `manager.shah@company.com`
- Manager Daniel Hughes: `manager.hughes@company.com`

New users created by an administrator receive the temporary password `ChangeMe123!` unless another temporary password is entered during account creation.

## Included functionality

- Role-based login and navigation
- PBKDF2 password hashing with unique salts
- Blank login form
- Employee modules, quizzes, persistent scores, progress and achievements
- 80% quiz pass threshold
- Manager employee views, course assignments and reports
- Administrator user creation, editing and deletion
- Administrator manager assignment
- Administrator course assignment, reassignment and unassignment
- Administrator course creation
- SQLite persistence and cascading cleanup of deleted users
- Confirmation before user deletion
- Input and date validation

## Reset sample data

```bash
python reset_demo.py
```

This recreates the sample users, managers, courses and employee assignments.
