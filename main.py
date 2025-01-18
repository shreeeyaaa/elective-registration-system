from fastapi import FastAPI, Path, Request, Form, HTTPException, Depends,Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, Text, Date, DateTime, Float, create_engine
)
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from datetime import datetime
from fastapi import Query
from typing import Generator
import pymysql
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
# from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = "mysql+pymysql://root:OmMina12@localhost:3306/elective_system"
# DATABASE_URL = "mysql+pymysql://root:@localhost:3306/elective_system"
# DATABASE_URL = "mysql+pymysql://root:@localhost:3306/elective_system"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def verify_password(plain_password: str, hashed_password: str):
    # return pwd_context.verify(plain_password, hashed_password)
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#hashing password
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
#define declarative_base
Base = declarative_base()

# Models
class Student(Base):
    __tablename__ = "Student"
    student_id = Column(String(255), primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    contact_number = Column(String(255))
    program = Column((String(255)), nullable=False)
    current_semester = Column(Integer)
    cgpa = Column(Float)
    batch_year = Column((String(255)), nullable=False)
    department = Column((String(255)), nullable=False)
    total_credits_completed = Column(Integer)
    advisor_id = Column((String(255)), ForeignKey("Professor.professor_id"))
    
    password_hash = Column(String(255), nullable=False)

class Course(Base):
    __tablename__ = "Course"
    course_code = Column((String(255)), primary_key=True)
    course_name = Column((String(255)), nullable=False)
    credits = Column(Integer, nullable=False)
    max_seats = Column(Integer, nullable=False)
    min_seats = Column(Integer, nullable=False)
    department = Column((String(255)), nullable=False)
    course_type = Column((String(255)))
    prerequisites = Column(Text)
    course_description = Column(Text)
    syllabus_link = Column((String(255)))
    is_active = Column(Boolean, default=True)

class Professor(Base):
    __tablename__ = "Professor"
    professor_id = Column((String(255)), primary_key=True)
    full_name = Column((String(255)), nullable=False)
    email = Column((String(255)), unique=True, nullable=False)
    contact_number = Column((String(255)))
    department = Column((String(255)), nullable=False)
    designation = Column(String(255))
    specialization = Column(String(255))
    office_room = Column(String(255))
    is_available = Column(Boolean, default=True)


class Department(Base):
    __tablename__ = "Department"
    dept_code = Column((String(255)), primary_key=True)
    dept_name = Column((String(255)), nullable=False)
    hod_id = Column((String(255)), ForeignKey("Professor.professor_id"))
    location = Column(String(255))
    max_electives_per_semester = Column(Integer, default=2)
    contact_number = Column(String(255))
    email = Column((String(255)), unique=True)

class Semester(Base):
    __tablename__ = "Semester"
    semester_id = Column((String(255)), primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    academic_year = Column((String(255)), nullable=False)
    registration_window_start = Column(DateTime)
    registration_window_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    max_credits_allowed = Column(Integer, default=21)

class TimeSlot(Base):
    __tablename__ = "Time_Slot"
    slot_id = Column((String(255)), primary_key=True)
    day = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    room_number = Column(String(255))
    capacity = Column(Integer)
    is_available = Column(Boolean, default=True)

class Admin(Base):
    __tablename__ = "Admin"
    admin_id = Column((String(255)), primary_key=True)
    full_name = Column((String(255)), nullable=False)
    role = Column((String(255)), nullable=False)
    department = Column(String(255))
    email = Column((String(255)), unique=True, nullable=False)
    contact_number = Column(String(255))

class Prerequisite(Base):
    __tablename__ = "Prerequisite"
    prereq_id = Column((String(255)), primary_key=True)
    course_code = Column((String(255)), ForeignKey("Course.course_code"))
    required_course_code = Column((String(255)), ForeignKey("Course.course_code"))
    min_grade_required = Column(String(255))

class Registration(Base):
    __tablename__ = "Registration"
    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column((String(255)), ForeignKey("Student.student_id"))
    course_code = Column((String(255)), ForeignKey("Course.course_code"))
    reg_timestamp = Column(DateTime, default=datetime.now)
    status = Column(String(255))
    priority_number = Column(Integer)
    remarks = Column(Text)
    approval_admin_id = Column((String(255)), ForeignKey("Admin.admin_id"))
    prerequisites_met = Column(Boolean, default=False)

    # Add these relationship definitions
    student = relationship("Student", backref="registrations")
    course = relationship("Course", backref="registrations")

class CourseMaterial(Base):
    __tablename__ = "Course_Material"
    material_id = Column((String(255)), primary_key=True)
    course_code = Column((String(255)), ForeignKey("Course.course_code"))
    title = Column((String(255)), nullable=False)
    document_type = Column(String(255))
    file_link = Column(String(255))
    upload_date = Column(DateTime, default=datetime.now)
    uploaded_by = Column((String(255)), ForeignKey("Professor.professor_id"))

class CourseSchedule(Base):
    __tablename__ = "Course_Schedule"
    course_code = Column((String(255)), ForeignKey("Course.course_code"), primary_key=True)
    slot_id = Column((String(255)), ForeignKey("Time_Slot.slot_id"), primary_key=True)


# Add other models as per your schema...

# Create all tables
Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    """Renders the login page."""
    return templates.TemplateResponse("landing.html", {"request": request})



# Login Handling
@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request, type: str):
    if type == "student":
        return templates.TemplateResponse("student_login.html", {"request": request})
    # Optionally handle admin login here
    elif type == "admin":
        return templates.TemplateResponse("admin_login.html", {"request": request})
    else:
        return RedirectResponse(url="/", status_code=303)


# Add new route for admin login
@app.post("/admin-authenticate", response_class=HTMLResponse)
def admin_login(
    request: Request,
    admin_id: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    # Query to find admin by both admin_id and email
    admin = db.query(Admin).filter(
        Admin.admin_id == admin_id,
        Admin.email == email
    ).first()
    
    if admin:
        return RedirectResponse(url="/admin", status_code=303)
    
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Invalid admin credentials"
    })

