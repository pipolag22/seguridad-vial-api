from sqlmodel import Session, select
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.schemas.traffic_safety_course_schema import TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate
from typing import List, Optional

def create_course(course_data: TrafficSafetyCourseCreate, session: Session) -> TrafficSafetyCourseRead:
    db_course = TrafficSafetyCourse.model_validate(course_data)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return TrafficSafetyCourseRead.model_validate(db_course)

def get_all_courses(session: Session) -> List[TrafficSafetyCourseRead]:
    courses = session.exec(select(TrafficSafetyCourse)).all()
    return [TrafficSafetyCourseRead.model_validate(c) for c in courses]

def get_course_by_id(course_id: int, session: Session) -> Optional[TrafficSafetyCourseRead]:
    course = session.get(TrafficSafetyCourse, course_id)
    if course:
        return TrafficSafetyCourseRead.model_validate(course)
    return None

def update_course(course_id: int, course_data: TrafficSafetyCourseUpdate, session: Session) -> Optional[TrafficSafetyCourseRead]:
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        return None

    update_data = course_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    session.add(course)
    session.commit()
    session.refresh(course)
    return TrafficSafetyCourseRead.model_validate(course)

def delete_course(course_id: int, session: Session) -> bool:
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        return False
    session.delete(course)
    session.commit()
    return True