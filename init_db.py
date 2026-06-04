import random
from datetime import date

from run import app
from app import db
from app.models import Course, CourseSelection, Semester, Student, Teacher, User
from app.utils.db_objects import ensure_academic_schema


def seed_demo():
    with app.app_context():
        db.create_all()
        ensure_academic_schema()

        if User.query.filter_by(username="admin").first():
            print("Demo data already exists. Schema and database objects were checked.")
            return

        spring = Semester.query.filter_by(name="2025-2026 Spring").first()
        if spring is None:
            spring = Semester(
                name="2025-2026 Spring",
                start_date=date(2026, 2, 24),
                end_date=date(2026, 7, 5),
                is_active=True,
            )
            db.session.add(spring)

        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        student_users = []
        teacher_users = []
        for i in range(1, 21):
            user = User(username=f"20240{i:03d}", role="student")
            user.set_password("123456")
            db.session.add(user)
            student_users.append(user)

        for i in range(1, 6):
            user = User(username=f"T{i:04d}", role="teacher")
            user.set_password("123456")
            db.session.add(user)
            teacher_users.append(user)

        db.session.flush()

        student_profiles = []
        for i, user in enumerate(student_users, start=1):
            student_profiles.append(
                Student(
                    user_id=user.id,
                    student_no=user.username,
                    name=f"Student{i}",
                    age=random.randint(18, 23),
                    gender=random.choice(["男", "女"]),
                    department=random.choice(["计算机系", "软件工程系"]),
                )
            )
        db.session.add_all(student_profiles)

        teacher_profiles = []
        for i, user in enumerate(teacher_users, start=1):
            teacher_profiles.append(
                Teacher(
                    user_id=user.id,
                    teacher_no=user.username,
                    name=f"Teacher{i}",
                    department="计算机系",
                )
            )
        db.session.add_all(teacher_profiles)
        db.session.flush()

        course_specs = [
            ("CS101", "程序设计基础", 3.0, "required"),
            ("CS102", "数据结构", 3.5, "required"),
            ("CS201", "数据库原理", 3.5, "required"),
            ("CS202", "操作系统", 4.0, "required"),
            ("CS301", "计算机网络", 3.0, "required"),
            ("CS302", "编译原理", 4.0, "elective"),
            ("CS303", "人工智能导论", 2.5, "elective"),
        ]
        courses = []
        for course_no, course_name, credit, course_type in course_specs:
            courses.append(
                Course(
                    course_no=course_no,
                    course_name=course_name,
                    credit=credit,
                    department="计算机系",
                    teacher_id=random.choice(teacher_profiles).id,
                    semester_id=spring.id,
                    course_type=course_type,
                    max_students=random.randint(50, 100),
                    status="open",
                )
            )
        db.session.add_all(courses)
        db.session.flush()

        selections = []
        for student in student_profiles:
            for course in random.sample(courses, k=random.randint(2, min(5, len(courses)))):
                selections.append(
                    CourseSelection(
                        student_id=student.id,
                        course_id=course.id,
                        grade=round(random.uniform(55, 100), 2),
                    )
                )
        db.session.add_all(selections)
        db.session.commit()

        ensure_academic_schema()

        print("Demo data created.")
        print("Admin: admin / admin123")
        print("Students: 20240001-20240020 / 123456")
        print("Teachers: T0001-T0005 / 123456")
        print(f"Course selections: {len(selections)} records")


if __name__ == "__main__":
    seed_demo()
