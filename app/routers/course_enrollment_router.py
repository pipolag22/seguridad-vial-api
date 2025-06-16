from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from datetime import date

from app.config.database import get_session
from app.models import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdate
from app.models.course_enrollment import CourseEnrollmentReportItem 
from app.services import course_enrollment_service
from app.routers.user_router import get_current_admin_user, get_current_inspector_user, get_current_judge_user, get_current_user # Asegúrate de que estos imports sean correctos para tus funciones de seguridad


router = APIRouter(prefix="/course-enrollments", tags=["Course Enrollments"])

@router.post("/", response_model=CourseEnrollmentRead, status_code=status.HTTP_201_CREATED, summary="Crear una nueva inscripción a curso")
def create_course_enrollment_endpoint(
    enrollment_create: CourseEnrollmentCreate,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_admin_user)
):
    """
    Crea una nueva inscripción para un curso de seguridad vial.
    La fecha de expiración se calculará automáticamente si no se proporciona.
    Requiere rol de ADMIN.
    """
    new_enrollment = course_enrollment_service.create_course_enrollment(enrollment_create, session)
    return new_enrollment

@router.get("/", response_model=List[CourseEnrollmentRead], summary="Obtener todas las inscripciones a cursos")
def read_all_course_enrollments_endpoint(
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_inspector_user) 
):
    """
    Obtiene una lista de todas las inscripciones a cursos de seguridad vial.
    Requiere rol de ADMIN o INSPECTOR.
    """
    enrollments = course_enrollment_service.get_all_course_enrollments(session)
    return enrollments

@router.get("/{enrollment_id}", response_model=CourseEnrollmentRead, summary="Obtener inscripción por ID")
def read_course_enrollment_endpoint(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_inspector_user) # ADMIN o INSPECTOR pueden ver por ID
):
    """
    Obtiene los detalles de una inscripción a curso específica por su ID.
    Requiere rol de ADMIN o INSPECTOR.
    """
    enrollment = course_enrollment_service.get_course_enrollment_by_id(enrollment_id, session)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada")
    return enrollment

@router.put("/{enrollment_id}", response_model=CourseEnrollmentRead, summary="Actualizar inscripción por ID")
def update_course_enrollment_endpoint(
    enrollment_id: int,
    enrollment_update: CourseEnrollmentUpdate,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_admin_user) # Solo ADMIN puede actualizar inscripciones
):
    """
    Actualiza la información de una inscripción a curso existente por su ID.
    Requiere rol de ADMIN.
    """
    updated_data = enrollment_update.model_dump(exclude_unset=True)
    updated_enrollment = course_enrollment_service.update_course_enrollment(enrollment_id, updated_data, session)
    if not updated_enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada")
    return updated_enrollment

@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar inscripción por ID")
def delete_course_enrollment_endpoint(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_admin_user) # Solo ADMIN puede eliminar inscripciones
):
    """
    Elimina una inscripción a curso del sistema por su ID.
    Requiere rol de ADMIN.
    """
    if not course_enrollment_service.delete_course_enrollment(enrollment_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada")
    return



@router.put(
    "/{enrollment_id}/complete",
    response_model=CourseEnrollmentRead,
    summary="Marcar inscripción como Completada",
    description="Marca una inscripción a curso como 'Completada' y establece la fecha de finalización. Si la inscripción es marcada como completada, su fecha de expiración se recalcula a 60 días desde la finalización. Requiere rol de ADMIN, INSPECTOR o JUEZ."
)
def complete_enrollment_endpoint(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_inspector_user) 
   
):
    """
    Permite a un inspector o juez marcar una inscripción como completada,
    actualizando su estado y calculando la nueva fecha de vencimiento.
    """
    updated_enrollment = course_enrollment_service.mark_enrollment_as_completed(enrollment_id, session)
    if not updated_enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada")
    return updated_enrollment

@router.put(
    "/{enrollment_id}/expire-by-action",
    response_model=CourseEnrollmentRead,
    summary="Marcar inscripción como Expirada (por acción)",
    description="Marca una inscripción a curso como 'Expirada' por acción de un inspector o juez, actualizando su estado y la fecha de expiración a la fecha actual. Requiere rol de ADMIN, INSPECTOR o JUEZ."
)
def expire_enrollment_by_action_endpoint(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_admin_user) 
):
    """
    Permite a un inspector o juez marcar una inscripción como expirada,
    estableciendo su estado y fecha de expiración al día actual.
    """
    updated_enrollment = course_enrollment_service.mark_enrollment_as_expired_by_action(enrollment_id, session)
    if not updated_enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada")
    return updated_enrollment


@router.get(
    "/reports/expiring-or-expired",
    response_model=List[CourseEnrollmentReportItem],
    summary="Reporte de Inscripciones Próximas a Vencer/Vencidas",
    description="Genera un reporte de inscripciones a cursos que están próximas a vencer (dentro de los días especificados) o que ya han vencido. Incluye detalles de la persona y el curso asociado. Requiere rol de ADMIN o INSPECTOR."
)
def get_expiring_enrollments_report_endpoint(
    days_until_expiration: int = 30,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_inspector_user) 
):
    """
    Genera un reporte de inscripciones a cursos que están próximas a vencer
    (dentro de los `days_until_expiration` días) o que ya han vencido.
    Incluye detalles de la persona y el curso asociado.
    """
    report_data = course_enrollment_service.get_expiring_or_expired_enrollments_report(
        session,
        days_until_expiration=days_until_expiration
    )
    return report_data