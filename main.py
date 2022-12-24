import random
from copy import deepcopy


class Book:
    def __init__(self, book_id, value):
        self.id = book_id
        self.value = value


class Library:
    def __init__(self, lib_id, signup_time, books_per_day):
        self.id = lib_id
        self.signup_time = signup_time
        self.books_per_day = books_per_day
        self.book_list = set()

    def add_book(self, book: Book):
        self.book_list.add(book)

    def sort_books(self):
        self.book_list = sorted(self.book_list, key=lambda x: x.value, reverse=True)

    def give_scanned_books(self, days_left, already_scanned):
        days_left -= self.signup_time
        books = []
        scanned = 0
        for b in self.book_list:
            if scanned == days_left*self.books_per_day:
                break
            if b not in already_scanned:
                books.append(b)
                scanned += 1
        return books


class Solution:
    def __init__(self, list_of_libs):
        self.list_of_libs = list_of_libs
        self.fitness = self.compute_fitness()

    def compute_fitness(self):
        fitness = 0
        for lib in self.list_of_libs:
            for b in lib.book_list:
                fitness += b.value
        return fitness

    


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
    def __init__(self, deadline, libs_num, pop_size):
        self.libs = []
        self.deadline = deadline
        self.libs_num = libs_num
        self.pop_size = pop_size

    def add_lib(self, lib):
        assert len(self.libs) < self.libs_num
        self.libs.append(lib)

    def compute(self):
        pop = Population(self.pop_size)
        for i in range(self.pop_size):
            days_left = self.deadline
            libs = []
            scanned_books = set()
            for l in sorted(self.libs, key=lambda x: random.random()):
                if days_left <= 0:
                    break
                sol_lib = deepcopy(l)
                sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
                scanned_books.update(sol_lib.book_list)
                days_left -= l.signup_time
                libs.append(sol_lib)
            pop.add_solution(Solution(libs))
        return pop

    def view_problem(self):
        print("number of libraries:", self.libs_num)
        print("deadline:", self.deadline)
        for l in self.libs:
            print("\tLibrary no.", l.id)
            print("\t\tOpening time:", l.signup_time)
            print("\t\tBooks per day:", l.books_per_day)
            print("\t\tBook list:")
            for b in l.book_list:
                print("\t\t\tBook id:",b.id, "Book value:", b.value)
            print()
    
        #dobra uznałem że bez komentarzy to jednak nie da rady
        #przenoszę oba do Problem bo potrzebuję dostępu do orginalnych bibliotek żeby wiedzieć jakie książki mogę zeskanować
        #możesz wyjebać te linijki komentarza jak je przeczytasz
    def mutate(self, solution: Solution):
        #tu poniżej zmieniam kolejność 2 losowych w solution
        idx1, idx2 = random.sample(range(len(solution.list_of_libs)), 2)
        solution.list_of_libs[idx1], solution.list_of_libs[idx2] = solution.list_of_libs[idx2], solution.list_of_libs[idx1]

        #tutaj dużo kopiowania kodu robiłem z compute pewnie powinienem to jakoś rozbić na metody ale to razem przegadamy jak co
        days_left = self.deadline
        scanned_books = set()
        #nie zdebugowałem tego ale powinno updateować wszystkie biblioteki z solution.list_of_libs
        for idx in range(min(idx1, idx2)):
            l = self.libs[idx]
            if days_left <= 0:
                break
            scanned_books.update(l.give_scanned_books(days_left, scanned_books))
            days_left -= l.signup_time
        
        for idx in range(min(idx1,idx2), len(solution.list_of_libs)):
            if days_left <= 0:
                break
            l = self.libs[solution.list_of_libs[idx].id]
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update(sol_lib.book_list)
            days_left -= l.signup_time
            solution[idx] = sol_lib
        
        return solution
            
            
            




library = open("libraries/f_libraries_of_the_world.txt", "r")

b, l, d = [int(x) for x in library.readline().split()]
values = [int(x) for x in library.readline().split()]
assert len(values) == b

problem = Problem(d, l, 10)

for i in range(l):
    spl = library.readline().split()
    new_lib = Library(i, int(spl[1]), int(spl[2]))
    for x in library.readline().split():
        new_lib.add_book(Book(int(x), values[int(x)]))
    new_lib.sort_books()
    problem.add_lib(new_lib)
library.close()

# problem.view_problem()
test=problem.compute()
