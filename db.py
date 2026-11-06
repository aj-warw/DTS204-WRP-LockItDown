import sqlite3
from models import User, Course, Lesson, Enrolment, LessonProgress
from datetime import date

# opens a new connection and enforce foreign keys

def get_connection(): 
    connection = sqlite3.connect("lockitdown.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise_database(): # create database if it doesnt exist.
    connection = get_connection() # create a connection just for this function

    try:
    # ------------------------------------------------------------ USER -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS user (

                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL, 
                manager_id INTEGER, 
                password_hash TEXT NOT NULL, 
                salt TEXT NOT NULL, 
                must_change BOOLEAN NOT NULL DEFAULT true, 
                active BOOLEAN NOT NULL DEFAULT true,

                FOREIGN KEY (manager_id) REFERENCES user(user_id)
            ) 
        """)

    # ------------------------------------------------------------ COURSE -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS course (

                course_id INTEGER PRIMARY KEY,
                title TEXT UNIQUE NOT NULL, 
                description TEXT, 
                duration TEXT NOT NULL,
                points_reward INTEGER NOT NULL
            ) 
        """)

    # ------------------------------------------------------------ LESSON -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS lesson (
                
                lesson_id INTEGER PRIMARY KEY, 
                course_id INTEGER NOT NULL, 
                title TEXT NOT NULL, 
                content TEXT NOT NULL, 
                lesson_order INTEGER NOT NULL,

                FOREIGN KEY (course_id) REFERENCES course(course_id),
                UNIQUE(course_id, lesson_order) --  prevents 2 lessons within the same course having the same position.
            ) 
        """)

    # ------------------------------------------------------------ ENROLMENT -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS enrolment (

                enrolment_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL, 
                course_id INTEGER NOT NULL, 
                assigned_by INTEGER, 
                due_date TEXT,
                status TEXT NOT NULL, 
                progress_percent INTEGER NOT NULL, 
                completed_at TEXT,
                    
                FOREIGN KEY (user_id) REFERENCES user(user_id),
                FOREIGN KEY (course_id) REFERENCES course(course_id),
                FOREIGN KEY (assigned_by) REFERENCES user(user_id),
                    
                UNIQUE(user_id, course_id) -- Composite key to make sure every user assignment is unique (user cant be assigned to the same course twice)
            ) 
        """)

    # ------------------------------------------------------------ LESSONPROGRESS -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS lessonprogress (
                enrolment_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL, 
                completed_at TEXT NOT NULL,
            
                PRIMARY KEY (enrolment_id, lesson_id), -- not 2 primary keys, 2 fields act as 1 primary key
                FOREIGN KEY (enrolment_id) REFERENCES enrolment(enrolment_id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(lesson_id)
            ) 
        """)

    # ------------------------------------------------------------ QUIZQUESTION -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS quizquestion (
                question_id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL, 
                question_text TEXT NOT NULL,

                FOREIGN KEY (course_id) REFERENCES course(course_id)
            ) 
        """)


    # ------------------------------------------------------------ QUIZOPTION -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS quizoption (
                option_id INTEGER PRIMARY KEY, 
                question_id INTEGER NOT NULL, 
                option_text TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,

                FOREIGN KEY (question_id) REFERENCES quizquestion(question_id)
            ) 
        """)

    # ------------------------------------------------------------ QUIZATTEMPT -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS quizattempt (
                quiz_attempt_id INTEGER PRIMARY KEY, 
                enrolment_id INTEGER NOT NULL, 
                score INTEGER NOT NULL, 
                total INTEGER NOT NULL, 
                percent INTEGER NOT NULL,
                result TEXT NOT NULL, 
                attempted TEXT NOT NULL,

                FOREIGN KEY (enrolment_id) REFERENCES enrolment(enrolment_id)
            ) 
        """)


    # ------------------------------------------------------------ REWARD -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS reward (
                reward_id INTEGER PRIMARY KEY, 
                badge_name TEXT NOT NULL, 
                points_required INTEGER NOT NULL,

                UNIQUE(badge_name)
            ) 
        """)


    # ------------------------------------------------------------ USERREWARD -----------------------------------------------------------------#
        connection.execute(""" 
            CREATE TABLE IF NOT EXISTS userreward (
                user_id INTEGER NOT NULL,
                reward_id INTEGER NOT NULL,
                earned_at TEXT NOT NULL,

                PRIMARY KEY (user_id, reward_id),
                FOREIGN KEY (user_id) REFERENCES user(user_id),
                FOREIGN KEY (reward_id) REFERENCES reward(reward_id)
            )
        """)

        connection.commit() # commit changes to db through connection

    finally: 
        connection.close()

# --------------------------------------------------------------------- CRUD --------------------------------------------------------------------------- #
# ------------------------------------------------ USER ----------------------------------------------------- #

# CREATE

def create_user(name, email, role, manager_id, password_hash, salt):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute(""" 
            INSERT INTO user (name, email, role, manager_id, password_hash, salt)
            VALUES (?,?,?,?,?,?) -- placeholder for variables passed in from python
        """, 
        (name, email, role, manager_id, password_hash, salt)
        )

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally: 
        connection.close()

# READ

def get_user(user_id): # select and return a record of a user 
    connection = get_connection()
    try: 
        cursor = connection.execute("""
            SELECT user_id, name, email, role, manager_id, password_hash, salt, must_change, active
            FROM User 
            WHERE user_id = ?   
        """,
        (user_id,)
        )
        returned = cursor.fetchone() 

        if returned is None:
            return None

        return User(
            user_id = returned[0],
            name = returned[1],
            email = returned[2],
            role = returned[3],
            manager_id = returned[4],
            password_hash = returned[5],
            salt = returned[6],
            must_change = bool(returned[7]),
            active = bool(returned[8]),
        )
    finally:
        connection.close()

# UPDATE

def update_user(user_id, name, email, role, manager_id): # select a user using user id and UPDATE
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            UPDATE user
            SET name = ?, email = ?, role = ?, manager_id = ?
            WHERE user_id = ?
        """, (name, email, role, manager_id, user_id))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally: 
        connection.close()

