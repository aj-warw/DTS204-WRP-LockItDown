from datetime import date

# -------------------------------------------------------- USER ----------------------------------------------------- #
class User: 
    # ---------------------- USER ATTRIBUTES ------------------ #
    def __init__(self, user_id, name, email, role, manager_id, password_hash, salt, must_change, active):
        self.__user_id = user_id
        self.__name = name
        self.__email = email
        self.__role = role
        self.__manager_id = manager_id
        self.__password_hash = password_hash
        self.__salt = salt
        self.__must_change = must_change
        self.__active = active

    # ---------------------- USER METHODS ------------------ #
    def is_active(self):
        return bool(self.__active) # checks the active attribute to check if a user is active and returns true or false

# -------------------------------------------------------- COURSE ----------------------------------------------------- #
class Course: 
    # ---------------------- COURSE ATTRIBUTES ------------------ #
    def __init__(self, course_id, title, description, duration, points_reward):
        self.__course_id = course_id
        self.__title = title
        self.__description = description
        self.__duration = duration
        self.__points_reward = points_reward

    # ---------------------- COURSE METHODS ------------------ #

# -------------------------------------------------------- LESSON ----------------------------------------------------- #
class Lesson: 
    # ---------------------- LESSON ATTRIBUTES ------------------ #
    def __init__(self, lesson_id, course_id, title, content, lesson_order):
        self.__lesson_id = lesson_id
        self.__course_id = course_id
        self.__title = title
        self.__content = content
        self.__lesson_order = lesson_order


    # adding read only properties to "Lesson" by making functions that use the private lesson IDs and 
    # course IDs and return the content of lesson ID and course ID without needing to unprivate the attributes
    @property
    def lesson_id(self):
        return self.__lesson_id

    @property
    def course_id(self):
        return self.__course_id

    # ---------------------- LESSON METHODS ------------------ #


# -------------------------------------------------------- ENROLMENT ----------------------------------------------------- #
class Enrolment: 
    # ---------------------- ENROLMENT ATTRIBUTES ------------------ #
    def __init__(self, enrolment_id, user_id, course_id, assigned_by, due_date, status, progress_percent, completed_at):
        self.__enrolment_id = enrolment_id
        self.__user_id = user_id
        self.__course_id = course_id
        self.__assigned_by = assigned_by
        self.__due_date = due_date
        self.__status = status
        self.__progress_percent = progress_percent
        self.__completed_at = completed_at

    @property
    def progress_percent(self):
        return self.__progress_percent

    # ---------------------- ENROLMENT METHODS ------------------ #
    def is_completed(self): # check if the enrolment is completed or not and return true or false.
        if self.__status == "Complete":
            return True
        
        else: 
            return False
        

    def is_overdue(self, today): 
        if self.__due_date is None: # check if a due date exists and just return false if there isnt
            return False
        
        else:
            return today > self.__due_date and not self.is_completed() # check if the date is overdue and if the enrolment is completed and return true or false.

    def complete_lesson(self, lesson: Lesson):

        # ensures that the lesson belongs to the enrolled course
        if lesson.course_id != self.__course_id: 
            raise ValueError("Lesson does not belong to this enrolments course")

        # creates a lesson progress object to record completion using the values from the current enrolment and lesson objects being used
        lesson_progress = LessonProgress(
            self.__enrolment_id,
            lesson.lesson_id,
            date.today()
        )

        return lesson_progress

    
    def update_progress(self, completed, total):
        if total <= 0: 
            raise ValueError("The total amount of lessons must be greater than 0") # throw error if there are no total lessons

        if completed > total or completed < 0:
            raise ValueError("Invalid number of completed lessons") # throw error if there are more completed lessons than total amount of lessons of if there are less than 0 completed lessons

        self.__progress_percent = round((completed / total)* 100) # make a percentage from the completed lessons and total lessons

# -------------------------------------------------------- LESSONPROGRESS ----------------------------------------------------- #
class LessonProgress: 
    # ---------------------- LESSONPROGRESS ATTRIBUTES ------------------ #
    def __init__(self, enrolment_id, lesson_id, completed_at): 
        self.__enrolment_id = enrolment_id
        self.__lesson_id = lesson_id
        self.__completed_at = completed_at

    # ---------------------- LESSONPROGRESS METHODS ------------------ #
    

