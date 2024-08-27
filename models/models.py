import json
import re as regex
from datetime import datetime
from io import BytesIO

import bcrypt
import streamlit as st
from PIL import Image
from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        LargeBinary, String, create_engine, inspect)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from helpers.linkedin import get_linkedin_profile_json

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_manager = Column(Boolean, default=False)
    is_enterprise_admin = Column(Boolean, default=False)
    linkedin_profile = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    skills = Column(String, default="{}")
    ladder = Column(String)
    current_position = Column(String)
    responsibilities = Column(String)
    resume_pdf = Column(LargeBinary)
    position_id = Column(Integer, ForeignKey("positions.id"))
    position = relationship("Position")
    profile_image = Column(LargeBinary)  # New field for profile image

    def get_skills(self):
        return json.loads(self.skills)

    def set_skills(self, skills_dict):
        self.skills = json.dumps(skills_dict)

    def set_profile_image(self, image_file):
        img = Image.open(image_file)
        img = img.convert("RGB")
        img.thumbnail((150, 150))
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        self.profile_image = buffer.getvalue()

    def get_profile_image(self):
        if self.profile_image:
            return Image.open(BytesIO(self.profile_image))
        return None


class Ladder(Base):
    __tablename__ = "ladders"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    prefix = Column(String, nullable=False)
    positions = relationship(
        "Position", back_populates="ladder", cascade="all, delete-orphan"
    )


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    ladder_id = Column(Integer, ForeignKey("ladders.id"), nullable=False)
    ladder = relationship("Ladder", back_populates="positions")
    eligibility_criteria = relationship(
        "EligibilityCriteria", back_populates="position", cascade="all, delete-orphan"
    )


class EligibilityCriteria(Base):
    __tablename__ = "eligibility_criteria"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    position = relationship("Position", back_populates="eligibility_criteria")
    criteria_text = Column(String, nullable=False)


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_current_password(user_id, provided_password):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    if user:
        return bcrypt.checkpw(provided_password.encode("utf-8"), user.password)
    return False


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)


def register_user(
    email,
    password,
    is_manager,
    is_enterprise_admin,
    linkedin_profile,
    first_name,
    last_name,
    address,
    phone,
    profile_image=None,
):
    session = Session()
    hashed_password = hash_password(password)
    new_user = User(
        email=email,
        password=hashed_password,
        is_manager=is_manager,
        is_enterprise_admin=is_enterprise_admin,
        linkedin_profile=linkedin_profile,
        first_name=first_name,
        last_name=last_name,
        address=address,
        phone=phone,
    )
    if profile_image:
        new_user.set_profile_image(profile_image)
    session.add(new_user)
    session.flush()  # This will assign an id to new_user

    if linkedin_profile:
        scraped_info = get_linkedin_profile_json(linkedin_profile)
        linkedin_info = LinkedInProfileInfo(
            user_id=new_user.id,
            linkedin_profile_url=linkedin_profile,
            scraped_info=json.dumps(scraped_info),
        )
        session.add(linkedin_info)

    session.commit()
    session.close()


def verify_login(email, password):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    if user and verify_password(user.password, password):
        return user
    return None


def check_password_match(password_key, confirm_password_key, error_key):
    if password_key in st.session_state and confirm_password_key in st.session_state:
        if st.session_state[password_key] != st.session_state[confirm_password_key]:
            st.session_state[error_key] = "Passwords do not match."
        else:
            st.session_state[error_key] = ""


def update_user_profile(user_id, **kwargs):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        changed = False
        for key, value in kwargs.items():
            if hasattr(user, key):
                if key == "profile_image":
                    user.set_profile_image(value)
                    changed = True
                elif key == "skills":
                    # Convert the skills string to a dictionary if it's not already
                    current_skills = json.loads(user.skills) if user.skills else {}
                    # Update the skills dictionary
                    for skill in value:
                        current_skills[skill] = current_skills.get(skill, 3)
                    # Convert the updated skills dictionary back to a JSON string
                    user.skills = json.dumps(current_skills)
                    changed = True
                elif getattr(user, key) != value:
                    setattr(user, key, value)
                    changed = True

                if key == "linkedin_profile":
                    linkedin_info = (
                        session.query(LinkedInProfileInfo)
                        .filter_by(user_id=user.id)
                        .first()
                    )
                    if linkedin_info:
                        linkedin_info.linkedin_profile_url = value
                        scraped_info = get_linkedin_profile_json(value)
                        linkedin_info.scraped_info = json.dumps(scraped_info)
                        linkedin_info.last_updated = datetime.utcnow()
                    else:
                        scraped_info = get_linkedin_profile_json(value)
                        new_linkedin_info = LinkedInProfileInfo(
                            user_id=user.id,
                            linkedin_profile_url=value,
                            scraped_info=json.dumps(scraped_info),
                        )
                        session.add(new_linkedin_info)

                    # Update user's skills
                    skills = scraped_info.get("skills", [])
                    current_skills = json.loads(user.skills) if user.skills else {}
                    for skill in skills:
                        current_skills[skill] = current_skills.get(skill, 3)
                    user.skills = json.dumps(current_skills)
                    changed = True

        if changed:
            session.commit()
            session.refresh(user)
            session.close()
            return user
    session.close()
    return None


