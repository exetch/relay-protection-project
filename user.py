class User:
    def __init__(self, name, tests_counter=0):
        self.name = name
        self.tests_counter = tests_counter

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_tests_counter(self, tests_counter):
        self.tests_counter = tests_counter

    def get_tests_counter(self):
        return self.tests_counter