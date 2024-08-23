import json
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models.models import User, LinkedInProfileInfo


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
            # Check if new columns exist
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            new_columns = {
                'ladder': 'TEXT',
                'current_position': 'TEXT',
                'responsibilities': 'TEXT',
                'resume_pdf': 'TEXT'
            }

            for column, data_type in new_columns.items():
                if column not in columns:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column} {data_type}"))
                    print(f"{column} column added successfully.")

            if 'skills' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN skills TEXT DEFAULT '{}'"))
                print("Skills column added successfully.")
            else:
                conn.execute(text("ALTER TABLE users ALTER COLUMN skills TYPE TEXT"))
                print("Skills column type updated to TEXT.")

            conn.commit()
            print("Schema updated successfully.")
        except Exception as e:
            print(f"An error occurred while updating the schema: {str(e)}")


def migrate_linkedin_skills(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        linkedin_infos = session.query(LinkedInProfileInfo).all()

        for linkedin_info in linkedin_infos:
            if linkedin_info.scraped_info:
                try:
                    profile_data = json.loads(linkedin_info.scraped_info)
                    skills = profile_data.get('skills', [])

                    user = session.query(User).filter_by(id=linkedin_info.user_id).first()

                    if user:
                        skills_dict = {skill: 3 for skill in skills}  # Set default proficiency to 3
                        user.set_skills(skills_dict)
                        print(f"Updated skills for user {user.id}: {user.get_skills()}")
                    else:
                        print(f"No user found for LinkedIn info {linkedin_info.id}")
                except json.JSONDecodeError:
                    print(f"Error decoding LinkedIn info for user {linkedin_info.user_id}")

        session.commit()
        print("LinkedIn skills migrated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while migrating LinkedIn skills: {str(e)}")
    finally:
        session.close()


def update_existing_skills(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).all()
        for user in users:
            skills = user.get_skills()
            if skills:
                # Ensure all skills have integer proficiency
                updated_skills = {k: int(v) for k, v in skills.items()}
                user.set_skills(updated_skills)
            else:
                user.set_skills({})

        session.commit()
        print("Existing skills updated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while updating existing skills: {str(e)}")
    finally:
        session.close()


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

def migrate_work_profile_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).all()
        for user in users:
            # Here you would typically migrate data from an old structure to the new one
            # For this example, we'll just set some default values
            user.ladder = user.ladder or "Not specified"
            user.current_position = user.current_position or "Not specified"
            user.responsibilities = user.responsibilities or "Not specified"
            # We can't set a default for resume_pdf as it's a file path

        session.commit()
        print("Work profile data migrated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while migrating work profile data: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    db_path = get_db_path()
    engine = create_engine_with_path(db_path)

    while True:
        print("\nDatabase Operations:")
        print("1. Update schema")
        print("2. Migrate LinkedIn skills")
        print("3. Update existing skills")
        print("4. Migrate work profile data")
        print("5. Truncate database")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            update_schema(engine)
        elif choice == "2":
            migrate_linkedin_skills(engine)
        elif choice == "3":
            update_existing_skills(engine)
        elif choice == "4":
            migrate_work_profile_data(engine)
        elif choice == "5":
            confirm = input("Are you sure you want to truncate the database? This will delete all user data. (y/n): ")
            if confirm.lower() == "y":
                truncate_database(engine)
            else:
                print("Operation cancelled.")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")

    print("Exiting the program.")