# DEACTIVATE

def deactivate_user(user_id): # select a user and deactive
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            UPDATE user
            SET active = 0
            WHERE user_id = ?
        """, (user_id,))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally:
        connection.close()

# ------------------------------------------------------ COURSE ----------------------------------------------------------- #

# CREATE

def create_course(title, description, duration, points_reward):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute(""" 
            INSERT INTO course (title, description, duration, points_reward)
            VALUES (?,?,?,?) -- placeholder for variables passed in from python
        """, 
        (title, description, duration, points_reward)
        )

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally: 
        connection.close()

# READ

def get_course(course_id): # select and return a record of a course
    connection = get_connection()
    try: 
        cursor = connection.execute("""
            SELECT course_id, title, description, duration, points_reward
            FROM course
            WHERE course_id = ?
        """,
        (course_id,)
        )
        returned = cursor.fetchone() 

        if returned is None:
            return None

        return Course(
            course_id = returned[0],
            title = returned[1],
            description = returned[2],
            duration = returned[3],
            points_reward = returned[4],
        )
    finally:
        connection.close()

# UPDATE

def update_course(course_id, title, description, duration, points_reward): # select a course using course id and UPDATE
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            UPDATE course
            SET title = ?, description = ?, duration = ?, points_reward = ?
            WHERE course_id = ?
        """, (title, description, duration, points_reward, course_id))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally: 
        connection.close()

# DELETE

def delete_course(course_id): # select a course using course ID and delete
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            DELETE FROM course
            WHERE course_id = ?
        """, (course_id,))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally:
        connection.close()

# ------------------------------------------------------ LESSON ----------------------------------------------------------- #

# CREATE

def create_lesson(course_id, title, content, lesson_order):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute(""" 
            INSERT INTO lesson (course_id, title, content, lesson_order)
            VALUES (?,?,?,?) -- placeholder for variables passed in from python
        """, 
        (course_id, title, content, lesson_order)
        )

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally: 
        connection.close()

# READ

def get_lesson(lesson_id): # select and return a record of a lesson
    connection = get_connection()
    try: 
        cursor = connection.execute("""
            SELECT lesson_id, course_id, title, content, lesson_order
            FROM lesson
            WHERE lesson_id = ?
        """,
        (lesson_id,)
        )
        returned = cursor.fetchone() 

        if returned is None:
            return None

        return Lesson(
            lesson_id = returned[0],
            course_id = returned[1],
            title = returned[2],
            content = returned[3],
            lesson_order = returned[4],
        )
    finally:
        connection.close()

# UPDATE

def update_lesson(lesson_id, course_id, title, content, lesson_order): # select a lesson using lesson id and UPDATE
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            UPDATE lesson
            SET course_id = ?, title = ?, content = ?, lesson_order = ?
            WHERE lesson_id = ?
        """, (course_id, title, content, lesson_order, lesson_id))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally: 
        connection.close()

