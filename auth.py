import sqlite3
from db import get_connection
import hashlib
import secrets
from db import get_user_by_email, get_user, create_user, update_user_password

TEMP_PASS = "Secure123!" # constant temporary password can be changed later

def hash_password(password): # hashes input, creates password hash and salt
    # generate a random 16byte salt
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac( # hash using PBKDF2_HMAC - SHA256
        "sha256",
        password.encode("UTF-8"),
        salt,
        120000
    )

    # sqlite expects hex
    return password_hash.hex(), salt.hex()

def verify_password(password_hash, salt): # checks hash + salt against records in db
    pass

def authenticate_user(email, password): # allows user access if password hash + salt is verified and with corresponding email
    pass

def reset_user_password(user_id):

    password_hash, salt = hash_password(TEMP_PASS) # hash a password (constant for now), unpack the returned tuple into password_hash and salt

    # uses db function take the variables from here and send them to database
    updated = update_user_password( 
        user_id,
        password_hash,
        salt,
        must_change=False
    )

    if updated: # if the password was successfully updated return the cleartext password
        return TEMP_PASS

    return None # else return nothing
    