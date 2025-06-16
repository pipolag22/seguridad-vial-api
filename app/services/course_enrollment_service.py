from sqlmodel import Session, select, func
from typing import List, Dict, Any, Optional
from datetime import date, timedelta


from app.models import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdate
from app.models import Person, TrafficSafetyCourse 
from app.models.course_enrollment import CourseEnrollmentReportItem, CourseEnrollmentStatus



def create_course_enrollment(enrollment_create: CourseEnrollmentCreate, session: Session) -> CourseEnrollment:
    enrollment_data = enrollment_create.model_dump() 

    if enrollment_data.get("expiration_date") is None:
        
        enrollment_data["expiration_date"] = enrollment_create.enrollment_date + timedelta(days=90)
    
  
    if enrollment_data.get("status") is None:
        enrollment_data["status"] = CourseEnrollmentStatus.PENDING

    enrollment = CourseEnrollment.model_validate(enrollment_data)
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment


def get_course_enrollment_by_id(enrollment_id: int, session: Session) -> CourseEnrollmentRead | None:
    statement = select(CourseEnrollment).where(CourseEnrollment.id == enrollment_id)
    enrollment = session.exec(statement).first()
    if enrollment:
        enrollment_read = CourseEnrollmentRead.model_validate(enrollment)
        return enrollment_read
    return None


def get_all_course_enrollments(session: Session) -> List[CourseEnrollmentRead]:
    
    statement = select(CourseEnrollment)
    enrollments = session.exec(statement).all()
    return [CourseEnrollmentRead.model_validate(e) for e in enrollments]


def update_course_enrollment(enrollment_id: int, enrollment_update: Dict[str, Any], session: Session) -> CourseEnrollmentRead | None:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None

    updated_data = enrollment_update
    for key, value in updated_data.items():
        setattr(enrollment, key, value)

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
  
    return CourseEnrollmentRead.model_validate(enrollment)


def delete_course_enrollment(enrollment_id: int, session: Session) -> bool:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return False
    session.delete(enrollment)
    session.commit()
    return True




def mark_enrollment_as_completed(enrollment_id: int, session: Session) -> CourseEnrollmentRead | None:
    """
    Marca una inscripción como completada y calcula la nueva fecha de vencimiento
    post-finalización (regla de los 60 días).
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None

    if enrollment.status == CourseEnrollmentStatus.COMPLETED:
        return CourseEnrollmentRead.model_validate(enrollment)

    enrollment.completion_date = date.today()
    enrollment.status = CourseEnrollmentStatus.COMPLETED
    

    enrollment.expiration_date = enrollment.completion_date + timedelta(days=60)

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return CourseEnrollmentRead.model_validate(enrollment)


def mark_enrollment_as_expired_by_action(enrollment_id: int, session: Session) -> CourseEnrollmentRead | None:
    """
    Marca una inscripción como expirada directamente por acción de un inspector/juez.
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None
    
    if enrollment.status == CourseEnrollmentStatus.EXPIRED:
        return CourseEnrollmentRead.model_validate(enrollment) # Ya está expirado

    enrollment.status = CourseEnrollmentStatus.EXPIRED
    enrollment.expiration_date = date.today() # La hace expirar desde hoy
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return CourseEnrollmentRead.model_validate(enrollment)


def get_expiring_or_expired_enrollments_report(
    session: Session,
    days_until_expiration: int = 30
) -> List[CourseEnrollmentReportItem]:
    """
    Genera un reporte de inscripciones a cursos que están próximas a vencer
    o que ya han vencido. Incluye detalles de la persona y el curso asociado.
    """
    today = date.today()
    expiring_soon_date = today + timedelta(days=days_until_expiration)

    statement = select(CourseEnrollment, Person, TrafficSafetyCourse).join(
        Person, CourseEnrollment.person_id == Person.id
    ).join(
        TrafficSafetyCourse, CourseEnrollment.course_id == TrafficSafetyCourse.id
    ).where(
        
        (CourseEnrollment.expiration_date <= expiring_soon_date)
        (CourseEnrollment.expiration_date <= expiring_soon_date)
    & (CourseEnrollment.status.notin_([CourseEnrollmentStatus.COMPLETED, CourseEnrollmentStatus.CANCELED]))
    )

    results = session.exec(statement).all()

    report_items = []
    for enrollment, person, course in results:
        person_read_item = PersonRead.model_validate(person)
        course_read_item = TrafficSafetyCourseRead.model_validate(course)

        days_diff = (enrollment.expiration_date - today).days
        is_expired = enrollment.expiration_date < today
        
        report_item = CourseEnrollmentReportItem(
            id=enrollment.id,
            enrollment_date=enrollment.enrollment_date,
            completion_date=enrollment.completion_date,
            expiration_date=enrollment.expiration_date,
            status=enrollment.status,
            notes=enrollment.notes,
            person=person_read_item,
            course=course_read_item,
            days_until_expiration=days_diff,
            is_expired=is_expired
        )
        report_items.append(report_item)

    return report_items