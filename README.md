LOCK IT DOWN 

PROJECT STRUCTURE 

- main.py = main app entry point 
- models.py = classes and application models
- db.py = SQLite database and CRUD
- auth.py = authentication functionality

- ui/ REFER TO UI DESIGN DOCS
    - login.py = login interface
    - employee.py = employee dashboard
    - manager.py = manager dashboard
    - admin.py = adminstrator dashboard
    - training.py = training and quiz interface

- assets/ = images and resources


RUNNING THE APP 
run from "main.py" which should take you to a temp tkinter window for now. 
running the app for the first time will create a new database for you. You might need to create your own data if testing anything


DEV WORKFLOW
- create a new feature branch from sprint 3 for your jira task
- develop whatever you doing on that branch
- commit and push changes to that branch
- open a pull request to pull your feature branch to sprint 3 branch.  Any other team member can approve pull requests
- only when sprint is complete, merge sprint with main

dont push changes directly to sprint or main