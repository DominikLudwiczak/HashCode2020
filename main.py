import random
from copy import deepcopy
import copy
import time

end_time = time.time() + 240 # stop after 240 seconds


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

    def define_books(self, books):
        self.book_list = books

    def sort_books(self):
        self.book_list = sorted(self.book_list, key=lambda x: x.value, reverse=True)

    def give_scanned_books(self, days_left, already_scanned):
        books = []
        scanned = 0
        for b in self.book_list:
            if scanned + 1 > days_left*self.books_per_day:
                return books
            if b.id not in already_scanned:
                books.append(b)
                scanned += 1
        return books


class Solution:
    def __init__(self, list_of_libs):
        self.list_of_libs = list_of_libs
        self.fitness = self.compute_fitness()

    def compute_fitness(self):
        fitness = 0
        taken_books = set()
        for lib in self.list_of_libs:
            for b in lib.book_list:
                if b.id not in taken_books:
                    fitness += b.value
                    taken_books.add(b.id)
        return fitness


class Problem:
    def __init__(self, deadline, libs_num, pop_size):
        self.libs = []
        self.deadline = deadline
        self.libs_num = libs_num
        self.pop_size = pop_size
        self.p_mutate = 0.6
        self.p_cross = 0.2
        self.t_size = 15

    def add_lib(self, lib):
        assert len(self.libs) < self.libs_num
        self.libs.append(lib)

    def get_next(self, current_day, taken_libs):
        best = -1
        best_time = 1000000
        out = None

        for l in self.libs:
            remaining = self.deadline - current_day - l.signup_time
            if remaining <= 0:
                break
            books_count = remaining * l.books_per_day
            books_value = 0
            scanned_books = []
            for b in l.book_list:
                if len(scanned_books) >= books_count:
                    break
                books_value += b.value
                scanned_books.append(b)

            books_value /= l.signup_time

            if books_value >= best and l.id not in taken_libs:
                if books_value == best and l.signup_time >= best_time:
                    continue
                best = books_value
                best_time = l.signup_time
                out = Library(l.id, l.signup_time, l.books_per_day)
                out.define_books(scanned_books)
        return out

    def greedy(self):
        current_day = 0
        sol_libs = []
        taken_libs = set()

        for _ in self.libs:
            temp = self.get_next(current_day, taken_libs)
            if temp is None:
                break
            current_day += temp.signup_time
            taken_libs.add(temp.id)
            sol_libs.append(temp)
        sol = Solution(sol_libs)
        return sol

    def random_pop(self):
        pop = []
        pop.append(self.greedy())
        for _ in range(self.pop_size-1):
            days_left = self.deadline
            libs = []
            scanned_books = set()
            for l in sorted(self.libs, key=lambda x: random.random()):
                days_left -= l.signup_time
                if days_left > 0:
                    sol_lib = copy.copy(l)
                    sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
                    scanned_books.update([book.id for book in sol_lib.book_list])
                    libs.append(sol_lib)
                else:
                    days_left += l.signup_time
            pop.append(Solution(libs))
        return pop

    def mutate(self, solution: Solution):
        indices = [lib.id for lib in solution.list_of_libs]

        if len(indices) < len(self.libs)/2:
            taken = set([id for lib in indices])
            lib_idx = random.randint(0, len(self.libs)-1)
            while lib_idx in taken:
                lib_idx = random.randint(0, len(self.libs)-1)
            idx1 = random.randint(0, len(indices)-1)
            indices[idx1] = lib_idx
        else:
            idx1, idx2 = random.sample(range(len(indices)), 2)
            indices[idx1], indices[idx2] = indices[idx2], indices[idx1]

        libs = []
        days_left = self.deadline
        scanned_books = set()

        for lib_idx in range(len(indices)):
            l = self.libs[indices[lib_idx]]
            days_left -= l.signup_time
            if days_left <= 0:
                days_left += l.signup_time
                continue
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update([book.id for book in sol_lib.book_list])
            libs.append(sol_lib)

        taken = set([lib for lib in indices])
        for l in self.libs:
            if l.id not in taken:
                if l.signup_time < days_left:
                    days_left -= l.signup_time
                    if days_left <= 0:
                        days_left += l.signup_time
                        continue
                    sol_lib = deepcopy(l)
                    sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
                    scanned_books.update([book.id for book in sol_lib.book_list])
                    libs.append(sol_lib)

        return Solution(libs)

    def crossover(self, sol1: Solution, sol2: Solution):
        libs = []
        taken = set()
        length = len(sol1.list_of_libs)
        indices1 = [lib.id for lib in sol1.list_of_libs]
        indices2 = [lib.id for lib in sol2.list_of_libs]
        days_left = self.deadline
        scanned_books = set()

        for idx in range(length//2):
            l = self.libs[indices1[idx]]
            days_left -= l.signup_time
            if days_left <= 0:
                days_left += l.signup_time
                continue
            sol_lib = deepcopy(l)
            taken.add(l.id)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update([book.id for book in sol_lib.book_list])
            libs.append(sol_lib)

        for idx in range(length//2, len(indices2)):
            l = self.libs[indices2[idx]]
            days_left -= l.signup_time
            if days_left <= 0:
                days_left += l.signup_time
                continue
            if l in taken:
                for help_idx in range(length//2, length):
                    l = self.libs[indices1[help_idx]]
                    if l.id not in taken:
                        break
            sol_lib = deepcopy(l)
            sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
            scanned_books.update([book.id for book in sol_lib.book_list])
            libs.append(sol_lib)

        taken = set([lib.id for lib in libs])
        for l in self.libs:
            if l.id not in taken:
                if l.signup_time < days_left:
                    days_left -= l.signup_time
                    if days_left <= 0:
                        days_left += l.signup_time
                        continue
                    sol_lib = deepcopy(l)
                    sol_lib.book_list = l.give_scanned_books(days_left, scanned_books)
                    scanned_books.update([book.id for book in sol_lib.book_list])
                    libs.append(sol_lib)
        return Solution(libs)

    @staticmethod
    def tournament(sample):
        sample = sorted(sample, key=lambda solution: solution.fitness)
        winner = sample[-1]
        return winner

    def step(self, population):
        new_population = []
        for _ in range(self.pop_size):
            new_sol = self.tournament(random.sample(population, self.t_size))

            if random.random() < self.p_mutate:
                new_sol = self.mutate(new_sol)

            if random.random() < self.p_cross:
                new_sol = self.crossover(new_sol, population[0])

            new_population.append(new_sol)
        print(len(set(new_population)))
        return new_population

    def solve(self):
        population = self.random_pop()
        no_impro = 0
        best_score = 0
        best_solution = self.tournament(population)
        while time.time() < end_time:
            print(best_score)
            no_impro += 1
            population = self.step(population)
            for solution in population:
                if solution.fitness > best_score:
                    best_score = solution.fitness
                    best_solution = solution
                    no_impro = 0

        print("best fitness = ", best_solution.fitness)
        books = set()
        with open("testxd.txt", "w") as file:
            file.write(str(len(best_solution.list_of_libs)) + '\n')
            for x in best_solution.list_of_libs:
                file.write(str(x.id) + ' ' + str(len(x.book_list)) + '\n')
                for book in x.book_list:
                    file.write(str(book.id) + ' ')
                    if book in books:
                        print("pain")
                    else:
                        books.add(book)

                file.write('\n')

        print(sum([b.value for b in books]))
        return best_solution

library = open("libraries/c_incunabula.txt", "r")

b, l, d = [int(x) for x in library.readline().split()]
values = [int(x) for x in library.readline().split()]
assert len(values) == b
problem = Problem(d, l, 20)

for i in range(l):
    spl = library.readline().split()
    new_lib = Library(i, int(spl[1]), int(spl[2]))
    for x in library.readline().split():
        new_lib.add_book(Book(int(x), values[int(x)]))
    new_lib.sort_books()
    problem.add_lib(new_lib)
library.close()

test = problem.solve()
