from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.config.database import get_session
from app.schemas.course_enrollment_schema import CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdateStatus
from app.services import course_enrollment_service # Importa el servicio
from typing import List, Optional

router = APIRouter(prefix="/enrollments", tags=["Course Enrollments"])

@router.post("/", response_model=CourseEnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: CourseEnrollmentCreate, session: Session = Depends(get_session)
):
    enrollment = course_enrollment_service.create_enrollment(enrollment_data, session)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Person or Course not found")
    return enrollment

@router.get("/", response_model=List[CourseEnrollmentRead])
def read_all_enrollments(session: Session = Depends(get_session)):
    return course_enrollment_service.get_all_enrollments(session)

@router.get("/{enrollment_id}", response_model=CourseEnrollmentRead)
def read_enrollment(enrollment_id: int, session: Session = Depends(get_session)):
    enrollment = course_enrollment_service.get_enrollment_by_id(enrollment_id, session)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Course Enrollment not found")
    return enrollment


@router.put("/{enrollment_id}/status", response_model=CourseEnrollmentRead)
def update_enrollment_status_api(
    enrollment_id: int,
    status_update: CourseEnrollmentUpdateStatus, 
    session: Session = Depends(get_session)
):
    try:
        updated_enrollment = course_enrollment_service.update_enrollment_status(
            enrollment_id, status_update, session
        )
        if not updated_enrollment:
            raise HTTPException(status_code=404, detail="Course Enrollment not found")
        return updated_enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, session: Session = Depends(get_session)):
    if not course_enrollment_service.delete_enrollment(enrollment_id, session):
        raise HTTPException(status_code=404, detail="Course Enrollment not found")
    return {"message": "Course Enrollment deleted successfully"}
