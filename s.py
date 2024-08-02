class Employee:
    __id = 0

    def __init__(self, emp_name, emp_salary, emp_department):
        self.emp_id = f'E{self.set_id()}'
        self.emp_name = emp_name
        self.emp_salary = emp_salary
        self.emp_department = emp_department

    @classmethod
    def set_id(cls):
        cls.__id += 1
        return cls.__id

    def get_id(self):
        return self.__id

    def calculate_emp_salary(self):
        pass
    
    def emp_assign_department(self, department_name):
        pass
        
    def print_employee_details(self):
        return f'Employee name: {self.emp_name}\nEmployee department: {self.emp_department}\nId: {self.emp_id}'
    

emp1 = Employee('ADAMS', 50000, 'ACCOUNTING')
emp2 = Employee('JONES', 45000, 'RESEARCH')
emp3 = Employee('MARTIN', 55000, 'SALES')

print(emp1.print_employee_details())
print(emp2.print_employee_details())
print(emp3.print_employee_details())
