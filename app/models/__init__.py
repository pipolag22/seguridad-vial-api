# app/models/__init__.py

from .person import Person, PersonCreate, PersonRead, PersonUpdate
from .traffic_safety_course import TrafficSafetyCourse, TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate
from .inspector import Inspector, InspectorCreate, InspectorRead, InspectorUpdate
from .judge import Judge, JudgeCreate, JudgeRead, JudgeUpdate
from .course_enrollment import CourseEnrollment, CourseEnrollmentStatus, CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdate
from .user import User, UserRole, UserCreate, UserRead, UserUpdate

__all__ = [
    "Person", "PersonCreate", "PersonRead", "PersonUpdate",
    "TrafficSafetyCourse", "TrafficSafetyCourseCreate", "TrafficSafetyCourseRead", "TrafficSafetyCourseUpdate",
    "Inspector", "InspectorCreate", "InspectorRead", "InspectorUpdate",
    "Judge", "JudgeCreate", "JudgeRead", "JudgeUpdate",
    "CourseEnrollment", "CourseEnrollmentStatus", "CourseEnrollmentCreate", "CourseEnrollmentRead", "CourseEnrollmentUpdate",
    "User", "UserRole", "UserCreate", "UserRead", "UserUpdate",
]