@app.post("/student_login", response_class=HTMLResponse)
def student_login(
    request: Request,
    student_id: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Query to find student by both student_id and email
    student = db.query(Student).filter(Student.student_id == student_id, Student.email == email).first()
    
    # Verify if student exists and the password is correct
    if student:
        # return RedirectResponse(url="/student-dashboard", status_code=303)
        print("Student authenticated successfully")  # Log the success message
        return RedirectResponse(url=f"/student-dashboard?student_id={student.student_id}", status_code=303)

    print("Invalid student ID, email, or password")  # Log the error message
    # If authentication fails, return to the login page with an error message
    return templates.TemplateResponse("student_login.html", {
        "request": request,
        "error": "Invalid student ID, email, or password"
    })


# Elective Registration Page
@app.get("/register_elective", response_class=HTMLResponse)
def register_elective_page(request: Request, db: Session = Depends(get_db)):
    """Renders the elective course registration page."""
    courses = db.query(ElectiveSubject).all()
    return templates.TemplateResponse("register_elective.html", {"request": request, "courses": courses})

# Register Elective
@app.post("/register_elective", response_class=HTMLResponse)
def register_elective(
    request: Request,
    student_id: int = Form(...),
    subject_code: str = Form(...),
    priority_rank: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        priority = StudentPriorities(
            student_id=student_id,
            subject_code=subject_code,
            priority_rank=priority_rank,
        )
        db.add(priority)
        db.commit()
        return RedirectResponse(url="/success", status_code=303)
    except SQLAlchemyError as e:
        db.rollback()
        return templates.TemplateResponse("register_elective.html", {"request": request, "error": str(e)})






@app.get("/success", response_class=HTMLResponse)
def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/courses", response_class=HTMLResponse)
def available_courses(request: Request):
    db = SessionLocal()
    courses = db.query(Course).all()
    db.close()
    return templates.TemplateResponse("courses.html", {"request": request, "courses": courses})


# Update the admin dashboard route
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    message: str = Query(None),
    error: str = Query(None),
    db: SessionLocal = Depends(get_db)
):
    try:
        # Get all registrations with student and course info
        registrations = (
            db.query(Registration)
            .options(
                joinedload(Registration.student),
                joinedload(Registration.course)
            )
            .all()
        )
        
        courses = db.query(Course).all()
        
        return templates.TemplateResponse(
            "admin.html", 
            {
                "request": request, 
                "registrations": registrations,
                "courses": courses,
                "message": message,  # Success message if any
                "error": error      # Error message if any
            }
        )
    except Exception as e:
        print(f"Error in admin dashboard: {str(e)}")
        return templates.TemplateResponse(
            "admin.html", 
            {
                "request": request, 
                "error": str(e),
                "registrations": [],
                "courses": [],
                "message": None
            }
        )
# Add route to add a course
@app.get("/admin/add_course", response_class=HTMLResponse)
def add_course_form(request: Request):
    """Renders the form for adding a new course."""
    return templates.TemplateResponse("add_course.html", {"request": request})

@app.post("/admin/add_course", response_class=HTMLResponse)
def add_course(
    request: Request,
    course_code: str = Form(...),
    course_name: str = Form(...),
    credits: int = Form(...),
    max_seats: int = Form(...),
    min_seats: int = Form(...),
    department: str = Form(...),
    course_type: str = Form(...),
    prerequisites: str = Form(None),
    course_description: str = Form(None),
    syllabus_link: str = Form(None),
    db: SessionLocal = Depends(get_db),
):
    try:
        new_course = Course(
            course_code=course_code,
            course_name=course_name,
            credits=credits,
            max_seats=max_seats,
            min_seats=min_seats,
            department=department,
            course_type=course_type,
            prerequisites=prerequisites,
            course_description=course_description,
            syllabus_link=syllabus_link,
            is_active=True
        )
        db.add(new_course)
        db.commit()
        return RedirectResponse(url="/admin", status_code=302)
    except SQLAlchemyError as e:
        db.rollback()
        return templates.TemplateResponse("add_course.html", {"request": request, "error": str(e)})


# Add this route to your main.py

@app.post("/update_registration")
async def update_registration(
    request: Request,
    registration_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Find the registration
        registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
        
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        # Update the status
        registration.status = status
        
        # Add timestamp for approval/rejection if you want to track it
        if status in ["Approved", "Rejected"]:
            registration.reg_timestamp = datetime.now()
        
        # Commit the changes
        db.commit()
        
        # Redirect back to admin dashboard with success message
        return RedirectResponse(
            url="/admin?message=Registration+updated+successfully",
            status_code=303
        )
        
    except Exception as e:
        db.rollback()
        # Redirect back to admin dashboard with error message
        return RedirectResponse(
            url=f"/admin?error=Failed+to+update+registration:+{str(e)}",
            status_code=303
        )


from sqlalchemy.orm import aliased
@app.get("/student-dashboard", response_class=HTMLResponse)
def student_dashboard(
    request: Request,
    student_id: str = Query(...),  # Expect student_id as a query parameter
    db: Session = Depends(get_db),
    view_all: bool = Query(False)  # Default is False
):
    # Fetch student data
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Student not found"})

    # Fetch courses (not registered and registered)
    registration_alias = aliased(Registration)

    courses_not_registered = db.query(Course).filter(
        Course.is_active == True,
        ~Course.course_code.in_(
            db.query(registration_alias.course_code).filter(
                registration_alias.student_id == student_id
            )
        )
    ).limit(5)  # Fetch only the first 5 if view_all is False

    courses_registered = db.query(Course).filter(
        Course.is_active == True,
        Course.course_code.in_(
            db.query(registration_alias.course_code).filter(
                registration_alias.student_id == student_id
            )
        )
    ).limit(5)

    if view_all:
        courses_not_registered = db.query(Course).filter(Course.is_active == True).all()
        courses_registered = db.query(Course).filter(Course.is_active == True).all()

    # Render the template with both courses
    return templates.TemplateResponse("student-dashboard.html", {
        "request": request,
        "student": student,  # Pass student data
        "courses_not_registered": courses_not_registered,
        "courses_registered": courses_registered,
        "view_all": view_all  # Pass the view_all flag
    })


@app.get("/search")
def search_courses(query: str = Query(..., min_length=1)):
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # SQL query to search courses based on course_name
        search_query = "SELECT * FROM course WHERE course_name LIKE %s"
        cursor.execute(search_query, (f"%{query}%",))

        # Fetch the results
        result = cursor.fetchall()

        # Close the connection
        cursor.close()
        connection.close()

        # Return the results
        return {"courses": result}
    
    except Exception as e:
        # If there's any error, return a structured error response
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching the courses.",
            headers={"X-Error": str(e)}
        )
@app.post("/update-profile")
def update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    print("Received data:", data)  # Debug: Print the received data

    student_id = data.get("student_id")
    if not student_id:
        print("Error: Student ID is missing")  # Debug: Print missing student ID error
        return {"error": "Student ID is required"}
    
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        print(f"Error: No student found with ID {student_id}")  # Debug: Print student not found error
        return {"error": "Student not found"}

    print("Before update:", student.full_name, student.email, student.contact_number)  # Debug: Print current student data

    # Update student data
    student.full_name = data.get("name", student.full_name)
    student.email = data.get("email", student.email)
    student.contact_number = data.get("phone", student.contact_number)

    try:
        db.commit()
        print("Database commit successful")  # Debug: Confirm database commit
    except Exception as e:
        print("Error during commit:", str(e))  # Debug: Print any commit errors
        db.rollback()  # Rollback to avoid partial updates
        return {"error": "Failed to update profile"}

    print("After update:", student.full_name, student.email, student.contact_number)  # Debug: Print updated student data
    return {"message": "Profile updated successfully"}




@app.post("/update-profile/{student_id}")
async def update_profile(student_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print("Received data:", data)  # Debug: Print received data

        # Fetch the student record by student_id
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            print(f"Error: No student found with ID {student_id}")  # Debug: Student not found
            return {"error": "Student not found"}

        # Update student data with provided values or keep existing ones
        student.full_name = data.get("full_name", student.full_name)
        student.email = data.get("email", student.email)
        student.contact_number = data.get("contact_number", student.contact_number)
        student.program = data.get("program", student.program)
        student.department = data.get("department", student.department)

        # Commit the changes
        db.commit()
        print("Database commit successful")  # Debug: Confirm commit

        return {"message": "Profile updated successfully"}
    
    except Exception as e:
        print("Error during update:", str(e))  # Debug: Print error details
        db.rollback()  # Rollback in case of error
        return {"error": "Failed to update profile"}





@app.get("/register.html", response_class=HTMLResponse)
def register_confirmation(request: Request, course_code: str = Query(...), student_id: str = Query(...)):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "course_code": course_code,
        "student_id": student_id,
    })



@app.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    student_id: str = Form(...),
    course_code: str = Form(...),
    db: SessionLocal = Depends(get_db)
):
    try:
        registration = Registration(
            student_id=student_id,
            course_code=course_code,
            reg_timestamp=datetime.now(),
            status="Pending",
        )
        db.add(registration)
        db.commit()

        # Log the registration to make sure it was added
        print(f"Registration successful for student {student_id} and course {course_code}")

        # Redirect to the success page
        return RedirectResponse(url=f"/student-dashboard?student_id={student_id}", status_code=303)

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error occurred: {str(e)}")  # Log the error
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})




@app.post("/drop-course/{student_id}")
def drop_course(student_id: str, course_code: str = Form(...), db: Session = Depends(get_db)):
    registration = db.query(Registration).filter(
        Registration.course_code == course_code,
        Registration.student_id == student_id
    ).first()

    if registration:
        db.delete(registration)
        db.commit()
        return {"message": "Course dropped successfully"}
    else:
        raise HTTPException(status_code=404, detail="Course not found")