# -------------------------------------------------------- QUIZQUESTION ----------------------------------------------------- #
class QuizQuestion: 
    # ---------------------- QUIZQUESTION ATTRIBUTES ------------------ #
    def __init__(self, question_id, course_id, question_text):
        self.__question_id = question_id
        self.__course_id = course_id
        self.__question_text = question_text

    # ---------------------- QUIZQUESTION METHODS ------------------ #
    
    def check_answer(self, quiz_option: "QuizOption"):
        if self.__question_id != quiz_option.question_id: 
            raise ValueError("The option in question does not belong to the question being checked") # raise an error if somehow an invalid question option gets passed

        return quiz_option.is_correct # returns the value in the "is_correct" field in the selection of options. If the answer is right, True, otherwise, False.
        
# -------------------------------------------------------- QUIZOPTION ----------------------------------------------------- #
class QuizOption: 
    # ---------------------- QUIZOPTION ATTRIBUTES ------------------ #
    def __init__(self, option_id, question_id, option_text, is_correct):
        self.__option_id = option_id
        self.__question_id = question_id
        self.__option_text = option_text
        self.__is_correct = is_correct

    @property
    def is_correct(self): 
        return self.__is_correct

    @property
    def question_id(self): 
        return self.__question_id

    # ---------------------- QUIZOPTION METHODS ------------------ #


# -------------------------------------------------------- QUIZATTEMPT ----------------------------------------------------- #
class QuizAttempt: 
    # ---------------------- QUIZATTEMPT ATTRIBUTES ------------------ #
    def __init__(self, quiz_attempt_id, enrolment_id, score, total, percent, result, attempted):
        self.__quiz_attempt_id = quiz_attempt_id
        self.__enrolment_id = enrolment_id 
        self.__score = score    
        self.__total = total
        self.__percent = percent 
        self.__result = result
        self.__attempted = attempted

    @property
    def score(self): 
        return self.__score
    
    # ---------------------- QUIZATTEMPT METHODS ------------------ #
    def calculate_percentage(self):
        if self.__total <= 0: 
            raise ValueError("The amount of lessons in the quiz attempt is 0, the quiz must contain at least one question.")

        if self.__score > self.__total or self.__score < 0: 
            raise ValueError("There has been an error with the score, the score is either more than the total amount of questions or less than 0")

        self.__percent = round((self.__score / self.__total)* 100)

        return self.__percent

    def has_passed(self, pass_mark): # VERY IMPORTANT REMINDER - CREATE A VARIABLE FOR PASS MARKS OR CREATE A CONSTANT PROGRAM WIDE PASS MARK
        return self.calculate_percentage() >= pass_mark # returns true or false if quiz result % is greater than or equal to pass mark.

# -------------------------------------------------------- REWARD ----------------------------------------------------- #
class Reward:
    # ---------------------- REWARD ATTRIBUTES ------------------ #
    def __init__(self, reward_id, badge_name, points_required):
        self.__reward_id = reward_id
        self.__badge_name = badge_name
        self.__points_required = points_required

    # ---------------------- REWARD METHODS ------------------ #
    def is_unlocked(self, total_points): # VERY IMPORTANT REMINDER - THE PROGRAM WILL DERIVE TOTAL POINTS BY LOOKING THROUGHT THE ENROLMENT TABLE AND FINDING WHICH USER_ID HAS COMPLETED WHICH COURSES AND THEN CHECK THE COURSES TABLE TO FIND OUT HOW MANY POINTS THAT USER IS ENTITLED TO IN ORDER TO WORK OUT THE POINTS.
        return total_points >= self.__points_required

# -------------------------------------------------------- USERREWARD ----------------------------------------------------- #
class UserReward: 
    # ---------------------- USERREWARD ATTRIBUTES ------------------ #
    def __init__(self, user_id, reward_id, earned_at):
        self.__user_id = user_id
        self.__reward_id = reward_id
        self.__earned_at = earned_at

    # ---------------------- USERREWARD METHODS ------------------ #
        









    



