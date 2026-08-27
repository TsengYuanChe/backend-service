from getpass import getpass

from sqlalchemy import insert

from app.database import engine
from app.models.user import User
from app.core.security import hash_password


def main():
    name = input("Name: ")
    account_name = input("Account name: ")
    password = getpass("Password: ")

    hashed_password = hash_password(password)

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(
                name=name,
                account_name=account_name,
                password_hash=hashed_password,
                is_active=True,
            )
        )

    print("User created.")


if __name__ == "__main__":
    main()