from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.course_enrollment import CourseEnrollment
from app.models.person import Person
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.config.database import get_session
from typing import List, Optional
from datetime import date, timedelta

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/", response_model=CourseEnrollment)
def create_enrollment(enrollment: CourseEnrollment, session: Session = Depends(get_session)):
    # Validar que la persona y el curso existen
    person = session.get(Person, enrollment.person_id)
    course = session.get(TrafficSafetyCourse, enrollment.course_id)

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

@router.put("/{enrollment_id}/use", response_model=CourseEnrollment)
def use_course(
    enrollment_id: int,
    inspector_id: Optional[int] = None,
    judge_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if inspector_id:
        enrollment.inspector_id = inspector_id
    elif judge_id:
        enrollment.judge_id = judge_id
    else:
        raise HTTPException(status_code=400, detail="Must provide either inspector_id or judge_id")

    enrollment.status = "used"
    session.commit()
    session.refresh(enrollment)
    return enrollment

@router.get("/active", response_model=List[CourseEnrollment])
def get_active_enrollments(session: Session = Depends(get_session)):
    today = date.today()
    enrollments = session.exec(select(CourseEnrollment)).all()

    for e in enrollments:
        if e.status == "pending" and today > e.expiration_date:
            e.status = "expired"
        elif e.status == "pending" and today > e.deadline_date:
            e.status = "incomplete"

    session.commit()
    return enrollments
