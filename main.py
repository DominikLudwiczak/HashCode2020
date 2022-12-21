class Book:
    def __init__(self, book_id, value):
        self.id = book_id
        self.value = value

    def get_book(self):
        return self


class Library:
    def __init__(self, lib_id, signup_time, books_per_day):
        self.id = lib_id
        self.signup_time = signup_time
        self.books_per_day = books_per_day
        self.book_list = set()

    def add_book(self, book: Book):
        self.book_list.add(book)

    def get_lib(self):
        return self


class Solution:
    def __init__(self, list_of_libs, problem):
        self.list_of_libs = list_of_libs
        self.problem = problem
        self.fitness = 0

    def compute_fitness(self):
        scanned_books = set()

    def mutate(self):
        ...


class Population:
    def __init__(self, pop_size):
        self.pop_size = pop_size
        self.solutions = set()

    def add_solution(self, solution: Solution):
        assert len(self.solutions) < self.pop_size
        self.solutions.add(solution)

    def crossover(self):
        ...


class Problem:
    def __init__(self, deadline, libs_num):
        self.libs = []
        self.deadline = deadline
        self.libs_num = libs_num

    def add_lib(self, lib):
        assert len(self.libs) < self.libs_num
        self.libs.append(lib)

    def compute(self):
        ...

    def view_problem(self):
        print("number of libraries:", self.libs_num)
        print("deadline:", self.deadline)
        for l in range(len(self.libs)):
            lib = self.libs[l].get_lib()
            print("\tLibrary no.", l+1)
            print("\t\tOpening time:", lib.signup_time)
            print("\t\tBooks per day:", lib.books_per_day)
            print("\t\tBook list:")
            for b in lib.book_list:
                book = b.get_book()
                print("\t\t\tBook id:",book.id, "Book value:", book.value)
            print()

library = open("libraries/a_example.txt", "r")

b, l, d = [int(x) for x in library.readline().split()]
values = [int(x) for x in library.readline().split()]
assert len(values) == b

problem = Problem(d, l)

for i in range(l):
    spl = library.readline().split()
    new_lib = Library(i, int(spl[1]), int(spl[2]))
    for x in library.readline().split():
        new_lib.add_book(Book(int(x), values[int(x)]))
    problem.add_lib(new_lib)
library.close()

problem.view_problem()
# problem.compute()