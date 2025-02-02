class Person:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class Student(Person):
    def __init__(self, name, surname, courses_in_progress=None):
        super().__init__(name, surname)
        self.courses_in_progress = courses_in_progress if courses_in_progress else []
        self.grades = {}

    def rate_lecturer(self, lecturer, course, grade):
        if course in self.courses_in_progress and course in lecturer.courses_attached:
            if course in lecturer.grades:
                lecturer.grades[course] += [grade]
            else:
                lecturer.grades[course] = [grade]
        else:
            return "Ошибка"

    def average_grade(self):
        total_grades = 0
        total_count = 0
        for grades in self.grades.values():
            total_grades += sum(grades)
            total_count += len(grades)
        return total_grades / total_count if total_count != 0 else 0

    def __str__(self):
        return f"Студент: {self.name} {self.surname}, Средняя оценка за домашние задания: {self.average_grade():.2f}"


class Lecturer(Person):
    def __init__(self, name, surname, courses_attached=None):
        super().__init__(name, surname)
        self.courses_attached = courses_attached if courses_attached else []
        self.grades = {}

    def average_grade(self):
        total_grades = 0
        total_count = 0
        for grades in self.grades.values():
            total_grades += sum(grades)
            total_count += len(grades)
        return total_grades / total_count if total_count != 0 else 0

    def __str__(self):
        return f"Лектор: {self.name} {self.surname}, Средняя оценка за лекции: {self.average_grade():.2f}"


class Reviewer(Person):
    def __init__(self, name, surname):
        super().__init__(name, surname)

    def rate_student(self, student, course, grade):
        if course in student.courses_in_progress:
            if course in student.grades:
                student.grades[course] += [grade]
            else:
                student.grades[course] = [grade]
        else:
            return "Ошибка"

    def __str__(self):
        return f"Проверяющий: {self.name} {self.surname}"

def average_student_grade(students, course):
    total_grades = 0
    total_count = 0
    for student in students:
        if course in student.grades:
            total_grades += sum(student.grades[course])
            total_count += len(student.grades[course])
    return total_grades / total_count if total_count != 0 else 0

def average_lecturer_grade(lecturers, course):
    total_grades = 0
    total_count = 0
    for lecturer in lecturers:
        if course in lecturer.grades:
            total_grades += sum(lecturer.grades[course])
            total_count += len(lecturer.grades[course])
    return total_grades / total_count if total_count != 0 else 0

# Студенты
student1 = Student('Иван', 'Иванов', ['Python', 'Git'])
student2 = Student('Мария', 'Кузнецова', ['Python', 'Git'])

# Лекторы
lecturer1 = Lecturer('Алексей', 'Алексеев', ['Python'])
lecturer2 = Lecturer('Екатерина', 'Петрова', ['Git'])

# Проверяющие
reviewer1 = Reviewer('Дмитрий', 'Сидоров')
reviewer2 = Reviewer('Ольга', 'Миронова')

# Оценки студентам
reviewer1.rate_student(student1, 'Python', 9)
reviewer1.rate_student(student2, 'Python', 8)
reviewer2.rate_student(student1, 'Git', 7)
reviewer2.rate_student(student2, 'Git', 10)

# Оценки лекторам
student1.rate_lecturer(lecturer1, 'Python', 8)
student2.rate_lecturer(lecturer1, 'Python', 9)
student1.rate_lecturer(lecturer2, 'Git', 7)
student2.rate_lecturer(lecturer2, 'Git', 9)

# Вывод информации о студентах и лекторах
print(student1)
print(student2)
print(lecturer1)
print(lecturer2)

# Подсчет средней оценки
average_student_python = average_student_grade([student1, student2], 'Python')
average_lecturer_python = average_lecturer_grade([lecturer1, lecturer2], 'Python')

print(f"Средняя оценка за домашние задания по курсу Python: {average_student_python:.2f}")
print(f"Средняя оценка за лекции по курсу Python: {average_lecturer_python:.2f}")