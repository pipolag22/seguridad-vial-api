from sqlmodel import Session, select
from app.models.course_enrollment import CourseEnrollment, CourseEnrollmentStatus 
from app.models.person import Person
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.models.inspector import Inspector
from app.models.judge import Judge
from app.models.user import User, UserRole 
from app.schemas.course_enrollment_schema import CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdateStatus
from datetime import date, timedelta
from typing import List, Optional
from fastapi import HTTPException, status 


ALLOWED_STATUS_TRANSITIONS = {
    CourseEnrollmentStatus.PENDING: [CourseEnrollmentStatus.COMPLETED, CourseEnrollmentStatus.USED],
    CourseEnrollmentStatus.COMPLETED: [CourseEnrollmentStatus.USED],
    CourseEnrollmentStatus.INCOMPLETE: [CourseEnrollmentStatus.COMPLETED, CourseEnrollmentStatus.USED], # Si un curso fue incompleto, aún se puede completar o usar
    CourseEnrollmentStatus.USED: [], # Una vez usado, no cambia de estado
    CourseEnrollmentStatus.EXPIRED: [], # Un curso expirado no puede cambiar a otro estado directamente
}

def _get_calculated_enrollment_read(enrollment: CourseEnrollment, session: Session) -> Optional[CourseEnrollmentRead]:
    """
    Función auxiliar para crear un objeto CourseEnrollmentRead con campos calculados
    y datos desnormalizados de Person y TrafficSafetyCourse.
    """
    # Usar .person y .course que vienen de las relaciones
    person = enrollment.person 
    course = enrollment.course

    if not person or not course:
        return None 

    today = date.today()

    # Calcular el estado actual en tiempo real 
    current_calculated_status = enrollment.status
    if enrollment.status == CourseEnrollmentStatus.PENDING:
        if today > enrollment.expiration_date: # Si ya pasó la fecha de expiración inicial (que es la deadline)
            current_calculated_status = CourseEnrollmentStatus.EXPIRED
        elif today > enrollment.deadline_date: # Si pasó la fecha límite pero aún no la de expiración
            current_calculated_status = CourseEnrollmentStatus.INCOMPLETE
    elif enrollment.status == CourseEnrollmentStatus.COMPLETED:
        if today > enrollment.expiration_date: # Si ya pasó la fecha de expiración después de completar
            current_calculated_status = CourseEnrollmentStatus.EXPIRED
    
    # Calcular días restantes
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
        completion_date=enrollment.completion_date,
        deadline_date=enrollment.deadline_date,
        expiration_date=enrollment.expiration_date,
        status=enrollment.status, # El estado guardado en DB
        inspector_id=enrollment.inspector_id,
        judge_id=enrollment.judge_id,
        current_calculated_status=current_calculated_status, # El estado dinámico/calculado
        days_until_deadline=days_until_deadline,
        days_until_expiration=days_until_expiration
    )

def create_enrollment(enrollment_data: CourseEnrollmentCreate, session: Session) -> CourseEnrollmentRead:
    person = session.get(Person, enrollment_data.person_id)
    course = session.get(TrafficSafetyCourse, enrollment_data.course_id)

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with ID {enrollment_data.person_id} not found.")
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with ID {enrollment_data.course_id} not found.")

    today = date.today()
    
    enrollment_db = CourseEnrollment(
        person_id=enrollment_data.person_id,
        course_id=enrollment_data.course_id,
        enrollment_date=today,
        deadline_date=today + timedelta(days=60), # 2 meses para completar
        expiration_date=today + timedelta(days=60), # Inicialmente, la expiración coincide con la deadline si no se completa
        status=CourseEnrollmentStatus.PENDING # Siempre empieza como pendiente
    )
    
    session.add(enrollment_db)
    session.commit()
    session.refresh(enrollment_db)

    
    enrollment_with_relations = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment_db.id)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).first()
    
    return _get_calculated_enrollment_read(enrollment_with_relations, session)

