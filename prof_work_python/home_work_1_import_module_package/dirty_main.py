from application.salary import *
from application.db.people import *

if __name__ == '__main__':
    print("Вызов функций через import *")
    calculate_salary()
    get_employees()