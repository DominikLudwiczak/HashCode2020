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

    def delete(self):
        for x in self.list_of_libs:
            del x


# class Population:
#     def __init__(self, pop_size):
#         self.pop_size = pop_size
#         self.solutions = set()
#
#     def add_solution(self, solution: Solution):
#         assert len(self.solutions) < self.pop_size
#         self.solutions.add(solution)


class Problem:
    def __init__(self, deadline, libs_num, pop_size):
        self.libs = []
        self.deadline = deadline
        self.libs_num = libs_num
        self.pop_size = pop_size
        self.p_mutate = 0.6
        self.p_cross = 0.4
        self.t_size = 2

    def add_lib(self, lib):
        assert len(self.libs) < self.libs_num
        self.libs.append(lib)

    def random_pop(self):
        # pop = Population(self.pop_size)
        pop = []
        for _ in range(self.pop_size):
            days_left = self.deadline
            libs = []
            scanned_books = set()
            for l in sorted(self.libs, key=lambda x: random.random()):
                days_left -= l.signup_time
                if days_left <= 0:
                    break
                sol_lib = deepcopy(l)
                sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
                scanned_books.update(sol_lib.book_list)
                libs.append(sol_lib)
            # pop.add_solution(Solution(libs))
            pop.append(Solution(libs))
        return pop

    def mutate(self, solution: Solution):
        idx1, idx2 = random.sample(range(len(solution.list_of_libs)), 2)
        solution.list_of_libs[idx1], solution.list_of_libs[idx2] = solution.list_of_libs[idx2], solution.list_of_libs[idx1]
        libs =[]

        days_left = self.deadline
        scanned_books = set()
        for idx in range(min(idx1, idx2)):
            l = self.libs[solution.list_of_libs[idx].id]
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            days_left -= l.signup_time
            if days_left <= 0:
                break
            scanned_books.update(sol_lib.book_list)
            libs.append(sol_lib)
        
        for idx in range(min(idx1, idx2), len(solution.list_of_libs)):
            l = self.libs[solution.list_of_libs[idx].id]
            days_left -= l.signup_time
            if days_left <= 0:
                break
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update(sol_lib.book_list)
            libs.append(sol_lib)
        xd = Solution(libs)
        return xd

    def crossover(self, sol1: Solution, sol2: Solution):
        libs = []
        taken = set()
        length = len(sol1.list_of_libs)
        days_left = self.deadline
        scanned_books = set()
        for idx in range(length//2):
            l = self.libs[sol1.list_of_libs[idx].id]
            days_left -= l.signup_time
            if days_left <= 0:
                break
            sol_lib = deepcopy(l)
            taken.add(l.id)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update(sol_lib.book_list)
            libs.append(sol_lib)

        for idx in range(length//2, length):
            l = self.libs[sol1.list_of_libs[idx].id]
            days_left -= l.signup_time
            if days_left <= 0:
                break
            if l in taken:
                for help_idx in range(length//2, length):
                    l = self.libs[sol1.list_of_libs[help_idx].id]
                    if l.id not in taken:
                        break
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update(sol_lib.book_list)
            libs.append(sol_lib)

            sol = Solution(libs)
            # sol1.delete()
            # del sol1
            return sol

    @staticmethod
    def tournament(sample):
        sample = sorted(sample, key=lambda solution: solution.fitness)
        return sample[-1]

    def step(self, population):
        for i, solution in enumerate(population):
            if i >= self.pop_size:
                break
            if random.random() < self.p_mutate:
                solution = self.mutate(solution)
            if random.random() < self.p_cross:
                solution = self.crossover(solution, population[random.randint(0, self.pop_size-1)])
            population.append(solution)
        new_population = []
        for _ in range(self.pop_size):
            new_population.append(self.tournament(random.sample(population, self.t_size)))

        return new_population

    def solve(self):
        population = self.random_pop()
        no_impro = 0
        best_score = 0
        best_solution = None
        while no_impro < 100:
            print(best_score)
            no_impro += 1
            population = self.step(population)
            for solution in population:
                if solution.fitness > best_score:
                    best_score = solution.fitness
                    best_solution = solution
                    no_impro = 0
        return best_solution


library = open("libraries/f_libraries_of_the_world.txt", "r")

b, l, d = [int(x) for x in library.readline().split()]
values = [int(x) for x in library.readline().split()]
assert len(values) == b

problem = Problem(d, l, 50)

for i in range(l):
    spl = library.readline().split()
    new_lib = Library(i, int(spl[1]), int(spl[2]))
    for x in library.readline().split():
        new_lib.add_book(Book(int(x), values[int(x)]))
    new_lib.sort_books()
    problem.add_lib(new_lib)
library.close()

# problem.view_problem()
test = problem.solve()
