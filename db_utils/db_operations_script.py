import json
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models.models import (EligibilityCriteria, Ladder, LinkedInProfileInfo,
                           Position, User)


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


def migrate_enterprise_admin_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).all()
        for user in users:
            if user.is_enterprise_admin is None:
                user.is_enterprise_admin = False
                if user.is_manager:
                    user.is_manager = False
                    print(f"User {user.id} was a manager, now set as enterprise admin.")
                else:
                    print(f"User {user.id} set as non-enterprise admin.")

        session.commit()
        print("Enterprise admin data migrated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while migrating enterprise admin data: {str(e)}")
    finally:
        session.close()


def migrate_linkedin_skills(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        linkedin_infos = session.query(LinkedInProfileInfo).all()

        for linkedin_info in linkedin_infos:
            if linkedin_info.scraped_info:
                try:
                    profile_data = json.loads(linkedin_info.scraped_info)
                    skills = profile_data.get("skills", [])

                    user = (
                        session.query(User).filter_by(id=linkedin_info.user_id).first()
                    )

                    if user:
                        skills_dict = {
                            skill: 3 for skill in skills
                        }  # Set default proficiency to 3
                        user.set_skills(skills_dict)
                        print(f"Updated skills for user {user.id}: {user.get_skills()}")
                    else:
                        print(f"No user found for LinkedIn info {linkedin_info.id}")
                except json.JSONDecodeError:
                    print(
                        f"Error decoding LinkedIn info for user {linkedin_info.user_id}"
                    )

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


def migrate_resume_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).all()
        for user in users:
            if user.resume_pdf and os.path.isfile(user.resume_pdf):
                with open(user.resume_pdf, "rb") as file:
                    pdf_data = file.read()
                    user.resume_pdf = pdf_data
                os.remove(user.resume_pdf)  # Remove the file after migrating
            elif user.resume_pdf:
                user.resume_pdf = None  # Clear invalid file paths

        session.commit()
        print("Resume data migrated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while migrating resume data: {str(e)}")
    finally:
        session.close()


def populate_default_ladders_and_positions(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Default ladders and positions from work_profile.py
        default_ladders = {
            "Individual Contributor (Software)": {
                "prefix": "IC",
                "positions": [
                    "Software Engineer",
                    "Sr Software Engineer",
                    "Staff Software Engineer",
                    "Sr Staff Software Engineer",
                    "Principal Engineer",
                    "Distinguished Engineer",
                    "Fellow",
                ],
            },
            "Management": {
                "prefix": "M",
                "positions": [
                    "Manager",
                    "Sr Manager",
                    "Director",
                    "Sr Director",
                    "Vice President",
                    "Sr Vice President",
                    "Executive Vice President",
                ],
            },
            "Product": {
                "prefix": "PM",
                "positions": [
                    "Product Manager",
                    "Sr Product Manager",
                    "Group Product Manager",
                    "Vice President",
                    "Sr Vice President",
                ],
            },
        }

        for ladder_name, ladder_data in default_ladders.items():
            ladder = session.query(Ladder).filter_by(name=ladder_name).first()
            if not ladder:
                ladder = Ladder(name=ladder_name, prefix=ladder_data["prefix"])
                session.add(ladder)
                session.flush()

            existing_positions = (
                session.query(Position).filter_by(ladder_id=ladder.id).all()
            )
            existing_position_names = [p.name for p in existing_positions]

            for level, position_name in enumerate(ladder_data["positions"], start=1):
                if position_name not in existing_position_names:
                    position = Position(
                        name=position_name, level=level, ladder_id=ladder.id
                    )
                    session.add(position)

        session.commit()
        print("Default ladders and positions populated successfully.")
    except Exception as e:
        session.rollback()
        print(
            f"An error occurred while populating default ladders and positions: {str(e)}"
        )
    finally:
        session.close()


def update_schema(engine):
    with engine.connect() as conn:
        try:
            # Check if new tables exist
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]

            if "ladders" not in tables:
                conn.execute(
                    text(
                        """
                    CREATE TABLE ladders (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        prefix TEXT NOT NULL
                    )
                """
                    )
                )
                print("Ladders table created successfully.")

            if "positions" not in tables:
                conn.execute(
                    text(
                        """
                    CREATE TABLE positions (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        level INTEGER NOT NULL,
                        ladder_id INTEGER NOT NULL,
                        FOREIGN KEY (ladder_id) REFERENCES ladders (id)
                    )
                """
                    )
                )
                print("Positions table created successfully.")

            if "eligibility_criteria" not in tables:
                conn.execute(
                    text(
                        """
                    CREATE TABLE eligibility_criteria (
                        id INTEGER PRIMARY KEY,
                        position_id INTEGER NOT NULL,
                        criteria TEXT NOT NULL,
                        FOREIGN KEY (position_id) REFERENCES positions (id)
                    )
                """
                    )
                )
                print("Eligibility criteria table created successfully.")

            # Check if position_id column exists in users table
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if "position_id" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN position_id INTEGER REFERENCES positions(id)"
                    )
                )
                print("position_id column added to users table successfully.")

            conn.commit()
            print("Schema updated successfully.")

            # Populate default ladders and positions
            populate_default_ladders_and_positions(engine)

        except Exception as e:
            print(f"An error occurred while updating the schema: {str(e)}")