# DELETE 

def delete_lesson(lesson_id): # select a lesson using lesson ID and delete
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            DELETE FROM lesson
            WHERE lesson_id = ?
        """, (lesson_id,))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally:
        connection.close()

# ------------------------------------------------------ ENROLMENT ----------------------------------------------------------- #

# CREATE

def create_enrolment(user_id, course_id, assigned_by, due_date, status, progress_percent, completed_at):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute(""" 
            INSERT INTO enrolment (user_id, course_id, assigned_by, due_date, status, progress_percent, completed_at)
            VALUES (?,?,?,?,?,?,?) -- placeholder for variables passed in from python
        """, 
        (user_id, course_id, assigned_by, due_date, status, progress_percent, completed_at)
        )

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally: 
        connection.close()

# READ

def get_enrolment(enrolment_id): # select and return a record of an enrolment
    connection = get_connection()
    try: 
        cursor = connection.execute("""
            SELECT enrolment_id, user_id, course_id, assigned_by, due_date, status, progress_percent, completed_at
            FROM enrolment
            WHERE enrolment_id = ?
        """,
        (enrolment_id,)
        )
        returned = cursor.fetchone() 

        if returned is None:
            return None

        return Enrolment(
            enrolment_id = returned[0],
            user_id = returned[1],
            course_id = returned[2],
            assigned_by = returned[3],
            due_date = date.fromisoformat(returned[4]) if returned[4] else None, # converts the passed in string into a date object if one is passed in, else it is Null
            status = returned[5],
            progress_percent = returned[6],
            completed_at= date.fromisoformat(returned[7]) if returned[7] else None # converts the passed in string into a date object if one is passed in, else it is Null
        )
    finally:
        connection.close()

# UPDATE

def update_enrolment(enrolment_id, due_date, status, progress_percent, completed_at):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE enrolment
            SET due_date = ?, status = ?, progress_percent = ?, completed_at = ?
            WHERE enrolment_id = ?
        """, (due_date, status, progress_percent, completed_at, enrolment_id))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

# DELETE 

def delete_enrolment(enrolment_id): # select a lesson using enrolment ID and delete
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            DELETE FROM enrolment
            WHERE enrolment_id = ?
        """, (enrolment_id,))

        connection.commit()

        return cursor.rowcount > 0 # check if the SQL update has worked, rowcount will be "1" if it worked and "0" if not. 1 = true 0 = false. 

    finally:
        connection.close()

# ------------------------------------------------------ LESSONPROGRESS ----------------------------------------------------------- #

# CREATE 

def create_lesson_progress(enrolment_id, lesson_id, completed_at):
    connection = get_connection() # create a connection just for this function

    try: 
        cursor = connection.execute("""
            INSERT into lessonprogress (enrolment_id, lesson_id, completed_at)
            VALUES(?, ?, ?)
        """, (enrolment_id, lesson_id, completed_at))
    
        connection.commit() 

        return enrolment_id, lesson_id

    finally: 
        connection.close()

# READ 

def get_lesson_progress(enrolment_id, lesson_id):
    connection = get_connection()

    try: 
        cursor = connection.execute("""
            SELECT enrolment_id, lesson_id, completed_at
            FROM lessonprogress 
            WHERE enrolment_id = ? AND lesson_id = ?
        """, (enrolment_id, lesson_id))

        returned = cursor.fetchone()

        if returned is None: 
            return None

        return LessonProgress( 
            enrolment_id = returned[0], 
            lesson_id = returned[1], 
            completed_at=date.fromisoformat(returned[2])
        )

    finally: 
        connection.close()

# ------------------------------------------------------ QUIZQUESTION ----------------------------------------------------------- #

# CREATE  

# READ

# UPDATE

# DELETE

# ------------------------------------------------------ QUIZOPTION ----------------------------------------------------------- #
# ------------------------------------------------------ QUIZATTEMPT ----------------------------------------------------------- #
# -------------------------------------------------------REWARD ----------------------------------------------------------- #
# ------------------------------------------------------ USERREWARD ---------------------------------------------------------- #

# IN PROGRESS

