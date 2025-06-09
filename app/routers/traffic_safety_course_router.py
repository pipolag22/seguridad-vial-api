from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.config.database import get_session
from typing import List

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/", response_model=TrafficSafetyCourse)
def create_course(course: TrafficSafetyCourse, session: Session = Depends(get_session)):
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

@router.get("/", response_model=List[TrafficSafetyCourse])
def read_all_courses(session: Session = Depends(get_session)):
    return session.exec(select(TrafficSafetyCourse)).all()

@router.get("/{course_id}", response_model=TrafficSafetyCourse)
def read_course(course_id: int, session: Session = Depends(get_session)):
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=TrafficSafetyCourse)
def update_course(course_id: int, updated: TrafficSafetyCourse, session: Session = Depends(get_session)):
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.name = updated.name
    course.description = updated.description
    session.commit()
    session.refresh(course)
    return course

@router.delete("/{course_id}")
def delete_course(course_id: int, session: Session = Depends(get_session)):
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course)
    session.commit()
    return {"deleted": True}
