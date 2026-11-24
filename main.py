from db import initialise_database
from ui.login import open_login_page


def main(): # initialise the database and open the login page

    initialise_database()

    open_login_page()


if __name__ == "__main__":
    main()
