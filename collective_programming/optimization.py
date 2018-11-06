# -*- coding: utf-8 -*-

import time
import random

people = [
    ('Seymour', 'BOS'),
    ('Franny', 'DAL'),
    ('Zooey', 'CAK'),
    ('Walt', 'MIA'),
    ('Buddy', 'ORD'),
    ('Les', 'OMA')
]

destination = 'LGA'

flights = {}

for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])
    flights[(origin, dest)].append((depart, arrive, int(price)))


def get_minutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


def print_schedule(r):
    for d in range(len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][int(r[d])]
        ret = flights[(destination, origin)][int(r[d + 1])]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                                                      out[0], out[1], out[2],
                                                      ret[0], ret[1], ret[2])


def schedule_cost(sol):
    total_price = 0
    latest_arrival = 0
    earliest_dep = 24 * 60

    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        return_flight = flights[(destination, origin)][int(sol[d + 1])]

        total_price += outbound[2]
        total_price += return_flight[2]

        if latest_arrival < get_minutes(outbound[1]):
            latest_arrival = get_minutes(outbound[1])
        if earliest_dep > get_minutes(return_flight[0]):
            earliest_dep = get_minutes(return_flight[0])

    total_wait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        return_flight = flights[(destination, origin)][int(sol[d + 1])]
        total_wait += latest_arrival - get_minutes(outbound[1])
        total_wait += get_minutes(return_flight[0]) - earliest_dep

    if latest_arrival > earliest_dep:
        total_price += 50

    return total_price + total_wait


def genetic_optimize(domain, cost_function, pop_size=50,step=1, mutprob=0.2, elite=0.2, maxiter=100):

    # 돌연 변이
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i]-step]+vec[i+1:]

    # 교배 연산
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[1:]

    # 초기화
    population = []
    for i in range(pop_size):
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

        population.append(vec)

    top_elite = int(elite * pop_size)

    for i in range(maxiter):
        scores = [(cost_function(v), v) for v in population]
        scores.sort()
        ranked = [v for (s, v) in scores]

        pop = ranked[0:top_elite]

        while len(pop) < pop_size:
            if random.random() < mutprob:

                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:

                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        print scores[0][0]
    return scores[0][1]


domain = [(0, 8)] * (len(people) * 2)

s = genetic_optimize(domain, schedule_cost)
print_schedule(s)
