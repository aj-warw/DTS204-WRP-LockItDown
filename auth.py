import hashlib
import secrets

from db import (
    get_user_by_email,
    get_user,
    create_user,
    update_user_password,
    deactivate_user,
    update_failed_login_attempts,
    reset_failed_login_attempts,
    lock_user_account,
    unlock_user_account,
    create_audit_log
)


MAX_FAILED_LOGIN_ATTEMPTS = 5


# PASSWORD SECURITY SECTION

def hash_password(password): 

    if not isinstance(password, str) or password == "":
        raise ValueError("Password must not be empty")

    # generate a random 16 byte salt
    salt = secrets.token_bytes(16)

    # hash password using PBKDF2 HMAC SHA256
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("UTF-8"),
        salt,
        120000
    )

    # SQLite expects strings so convert both values to hexadecimal
    return password_hash.hex(), salt.hex()


def verify_password(password, password_hash, salt): # checks the entered password against the stored password details

    # return false if any required password information is missing
    if not password or not password_hash or not salt:
        return False

    try:
        # convert the stored salt from hexadecimal back into bytes
        salt_bytes = bytes.fromhex(salt)

        # hash the password entered by the user using the stored salt
        entered_password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("UTF-8"),
            salt_bytes,
            120000
        )

        # convert the stored password hash from hexadecimal back into bytes
        stored_password_hash = bytes.fromhex(password_hash)

        # compare the entered password hash and stored password hash
        return secrets.compare_digest(
            entered_password_hash,
            stored_password_hash
        )

    except (ValueError, TypeError):
        return False


def password_is_valid(password): # checks whether a password meets the password requirements

    if not isinstance(password, str):
        return False

    # password must contain at least 8 characters
    if len(password) < 8:
        return False

    # password must contain at least one uppercase letter
    if not any(character.isupper() for character in password):
        return False

    # password must contain at least one lowercase letter
    if not any(character.islower() for character in password):
        return False

    # password must contain at least one number
    if not any(character.isdigit() for character in password):
        return False

    # password must contain at least one special character
    special_characters = "!@#$%^&*()-_=+[]{};:,.?/"

    if not any(character in special_characters for character in password):
        return False

    return True


def get_password_validation_message(password): # returns a detailed message when a password is invalid

    if not isinstance(password, str) or password == "":
        return "A password must be entered"

    if len(password) < 8:
        return "The password must contain at least 8 characters"

    if not any(character.isupper() for character in password):
        return "The password must contain at least one uppercase letter"

    if not any(character.islower() for character in password):
        return "The password must contain at least one lowercase letter"

    if not any(character.isdigit() for character in password):
        return "The password must contain at least one number"

    special_characters = "!@#$%^&*()-_=+[]{};:,.?/"

    if not any(character in special_characters for character in password):
        return "The password must contain at least one special character"

    return None


def generate_temporary_password(): # creates a random temporary password

    # generate different character groups to make sure the password meets the password rules
    uppercase_character = secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    lowercase_character = secrets.choice("abcdefghijklmnopqrstuvwxyz")
    number_character = secrets.choice("0123456789")
    special_character = secrets.choice("!@#$%^&*")

    # create additional random characters
    remaining_characters = "".join(
        secrets.choice(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
        )
        for character in range(8)
    )

    # combine the required characters with the random characters
    password_characters = list(
        uppercase_character
        + lowercase_character
        + number_character
        + special_character
        + remaining_characters
    )

    # securely rearrange the characters so the required characters are not always in the same position
    secrets.SystemRandom().shuffle(password_characters)

    return "".join(password_characters)


# AUTHORISATION SECTION

def authorise_role(user, allowed_roles): # checks that the current user has permission to access a function

    if user is None:
        return False

    if not user.is_active():
        return False

    # convert a single role into a list so either format can be used
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    return user.role in allowed_roles


def is_admin(user):
    return authorise_role(user, ["Admin"])


def is_manager(user):
    return authorise_role(user, ["Manager"])


def is_employee(user):
    return authorise_role(user, ["Employee"])


def can_manage_training(user): # admins can create training and managers can assign training
    return authorise_role(user, ["Admin", "Manager"])


# AUTHENTICATION