def get_enrollment_by_id(enrollment_id: int, session: Session) -> Optional[CourseEnrollmentRead]:
  
    enrollment = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment_id)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).first()
    if not enrollment:
        return None
    return _get_calculated_enrollment_read(enrollment, session)

def get_all_enrollments(session: Session) -> List[CourseEnrollmentRead]:

    enrollments_db = session.exec(
        select(CourseEnrollment)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).all()
    
    enrollments_read_list = []
    for enrollment in enrollments_db:
        read_obj = _get_calculated_enrollment_read(enrollment, session)
        if read_obj:
            enrollments_read_list.append(read_obj)
    return enrollments_read_list

def get_enrollments_by_person_dni(dni: str, session: Session) -> List[CourseEnrollmentRead]:
   
    person = session.exec(select(Person).where(Person.dni == dni)).first()
    if not person:
     
        return [] 
    
    
    enrollments_db = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.person_id == person.id)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).all()
    
    enrollments_read_list = []
    for enrollment in enrollments_db:
        read_obj = _get_calculated_enrollment_read(enrollment, session)
        if read_obj:
            enrollments_read_list.append(read_obj)
    return enrollments_read_list


def update_enrollment_status(
    enrollment_id: int, 
    status_update_data: CourseEnrollmentUpdateStatus, 
    session: Session,
    current_user: User # Este parámetro es CRÍTICO para la autorización
) -> CourseEnrollmentRead:
    # Cargar la inscripción con sus relaciones para la lógica y la respuesta
    enrollment = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment_id)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).first()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course Enrollment not found") 

    old_status = enrollment.status
    new_status = status_update_data.status


    if new_status not in ALLOWED_STATUS_TRANSITIONS.get(old_status, []):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status transition from '{old_status.value}' to '{new_status.value}'.")

 
    if new_status == CourseEnrollmentStatus.COMPLETED:
        # Solo un usuario con rol NORMAL puede marcar un curso como 'completed'
        if current_user.role != UserRole.NORMAL:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only normal users can mark courses as completed.")
        
        #  El usuario normal solo puede completar SU PROPIO curso
        if current_user.dni != enrollment.person.dni:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only complete your own enrollments.")
        
        
        enrollment.completion_date = date.today()
        enrollment.expiration_date = enrollment.completion_date + timedelta(days=180) # 6 meses desde la finalización

    elif new_status == CourseEnrollmentStatus.USED:
        # Solo inspectores, jueces o administradores pueden marcar un curso como 'used'
        if current_user.role not in [UserRole.INSPECTOR, UserRole.JUEZ, UserRole.ADMIN]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges. Only inspectors, judges, or admins can mark courses as used.")

        # Validar que se provea inspector_id o judge_id
        inspector_id = status_update_data.inspector_id
        judge_id = status_update_data.judge_id

        if not inspector_id and not judge_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="For status 'used', either 'inspector_id' or 'judge_id' must be provided.")
        
        # Validar que los IDs de inspector/juez existen (si se proporcionan)
        if inspector_id:
            inspector = session.get(Inspector, inspector_id)
            if not inspector:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspector with ID {inspector_id} not found.")
        if judge_id:
            judge = session.get(Judge, judge_id)
            if not judge:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Judge with ID {judge_id} not found.")

        
        enrollment.inspector_id = inspector_id
        enrollment.judge_id = judge_id
        enrollment.expiration_date = date.today() 
        
    
        if not enrollment.completion_date:
            enrollment.completion_date = date.today()

  
    if new_status != CourseEnrollmentStatus.USED:
        enrollment.inspector_id = None
        enrollment.judge_id = None

    enrollment.status = new_status
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    
    enrollment_with_relations = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment.id)
        .options(selectinload(CourseEnrollment.person), selectinload(CourseEnrollment.course))
    ).first()
    
    return _get_calculated_enrollment_read(enrollment_with_relations, session)

def delete_enrollment(enrollment_id: int, session: Session) -> bool:
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return False
    session.delete(enrollment)
    session.commit()
    return True


from sqlalchemy.orm import selectinload