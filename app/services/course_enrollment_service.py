from sqlmodel import Session, select
from app.models.course_enrollment import CourseEnrollment
from app.models.person import Person
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.models.inspector import Inspector 
from app.models.judge import Judge 
from app.schemas.course_enrollment_schema import CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdateStatus
from datetime import date, timedelta
from typing import List, Optional

# Definición de las transiciones de estado permitidas
ALLOWED_STATUS_TRANSITIONS = {
    "pending": ["completed", "used", "expired", "incomplete"],
    "completed": ["used"], 
    "used": [], 
    "expired": [], 
    "incomplete": ["completed", "used"] 
}

def _get_calculated_enrollment_read(enrollment: CourseEnrollment, session: Session) -> Optional[CourseEnrollmentRead]:
    """Helper function to create a CourseEnrollmentRead object with calculated fields."""
    person = session.get(Person, enrollment.person_id)
    course = session.get(TrafficSafetyCourse, enrollment.course_id)

    if not person or not course:
        return None 

    today = date.today()
    
    current_calculated_status = enrollment.status
    if enrollment.status == "pending":
        if today > enrollment.expiration_date:
            current_calculated_status = "expired"
        elif today > enrollment.deadline_date:
            current_calculated_status = "incomplete"
    

    days_until_deadline = (enrollment.deadline_date - today).days
    days_until_expiration = (enrollment.expiration_date - today).days

    return CourseEnrollmentRead(
        id=enrollment.id,
        person_id=enrollment.person_id,
        person_name=person.name,
        person_dni=person.dni,
        course_id=enrollment.course_id,
        course_name=course.name,
        course_description=course.description,
        enrollment_date=enrollment.enrollment_date,
        deadline_date=enrollment.deadline_date,
        expiration_date=enrollment.expiration_date,
        status=enrollment.status,
        inspector_id=enrollment.inspector_id,
        judge_id=enrollment.judge_id,
        current_calculated_status=current_calculated_status,
        days_until_deadline=days_until_deadline,
        days_until_expiration=days_until_expiration
    )

def create_enrollment(enrollment_data: CourseEnrollmentCreate, session: Session) -> Optional[CourseEnrollmentRead]:
    person = session.get(Person, enrollment_data.person_id)
    course = session.get(TrafficSafetyCourse, enrollment_data.course_id)

    if not person:
        raise ValueError(f"Person with ID {enrollment_data.person_id} not found.")
    if not course:
        raise ValueError(f"Course with ID {enrollment_data.course_id} not found.")

    today = date.today()
    
    enrollment_db = CourseEnrollment(
        person_id=enrollment_data.person_id,
        course_id=enrollment_data.course_id,
        enrollment_date=today,
        deadline_date=today + timedelta(days=60),
        expiration_date=today + timedelta(days=180), 
        status="pending" 
    )
    
    session.add(enrollment_db)
    session.commit()
    session.refresh(enrollment_db)
    return _get_calculated_enrollment_read(enrollment_db, session)

def get_enrollment_by_id(enrollment_id: int, session: Session) -> Optional[CourseEnrollmentRead]:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None
    return _get_calculated_enrollment_read(enrollment, session)

def get_all_enrollments(session: Session) -> List[CourseEnrollmentRead]:
    enrollments_db = session.exec(select(CourseEnrollment)).all()
    
    enrollments_read_list = []
    for enrollment in enrollments_db:
        read_obj = _get_calculated_enrollment_read(enrollment, session)
        if read_obj:
            enrollments_read_list.append(read_obj)
    return enrollments_read_list

def update_enrollment_status(
    enrollment_id: int, 
    status_update_data: CourseEnrollmentUpdateStatus, 
    session: Session
) -> Optional[CourseEnrollmentRead]:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None 

    old_status = enrollment.status
    new_status = status_update_data.status

    # Validar la transición de estado
    if new_status not in ALLOWED_STATUS_TRANSITIONS.get(old_status, []):
        raise ValueError(f"Invalid status transition from '{old_status}' to '{new_status}'.")


    if new_status == "used":
        inspector_id = status_update_data.inspector_id
        judge_id = status_update_data.judge_id

        if not inspector_id and not judge_id:
            raise ValueError("For status 'used', either 'inspector_id' or 'judge_id' must be provided.")
        
      
        if inspector_id:
            inspector = session.get(Inspector, inspector_id)
            if not inspector:
                raise ValueError(f"Inspector with ID {inspector_id} not found.")
        if judge_id:
            judge = session.get(Judge, judge_id)
            if not judge:
                raise ValueError(f"Judge with ID {judge_id} not found.")

       
        enrollment.inspector_id = inspector_id
        enrollment.judge_id = judge_id

    
    if new_status != "used":
        enrollment.inspector_id = None
        enrollment.judge_id = None


    enrollment.status = new_status
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return _get_calculated_enrollment_read(enrollment, session)

def delete_enrollment(enrollment_id: int, session: Session) -> bool:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return False
    session.delete(enrollment)
    session.commit()
    return True