def authenticate_user(email, password): # returns the user object when the login details are correct

    if not email or not password:
        return None

    # remove accidental spaces and convert the email to lowercase
    email = email.strip().lower()

    # retrieve the user object with the matching email address
    user = get_user_by_email(email)

    if user is None:
        return None

    # prevent deactivated accounts from logging in
    if not user.is_active():
        create_audit_log(
            user.user_id,
            "LOGIN_BLOCKED",
            "A login attempt was made using a deactivated account"
        )

        return None

    # prevent locked accounts from logging in
    if user.is_locked():
        create_audit_log(
            user.user_id,
            "LOGIN_BLOCKED",
            "A login attempt was made using a locked account"
        )

        return None

    # check the password against the password hash stored in the database
    password_is_correct = verify_password(
        password,
        user.password_hash,
        user.salt
    )

    if password_is_correct:
        # clear failed login attempts after a successful login
        reset_failed_login_attempts(user.user_id)

        create_audit_log(
            user.user_id,
            "LOGIN_SUCCESS",
            "User successfully logged into the platform"
        )

        # return an updated version of the user
        return get_user(user.user_id)

    # increase the failed login attempts when the password is incorrect
    new_failed_attempts = user.failed_login_attempts + 1

    update_failed_login_attempts(
        user.user_id,
        new_failed_attempts
    )

    create_audit_log(
        user.user_id,
        "LOGIN_FAILED",
        "An incorrect password was entered"
    )

    # lock the account after the maximum failed login attempts is reached
    if new_failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        lock_user_account(user.user_id)

        create_audit_log(
            user.user_id,
            "ACCOUNT_LOCKED",
            "The account was locked after too many failed login attempts"
        )

    return None


# PASSWORD MANAGEMENT SECTION 

def change_password(user_id, current_password, new_password): # allows a user to change their own password

    user = get_user(user_id)

    if user is None:
        return False

    if not user.is_active():
        return False

    # check that the current password entered by the user is correct
    if not verify_password(
        current_password,
        user.password_hash,
        user.salt
    ):
        create_audit_log(
            user_id,
            "PASSWORD_CHANGE_FAILED",
            "The current password entered by the user was incorrect"
        )

        return False

    # prevent the user from reusing their current password
    if verify_password(
        new_password,
        user.password_hash,
        user.salt
    ):
        return False

    # make sure the new password meets the password requirements
    if not password_is_valid(new_password):
        return False

    # hash the new password before saving it
    password_hash, salt = hash_password(new_password)

    updated = update_user_password(
        user_id,
        password_hash,
        salt,
        must_change=False
    )

    if updated:
        reset_failed_login_attempts(user_id)
        unlock_user_account(user_id)

        create_audit_log(
            user_id,
            "PASSWORD_CHANGED",
            "The user changed their password"
        )

    return updated


def reset_user_password(user_id, temp_password=None): # resets a password and forces a change after login

    user = get_user(user_id)

    if user is None:
        return None

    if not user.is_active():
        return None

    # generate a secure temporary password if one was not supplied
    if temp_password is None:
        temp_password = generate_temporary_password()

    if not password_is_valid(temp_password):
        return None

    # hash the temporary password before saving it
    password_hash, salt = hash_password(temp_password)

    updated = update_user_password(
        user_id,
        password_hash,
        salt,
        must_change=True
    )

    if not updated:
        return None

    # allow the user to log in using the temporary password
    reset_failed_login_attempts(user_id)
    unlock_user_account(user_id)

    create_audit_log(
        user_id,
        "PASSWORD_RESET",
        "The users password was reset and must be changed after login"
    )

    # return the clear temporary password once so it can be given to the user
    return temp_password


# USER MANAGEMENT 

def register_user(name, email, role, manager_id, password=None): # securely creates a new user account

    if not name or not email or not role:
        return None

    email = email.strip().lower()
    role = role.strip().title()

    valid_roles = ["Admin", "Manager", "Employee"]

    if role not in valid_roles:
        return None

    # prevent duplicate email addresses
    if get_user_by_email(email) is not None:
        return None

    # generate a temporary password if an administrator has not supplied one
    if password is None:
        password = generate_temporary_password()

    if not password_is_valid(password):
        return None

    password_hash, salt = hash_password(password)

    # new accounts must change their temporary password after login
    created_user_id = create_user(
        name,
        email,
        role,
        manager_id,
        password_hash,
        salt,
        must_change=True
    )

    if not created_user_id:
        return None

    create_audit_log(
        created_user_id,
        "ACCOUNT_CREATED",
        "A new user account was created"
    )

    # return the user ID and temporary password to the administrator
    return created_user_id, password


def disable_user_account(user_id): # deactivates an account and prevents login

    user = get_user(user_id)

    if user is None:
        return False

    if not user.is_active():
        return False

    deactivated = deactivate_user(user_id)

    if deactivated:
        create_audit_log(
            user_id,
            "ACCOUNT_DEACTIVATED",
            "The user account was deactivated"
        )

    return deactivated


def administrator_unlock_account(admin_user, user_id): # allows an administrator to unlock an account

    if not authorise_role(admin_user, ["Admin"]):
        return False

    user = get_user(user_id)

    if user is None:
        return False

    unlocked = unlock_user_account(user_id)

    if unlocked:
        reset_failed_login_attempts(user_id)

        create_audit_log(
            user_id,
            "ACCOUNT_UNLOCKED",
            "The account was unlocked by an administrator"
        )

    return unlocked