def get_user_by_id(user_id):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return user


def change_user_password(user_id, new_password):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.password = hash_password(new_password)
        session.commit()
        session.close()
        return True
    session.close()
    return False


def is_password_valid(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    # Check if password contains at least one number
    if not regex.search(r"\d", password):
        return False
    # Check if password contains at least one symbol
    if not regex.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


class LinkedInProfileInfo(Base):
    __tablename__ = "linkedin_profile_info"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    linkedin_profile_url = Column(String, nullable=False)
    scraped_info = Column(String)  # This will store the JSON string of the scraped info
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="linkedin_info")

    def extract_endorsements(self):
        if not self.scraped_info:
            return []

        try:
            scraped_info = json.loads(self.scraped_info)
        except json.JSONDecodeError:
            return []

        endorsements = []
        recommendations = scraped_info.get("recommendations", [])

        for recommendation in recommendations:
            endorser = recommendation.get("name", "Unknown")
            text = recommendation.get("text", "")
            if endorser and text:
                endorsements.append({"endorser": endorser, "text": text})

        return endorsements

    @classmethod
    def get_user_linkedin_info(cls, user_id):
        session = Session()
        try:
            linkedin_info = session.query(cls).filter_by(user_id=user_id).first()
            if linkedin_info:
                return linkedin_info
            return None
        finally:
            session.close()

    @classmethod
    def display_endorsements(cls, user_id):
        linkedin_info = cls.get_user_linkedin_info(user_id)
        if linkedin_info:
            return linkedin_info.extract_endorsements()
        return []


User.linkedin_info = relationship(
    "LinkedInProfileInfo", uselist=False, back_populates="user"
)


def get_user_skills(user_id):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return user.get_skills() if user else {}


def update_user_skills(user_id, skills):
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.set_skills(skills)
        session.commit()
        session.close()
        return True
    session.close()
    return False


def update_work_profile(user_id, **kwargs):
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            for key, value in kwargs.items():
                if key == "resume_pdf":
                    # If resume_pdf is provided, it should be the binary data of the PDF
                    setattr(user, key, value)
                else:
                    setattr(user, key, value)
            session.commit()
            session.refresh(user)
            return user
        return None
    except Exception as e:
        session.rollback()
        print(f"Error updating work profile: {str(e)}")
        return None
    finally:
        session.close()


def delete_resume(user_id):
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.resume_pdf = None
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting resume: {str(e)}")
        return False
    finally:
        session.close()


engine = create_engine("sqlite:///users.db", echo=True)


def create_tables_if_not_exist(engine):
    if not inspect(engine).has_table(User.__tablename__):
        User.__table__.create(engine)
    if not inspect(engine).has_table(LinkedInProfileInfo.__tablename__):
        LinkedInProfileInfo.__table__.create(engine)
    if not inspect(engine).has_table(Ladder.__tablename__):
        Ladder.__table__.create(engine)
    if not inspect(engine).has_table(Position.__tablename__):
        Position.__table__.create(engine)
    if not inspect(engine).has_table(EligibilityCriteria.__tablename__):
        EligibilityCriteria.__table__.create(engine)


# Add functions to interact with new models
def get_all_ladders():
    session = Session()
    ladders = session.query(Ladder).all()
    session.close()
    return ladders


def get_positions_for_ladder(ladder_id):
    session = Session()
    positions = (
        session.query(Position)
        .filter_by(ladder_id=ladder_id)
        .order_by(Position.level)
        .all()
    )
    position_dicts = [{"id": p.id, "name": p.name, "level": p.level} for p in positions]
    session.close()
    return position_dicts


def update_ladder_positions(ladder_id, positions):
    session = Session()
    try:
        ladder = session.query(Ladder).filter_by(id=ladder_id).first()
        if ladder:
            # Delete existing positions
            session.query(Position).filter_by(ladder_id=ladder_id).delete()

            # Add new positions
            for position in positions:
                new_position = Position(
                    name=position["name"], level=position["level"], ladder_id=ladder_id
                )
                session.add(new_position)

            session.commit()
            return True
    except Exception as e:
        session.rollback()
        print(f"Error updating ladder positions: {str(e)}")
        return False
    finally:
        session.close()


def get_eligibility_criteria(position_id):
    session = Session()
    criteria = (
        session.query(EligibilityCriteria).filter_by(position_id=position_id).first()
    )
    session.close()
    return criteria.criteria_text if criteria else None


def update_eligibility_criteria(position_id, criteria_text):
    session = Session()
    try:
        criteria = (
            session.query(EligibilityCriteria)
            .filter_by(position_id=position_id)
            .first()
        )
        if criteria:
            criteria.criteria_text = criteria_text
        else:
            new_criteria = EligibilityCriteria(
                position_id=position_id, criteria_text=criteria_text
            )
            session.add(new_criteria)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error updating eligibility criteria: {str(e)}")
        return False
    finally:
        session.close()


Session = sessionmaker(bind=engine)
