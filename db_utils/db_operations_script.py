import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import Base, User  # Import User and Base from main.py


def get_db_path():
    while True:
        db_path = input(
            "Enter the path to users.db (or press Enter for default './users.db'): "
        ).strip()
        if not db_path:
            db_path = "./users.db"

        if os.path.isfile(db_path):
            return db_path
        elif os.path.isdir(os.path.dirname(db_path)):
            return db_path
        else:
            print(
                f"The directory {os.path.dirname(db_path)} does not exist. Please enter a valid path."
            )


def create_engine_with_path(db_path):
    return create_engine(f"sqlite:///{db_path}")


def update_schema(engine):
    with engine.connect() as conn:
        try:
            # Use text() to create SQL expressions
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN first_name VARCHAR NOT NULL DEFAULT ''"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN last_name VARCHAR NOT NULL DEFAULT ''"
                )
            )
            conn.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
            conn.commit()
            print("Schema updated successfully.")
        except Exception as e:
            print(f"An error occurred while updating the schema: {str(e)}")
            print("If the columns already exist, you can ignore this error.")


def truncate_database(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Delete all records from the users table
        session.query(User).delete()
        session.commit()
        print("All data in the users table has been deleted.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while truncating the database: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    db_path = get_db_path()
    engine = create_engine_with_path(db_path)

    while True:
        print("\nDatabase Operations:")
        print("1. Update schema")
        print("2. Truncate database")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            update_schema(engine)
        elif choice == "2":
            confirm = input(
                "Are you sure you want to truncate the database? This will delete all user data. (y/n): "
            )
            if confirm.lower() == "y":
                truncate_database(engine)
            else:
                print("Operation cancelled.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

    print("Exiting the program.")