def migrate_profile_image(engine):
    with engine.connect() as conn:
        try:
            # Check if profile_image column exists in users table
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if "profile_image" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_image BLOB"))
                print("profile_image column added to users table successfully.")
            else:
                print("profile_image column already exists in users table.")

            conn.commit()
        except Exception as e:
            print(f"An error occurred while migrating profile image: {str(e)}")


def migrate_eligibility_criteria(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if the criteria_text column exists
        result = session.execute(text("PRAGMA table_info(eligibility_criteria)"))
        columns = [row[1] for row in result.fetchall()]

        if "criteria_text" not in columns:
            # Add the new column
            session.execute(
                text("ALTER TABLE eligibility_criteria ADD COLUMN criteria_text TEXT")
            )

            # Migrate existing data
            criteria_records = session.query(EligibilityCriteria).all()
            for record in criteria_records:
                if isinstance(record.criteria, dict):
                    # Convert the existing JSON criteria to text
                    criteria_text = json.dumps(record.criteria)
                    record.criteria_text = criteria_text

            # Remove the old column (SQLite doesn't support dropping columns, so we need to recreate the table)
            session.execute(
                text(
                    """
                CREATE TABLE eligibility_criteria_new (
                    id INTEGER PRIMARY KEY,
                    position_id INTEGER NOT NULL,
                    criteria_text TEXT NOT NULL,
                    FOREIGN KEY (position_id) REFERENCES positions (id)
                )
            """
                )
            )
            session.execute(
                text(
                    """
                INSERT INTO eligibility_criteria_new (id, position_id, criteria_text)
                SELECT id, position_id, criteria_text FROM eligibility_criteria
            """
                )
            )
            session.execute(text("DROP TABLE eligibility_criteria"))
            session.execute(
                text(
                    "ALTER TABLE eligibility_criteria_new RENAME TO eligibility_criteria"
                )
            )

        session.commit()
        print("Eligibility criteria migrated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while migrating eligibility criteria: {str(e)}")
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
        print("6. Migrate resume data")
        print("7. Migrate enterprise admin data")
        print("8. Populate default ladders and positions")
        print("9. Migrate profile image")
        print("10. Migrate eligibility criteria")
        print("11. Exit")

        choice = input("Enter your choice (1-11): ")

        if choice == "1":
            update_schema(engine)
        elif choice == "2":
            migrate_linkedin_skills(engine)
        elif choice == "3":
            update_existing_skills(engine)
        elif choice == "4":
            migrate_work_profile_data(engine)
        elif choice == "5":
            confirm = input(
                "Are you sure you want to truncate the database? This will delete all user data. (y/n): "
            )
            if confirm.lower() == "y":
                truncate_database(engine)
            else:
                print("Operation cancelled.")
        elif choice == "6":
            migrate_resume_data(engine)
        elif choice == "7":
            migrate_enterprise_admin_data(engine)
        elif choice == "8":
            populate_default_ladders_and_positions(engine)
        elif choice == "9":
            migrate_profile_image(engine)
        elif choice == "10":
            migrate_eligibility_criteria(engine)
        elif choice == "11":
            break
        else:
            print("Invalid choice. Please try again.")

    print("Exiting the program.")
