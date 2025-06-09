from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.course_enrollment import CourseEnrollment
from app.config.database import get_session
from typing import List
from datetime import date, timedelta

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/", response_model=CourseEnrollment)
def create_enrollment(enrollment: CourseEnrollment, session: Session = Depends(get_session)):
    # Validar que la persona y el curso existen
    person = session.get(enrollment.person_id)
    course = session.get(enrollment.course_id)
    if not person or not course:
        raise HTTPException(status_code=404, detail="Person or Course not found")
    today = date.today()
    enrollment.enrollment_date = today
    enrollment.deadline_date = today + timedelta(days=60)      # 2 meses
    enrollment.expiration_date = today + timedelta(days=180)   # 6 meses
    enrollment.status = "pending"

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment

@router.get("/", response_model=List[CourseEnrollment])
def read_all_enrollments(session: Session = Depends(get_session)):
    return session.exec(select(CourseEnrollment)).all()