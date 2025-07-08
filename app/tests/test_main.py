import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.config.database import get_session # Importa la función get_session original
from app.models import User, UserCreate, UserRole # Necesario para crear usuarios de prueba
from app.services.user_service import create_user_hashed_password # Necesario para crear usuarios de prueba
from datetime import date, timedelta
from app.models import CourseEnrollmentCreate, CourseEnrollmentReportItem, CourseEnrollmentStatus # Para el reporte

# Configuración de la base de datos de test
DATABASE_URL_TEST = "sqlite:///./test.db"
engine_test = create_engine(DATABASE_URL_TEST, echo=False, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine_test) # Crea tablas para la BD de test
    with Session(engine_test) as session:
        yield session
    SQLModel.metadata.drop_all(engine_test) # Elimina tablas después de cada test

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    # Sobreescribe la dependencia get_session en FastAPI para usar la BD de test
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear() # Limpia la sobreescritura después de los tests

def get_token_for_user(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/users/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def create_test_user(session: Session, username: str, password: str, role: UserRole):
    user_create = UserCreate(username=username, password=password, email=f"{username}@test.com", role=role)
    return create_user_hashed_password(user_create, session)

# --- Pruebas ---

def test_create_admin_user_and_login(client: TestClient, session: Session):
    """
    Verifica la creación de un usuario administrador y su inicio de sesión.
    """
    admin_user = create_test_user(session, "testadmin", "testpassword", UserRole.ADMIN)
    assert admin_user.username == "testadmin"
    assert admin_user.role == UserRole.ADMIN

    token = get_token_for_user(client, "testadmin", "testpassword")
    assert token is not None

    # Opcional: Probar un endpoint que solo el admin puede acceder
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200 # Admin puede ver todos los usuarios


def test_create_course_enrollment_and_auto_expiration_date(client: TestClient, session: Session):
    """
    Verifica que la fecha de expiración se calcula automáticamente (90 días).
    """
    # Prepara un usuario para crear la inscripción
    admin_token = get_token_for_user(client, "testadmin_enroll", "password", UserRole.ADMIN)
    
    # Necesitas una persona y un curso para crear una inscripción
    person_data = {"name": "Test Person", "last_name": "Test", "dni": "12345678A", "birth_date": "1990-01-01"}
    response_person = client.post("/persons/", json=person_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response_person.status_code == 201
    person_id = response_person.json()["id"]

    course_data = {"name": "Test Course", "description": "Desc", "price": 100.0, "duration_hours": 10}
    response_course = client.post("/traffic-safety-courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response_course.status_code == 201
    course_id = response_course.json()["id"]

    # Crea la inscripción sin especificar expiration_date
    enrollment_data = {
        "enrollment_date": str(date.today()),
        "person_id": person_id,
        "course_id": course_id
    }
    response_enrollment = client.post(
        "/course-enrollments/",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response_enrollment.status_code == 201
    created_enrollment = response_enrollment.json()
    
    expected_expiration_date = (date.today() + timedelta(days=90)).isoformat()
    assert created_enrollment["expiration_date"] == expected_expiration_date
    assert created_enrollment["status"] == CourseEnrollmentStatus.PENDING.value


def test_expiring_or_expired_enrollments_report(client: TestClient, session: Session):
    """
    Verifica que el reporte de inscripciones vencidas/próximas a vencer funciona.
    """
    admin_token = get_token_for_user(client, "admin_report", "password", UserRole.ADMIN)

    # Crea datos de prueba para el reporte
    # Persona 1
    person1_data = {"name": "Juan", "last_name": "Perez", "dni": "11111111A", "birth_date": "1980-01-01"}
    response_p1 = client.post("/persons/", json=person1_data, headers={"Authorization": f"Bearer {admin_token}"})
    person1_id = response_p1.json()["id"]

    # Curso 1
    course1_data = {"name": "Curso A", "description": "Desc A", "price": 100.0, "duration_hours": 10}
    response_c1 = client.post("/traffic-safety-courses/", json=course1_data, headers={"Authorization": f"Bearer {admin_token}"})
    course1_id = response_c1.json()["id"]

    # Inscripción 1 (Vencida) - expiró ayer
    expired_enrollment_data = {
        "enrollment_date": str(date.today() - timedelta(days=91)), # Inscrito hace 91 días
        "expiration_date": str(date.today() - timedelta(days=1)),  # Expiró ayer
        "person_id": person1_id,
        "course_id": course1_id,
        "status": CourseEnrollmentStatus.EXPIRED.value # Opcional, podría ser PENDING y se marcaría EXPIRED por la fecha
    }
    client.post("/course-enrollments/", json=expired_enrollment_data, headers={"Authorization": f"Bearer {admin_token}"})

    # Inscripción 2 (Próxima a vencer) - vence en 15 días
    expiring_soon_enrollment_data = {
        "enrollment_date": str(date.today() - timedelta(days=75)), # Inscrito hace 75 días
        "expiration_date": str(date.today() + timedelta(days=15)), # Vence en 15 días
        "person_id": person1_id,
        "course_id": course1_id,
        "status": CourseEnrollmentStatus.PENDING.value
    }
    client.post("/course-enrollments/", json=expiring_soon_enrollment_data, headers={"Authorization": f"Bearer {admin_token}"})

    # Inscripción 3 (No próxima a vencer ni vencida) - vence en 60 días
    valid_enrollment_data = {
        "enrollment_date": str(date.today()),
        "expiration_date": str(date.today() + timedelta(days=60)), # Vence en 60 días
        "person_id": person1_id,
        "course_id": course1_id,
        "status": CourseEnrollmentStatus.ACTIVE.value
    }
    client.post("/course-enrollments/", json=valid_enrollment_data, headers={"Authorization": f"Bearer {admin_token}"})


    # Ejecuta el reporte
    response = client.get(
        "/course-enrollments/reports/expiring-or-expired",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"days_until_expiration": 30} # Pedimos los que venzan en los próximos 30 días
    )
    
    assert response.status_code == 200
    report_items = response.json()
    
    # Deberíamos ver 2 inscripciones en el reporte (la vencida y la próxima a vencer)
    assert len(report_items) == 2
    
    # Verifica la estructura y el contenido básico de un item
    # No verificamos todos los campos ya que serían muchos, solo la estructura
    for item in report_items:
        # Pydantic v2 valida automáticamente al crear el modelo, pero aquí es JSON
        # Podemos validar que tenga las claves esperadas
        assert "id" in item
        assert "enrollment_date" in item
        assert "expiration_date" in item
        assert "person" in item
        assert "course" in item
        assert "days_until_expiration" in item
        assert "is_expired" in item
        
        # Verifica que la persona y el curso están anidados correctamente
        assert item["person"]["name"] == "Juan"
        assert item["course"]["name"] == "Curso A"

        # Verifica que la inscripción vencida esté marcada como expirada
        if item["expiration_date"] == str(date.today() - timedelta(days=1)):
            assert item["is_expired"] is True
            assert item["days_until_expiration"] < 0
        
        # Verifica que la inscripción próxima a vencer no esté expirada
        if item["expiration_date"] == str(date.today() + timedelta(days=15)):
            assert item["is_expired"] is False
            assert item["days_until_expiration"] >= 0
            assert item["days_until_expiration"] <= 30


def test_mark_enrollment_as_completed(client: TestClient, session: Session):
    """
    Verifica que se puede marcar una inscripción como completada y la fecha de expiración se actualiza.
    """
    admin_token = get_token_for_user(client, "admin_complete", "password", UserRole.ADMIN)

    # Crea persona y curso
    person_data = {"name": "Comp Person", "last_name": "Test", "dni": "22222222B", "birth_date": "1995-05-05"}
    response_p = client.post("/persons/", json=person_data, headers={"Authorization": f"Bearer {admin_token}"})
    person_id = response_p.json()["id"]

    course_data = {"name": "Curso B", "description": "Desc B", "price": 50.0, "duration_hours": 5}
    response_c = client.post("/traffic-safety-courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = response_c.json()["id"]

    # Crea una inscripción
    enrollment_data = {
        "enrollment_date": str(date.today() - timedelta(days=10)), # Inscrito hace 10 días
        "person_id": person_id,
        "course_id": course_id
    }
    response_enrollment = client.post(
        "/course-enrollments/",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response_enrollment.status_code == 201
    enrollment_id = response_enrollment.json()["id"]

    # Marca la inscripción como completada
    response_complete = client.put(
        f"/course-enrollments/{enrollment_id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response_complete.status_code == 200
    completed_enrollment = response_complete.json()

    assert completed_enrollment["status"] == CourseEnrollmentStatus.COMPLETED.value
    assert completed_enrollment["completion_date"] == str(date.today())
    # 60 días después de la finalización
    expected_new_expiration = (date.today() + timedelta(days=60)).isoformat()
    assert completed_enrollment["expiration_date"] == expected_new_expiration