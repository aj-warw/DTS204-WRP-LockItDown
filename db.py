import sqlite3
from models import (
    User,
    Course,
    Lesson,
    Enrolment,
    LessonProgress,
    QuizQuestion,
    QuizOption,
    QuizAttempt,
    UserReward,
    Reward
)
from datetime import date


# opens a new connection and enforces foreign keys
def get_connection():
    connection = sqlite3.connect("lockitdown.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise_database(): # create database if it doesnt exist
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
                failed_login_attempts INTEGER NOT NULL DEFAULT 0,
                account_locked BOOLEAN NOT NULL DEFAULT false,

                FOREIGN KEY (manager_id) REFERENCES user(user_id)
            )
        """)

        # check the existing user table in case the database was created
        # before the new security fields were added
        user_columns = connection.execute(
            "PRAGMA table_info(user)"
        ).fetchall()

        user_column_names = [
            column[1]
            for column in user_columns
        ]

        # add the failed login attempts field to an existing database
        if "failed_login_attempts" not in user_column_names:
            connection.execute("""
                ALTER TABLE user
                ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0
            """)

        # add the account locked field to an existing database
        if "account_locked" not in user_column_names:
            connection.execute("""
                ALTER TABLE user
                ADD COLUMN account_locked BOOLEAN NOT NULL DEFAULT false
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
                UNIQUE(course_id, lesson_order)
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

                UNIQUE(user_id, course_id)
            )
        """)

        # ------------------------------------------------------------ LESSONPROGRESS -----------------------------------------------------------------#
        connection.execute("""
            CREATE TABLE IF NOT EXISTS lessonprogress (

                enrolment_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,

                PRIMARY KEY (enrolment_id, lesson_id),
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

        # ------------------------------------------------------------ AUDITLOG -----------------------------------------------------------------#
        connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (

                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES user(user_id)
            )
        """)

        connection.commit() # commit changes to db through connection

    finally:
        connection.close()


# --------------------------------------------------------------------- CRUD --------------------------------------------------------------------------- #
# ------------------------------------------------ USER ----------------------------------------------------- #

# CREATE

def create_user(
    name,
    email,
    role,
    manager_id,
    password_hash,
    salt,
    must_change=True
):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute("""
            INSERT INTO user (
                name,
                email,
                role,
                manager_id,
                password_hash,
                salt,
                must_change,
                active,
                failed_login_attempts,
                account_locked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, 0)
        """,
        (
            name,
            email,
            role,
            manager_id,
            password_hash,
            salt,
            int(must_change)
        ))

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    except sqlite3.IntegrityError:
        return None

    finally:
        connection.close()


# READ

def get_user(user_id): # select and return a record of a user
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                user_id,
                name,
                email,
                role,
                manager_id,
                password_hash,
                salt,
                must_change,
                active,
                failed_login_attempts,
                account_locked
            FROM user
            WHERE user_id = ?
        """,
        (user_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return User(
            user_id=returned[0],
            name=returned[1],
            email=returned[2],
            role=returned[3],
            manager_id=returned[4],
            password_hash=returned[5],
            salt=returned[6],
            must_change=bool(returned[7]),
            active=bool(returned[8]),
            failed_login_attempts=returned[9],
            account_locked=bool(returned[10])
        )

    finally:
        connection.close()


def get_user_by_email(email): # select and return a user using their email address
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                user_id,
                name,
                email,
                role,
                manager_id,
                password_hash,
                salt,
                must_change,
                active,
                failed_login_attempts,
                account_locked
            FROM user
            WHERE LOWER(email) = LOWER(?)
        """,
        (email,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return User(
            user_id=returned[0],
            name=returned[1],
            email=returned[2],
            role=returned[3],
            manager_id=returned[4],
            password_hash=returned[5],
            salt=returned[6],
            must_change=bool(returned[7]),
            active=bool(returned[8]),
            failed_login_attempts=returned[9],
            account_locked=bool(returned[10])
        )

    finally:
        connection.close()


# UPDATE

def update_user(user_id, name, email, role, manager_id): # select a user using user id and update
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET name = ?, email = ?, role = ?, manager_id = ?
            WHERE user_id = ?
        """,
        (
            name,
            email,
            role,
            manager_id,
            user_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def update_user_password(
    user_id,
    password_hash,
    salt,
    must_change=False
): # updates the users password hash, salt and password change requirement
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET password_hash = ?,
                salt = ?,
                must_change = ?
            WHERE user_id = ?
        """,
        (
            password_hash,
            salt,
            int(must_change),
            user_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DEACTIVATE

def deactivate_user(user_id): # select a user and deactivate
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET active = 0
            WHERE user_id = ?
        """,
        (user_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------ USER SECURITY ----------------------------------------------------- #

def update_failed_login_attempts(
    user_id,
    failed_login_attempts
): # updates the amount of failed login attempts for a user
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET failed_login_attempts = ?
            WHERE user_id = ?
        """,
        (
            failed_login_attempts,
            user_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def reset_failed_login_attempts(user_id): # resets failed attempts after a successful login
    return update_failed_login_attempts(
        user_id,
        0
    )


def lock_user_account(user_id): # locks the users account
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET account_locked = 1
            WHERE user_id = ?
        """,
        (user_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def unlock_user_account(user_id): # unlocks the user and resets their failed attempts
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE user
            SET account_locked = 0,
                failed_login_attempts = 0
            WHERE user_id = ?
        """,
        (user_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------ AUDIT LOG ----------------------------------------------------- #

def create_audit_log(user_id, action, description): # records an important security event
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO audit_logs (
                user_id,
                action,
                description
            )
            VALUES (?, ?, ?)
        """,
        (
            user_id,
            action,
            description
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_audit_logs(): # retrieves all audit logs with the newest first
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                log_id,
                user_id,
                action,
                description,
                created_at
            FROM audit_logs
            ORDER BY created_at DESC, log_id DESC
        """)

        return cursor.fetchall()

    finally:
        connection.close()


# ------------------------------------------------------ COURSE ----------------------------------------------------------- #

# CREATE

def create_course(title, description, duration, points_reward):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute("""
            INSERT INTO course (
                title,
                description,
                duration,
                points_reward
            )
            VALUES (?, ?, ?, ?)
        """,
        (
            title,
            description,
            duration,
            points_reward
        ))

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally:
        connection.close()


# READ

def get_course(course_id): # select and return a record of a course
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                course_id,
                title,
                description,
                duration,
                points_reward
            FROM course
            WHERE course_id = ?
        """,
        (course_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return Course(
            course_id=returned[0],
            title=returned[1],
            description=returned[2],
            duration=returned[3],
            points_reward=returned[4]
        )

    finally:
        connection.close()


# UPDATE

def update_course(
    course_id,
    title,
    description,
    duration,
    points_reward
): # select a course using course id and update
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE course
            SET title = ?,
                description = ?,
                duration = ?,
                points_reward = ?
            WHERE course_id = ?
        """,
        (
            title,
            description,
            duration,
            points_reward,
            course_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_course(course_id): # select a course using course ID and delete
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM course
            WHERE course_id = ?
        """,
        (course_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ LESSON ----------------------------------------------------------- #

# CREATE

def create_lesson(course_id, title, content, lesson_order):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute("""
            INSERT INTO lesson (
                course_id,
                title,
                content,
                lesson_order
            )
            VALUES (?, ?, ?, ?)
        """,
        (
            course_id,
            title,
            content,
            lesson_order
        ))

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally:
        connection.close()


# READ

def get_lesson(lesson_id): # select and return a record of a lesson
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                lesson_id,
                course_id,
                title,
                content,
                lesson_order
            FROM lesson
            WHERE lesson_id = ?
        """,
        (lesson_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return Lesson(
            lesson_id=returned[0],
            course_id=returned[1],
            title=returned[2],
            content=returned[3],
            lesson_order=returned[4]
        )

    finally:
        connection.close()


# UPDATE

def update_lesson(
    lesson_id,
    course_id,
    title,
    content,
    lesson_order
): # select a lesson using lesson id and update
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE lesson
            SET course_id = ?,
                title = ?,
                content = ?,
                lesson_order = ?
            WHERE lesson_id = ?
        """,
        (
            course_id,
            title,
            content,
            lesson_order,
            lesson_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_lesson(lesson_id): # select a lesson using lesson ID and delete
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM lesson
            WHERE lesson_id = ?
        """,
        (lesson_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ ENROLMENT ----------------------------------------------------------- #

# CREATE

def create_enrolment(
    user_id,
    course_id,
    assigned_by,
    due_date,
    status,
    progress_percent,
    completed_at
):
    connection = get_connection() # create a connection just for this function

    try:
        cursor = connection.execute("""
            INSERT INTO enrolment (
                user_id,
                course_id,
                assigned_by,
                due_date,
                status,
                progress_percent,
                completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            course_id,
            assigned_by,
            due_date,
            status,
            progress_percent,
            completed_at
        ))

        connection.commit()

        return cursor.lastrowid # returns the id of the newly created record

    finally:
        connection.close()


# READ

def get_enrolment(enrolment_id): # select and return a record of an enrolment
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                enrolment_id,
                user_id,
                course_id,
                assigned_by,
                due_date,
                status,
                progress_percent,
                completed_at
            FROM enrolment
            WHERE enrolment_id = ?
        """,
        (enrolment_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return Enrolment(
            enrolment_id=returned[0],
            user_id=returned[1],
            course_id=returned[2],
            assigned_by=returned[3],
            due_date=date.fromisoformat(returned[4]) if returned[4] else None,
            status=returned[5],
            progress_percent=returned[6],
            completed_at=date.fromisoformat(returned[7]) if returned[7] else None
        )

    finally:
        connection.close()


# UPDATE

def update_enrolment(
    enrolment_id,
    due_date,
    status,
    progress_percent,
    completed_at
):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE enrolment
            SET due_date = ?,
                status = ?,
                progress_percent = ?,
                completed_at = ?
            WHERE enrolment_id = ?
        """,
        (
            due_date,
            status,
            progress_percent,
            completed_at,
            enrolment_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_enrolment(enrolment_id): # select an enrolment using enrolment ID and delete
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM enrolment
            WHERE enrolment_id = ?
        """,
        (enrolment_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ LESSONPROGRESS ----------------------------------------------------------- #

# CREATE

def create_lesson_progress(enrolment_id, lesson_id, completed_at):
    connection = get_connection() # create a connection just for this function

    try:
        connection.execute("""
            INSERT INTO lessonprogress (
                enrolment_id,
                lesson_id,
                completed_at
            )
            VALUES (?, ?, ?)
        """,
        (
            enrolment_id,
            lesson_id,
            completed_at
        ))

        connection.commit()

        return enrolment_id, lesson_id

    finally:
        connection.close()


# READ

def get_lesson_progress(enrolment_id, lesson_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                enrolment_id,
                lesson_id,
                completed_at
            FROM lessonprogress
            WHERE enrolment_id = ?
            AND lesson_id = ?
        """,
        (
            enrolment_id,
            lesson_id
        ))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return LessonProgress(
            enrolment_id=returned[0],
            lesson_id=returned[1],
            completed_at=date.fromisoformat(returned[2])
        )

    finally:
        connection.close()


# ------------------------------------------------------ QUIZQUESTION ----------------------------------------------------------- #

# CREATE

def create_quiz_question(course_id, question_text):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO quizquestion (
                course_id,
                question_text
            )
            VALUES (?, ?)
        """,
        (
            course_id,
            question_text
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


# READ

def get_quiz_question(question_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                question_id,
                course_id,
                question_text
            FROM quizquestion
            WHERE question_id = ?
        """,
        (question_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return QuizQuestion(
            question_id=returned[0],
            course_id=returned[1],
            question_text=returned[2]
        )

    finally:
        connection.close()


# UPDATE

def update_quiz_question(question_id, course_id, question_text):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE quizquestion
            SET question_text = ?
            WHERE question_id = ?
            AND course_id = ?
        """,
        (
            question_text,
            question_id,
            course_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_quiz_question(question_id, course_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM quizquestion
            WHERE question_id = ?
            AND course_id = ?
        """,
        (
            question_id,
            course_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ QUIZOPTION ----------------------------------------------------------- #

# CREATE

def create_quiz_option(question_id, option_text, is_correct):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO quizoption (
                question_id,
                option_text,
                is_correct
            )
            VALUES (?, ?, ?)
        """,
        (
            question_id,
            option_text,
            int(is_correct)
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


# READ

def get_quiz_option(option_id, question_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                option_id,
                question_id,
                option_text,
                is_correct
            FROM quizoption
            WHERE option_id = ?
            AND question_id = ?
        """,
        (
            option_id,
            question_id
        ))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return QuizOption(
            option_id=returned[0],
            question_id=returned[1],
            option_text=returned[2],
            is_correct=bool(returned[3])
        )

    finally:
        connection.close()


# UPDATE

def update_quiz_option(
    option_id,
    question_id,
    option_text,
    is_correct
):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE quizoption
            SET question_id = ?,
                option_text = ?,
                is_correct = ?
            WHERE option_id = ?
        """,
        (
            question_id,
            option_text,
            int(is_correct),
            option_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_quiz_option(option_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM quizoption
            WHERE option_id = ?
        """,
        (option_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ QUIZATTEMPT ----------------------------------------------------------- #

# CREATE

def create_quiz_attempt(
    enrolment_id,
    score,
    total,
    percent,
    result,
    attempted
):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO quizattempt (
                enrolment_id,
                score,
                total,
                percent,
                result,
                attempted
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            enrolment_id,
            score,
            total,
            percent,
            result,
            attempted
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


# READ

def get_quiz_attempt(quiz_attempt_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                quiz_attempt_id,
                enrolment_id,
                score,
                total,
                percent,
                result,
                attempted
            FROM quizattempt
            WHERE quiz_attempt_id = ?
        """,
        (quiz_attempt_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return QuizAttempt(
            quiz_attempt_id=returned[0],
            enrolment_id=returned[1],
            score=returned[2],
            total=returned[3],
            percent=returned[4],
            result=returned[5],
            attempted=returned[6]
        )

    finally:
        connection.close()


# ------------------------------------------------------- REWARD ----------------------------------------------------------- #

# CREATE

def create_reward(badge_name, points_required):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO reward (
                badge_name,
                points_required
            )
            VALUES (?, ?)
        """,
        (
            badge_name,
            points_required
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


# READ

def get_reward(reward_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                reward_id,
                badge_name,
                points_required
            FROM reward
            WHERE reward_id = ?
        """,
        (reward_id,))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return Reward(
            reward_id=returned[0],
            badge_name=returned[1],
            points_required=returned[2]
        )

    finally:
        connection.close()


# UPDATE

def update_reward(reward_id, badge_name, points_required):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE reward
            SET badge_name = ?,
                points_required = ?
            WHERE reward_id = ?
        """,
        (
            badge_name,
            points_required,
            reward_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# DELETE

def delete_reward(reward_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM reward
            WHERE reward_id = ?
        """,
        (reward_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ------------------------------------------------------ USERREWARD ---------------------------------------------------------- #

# CREATE

def create_userreward(user_id, reward_id, earned_at):
    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO userreward (
                user_id,
                reward_id,
                earned_at
            )
            VALUES (?, ?, ?)
        """,
        (
            user_id,
            reward_id,
            earned_at
        ))

        connection.commit()

        return user_id, reward_id # composite primary key

    finally:
        connection.close()


# READ

def get_userreward(user_id, reward_id):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                user_id,
                reward_id,
                earned_at
            FROM userreward
            WHERE user_id = ?
            AND reward_id = ?
        """,
        (
            user_id,
            reward_id
        ))

        returned = cursor.fetchone()

        if returned is None:
            return None

        return UserReward(
            user_id=returned[0],
            reward_id=returned[1],
            earned_at=returned[2]
        )

    finally:
        connection.close()


# IN PROGRESS
