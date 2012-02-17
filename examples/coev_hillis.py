#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import sortingnetwork as sn
INPUTS = 12

def evalNetwork(host, parasite, dimension):
    network = sn.SortingNetwork(dimension, host)
    return network.assess(parasite),

def genWire(dimension):
    return (random.randrange(dimension), random.randrange(dimension))

def genNetwork(dimension, min_size, max_size):
    size = random.randint(min_size, max_size)
    return [genWire(dimension) for i in xrange(size)]

def getParasite(dimension):
    return [random.choice((0, 1)) for i in range(dimension)]

def mutNetwork(individual, dimension, mutpb, addpb, delpb, indpb):
    if random.random() < mutpb:
        for index, elem in enumerate(individual):
            if random.random() < indpb:
                individual[index] = genWire(dimension)
    if random.random() < addpb:
        index = random.randint(0, len(individual))
        individual.insert(index, genWire(dimension))
    if random.random() < delpb:
        index = random.randrange(len(individual))
        del individual[index]
    return individual

def mutParasite(individual, indmut, indpb):
    for i in individual:
        if random.random() < indpb:
            indmut(i)
    return individual

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Host", list, fitness=creator.FitnessMin)
creator.create("Parasite", list, fitness=creator.FitnessMax)

htoolbox = base.Toolbox()
ptoolbox = base.Toolbox()

htoolbox.register("network", genNetwork, dimension=INPUTS, min_size=9, max_size=12)
htoolbox.register("individual", tools.initIterate, creator.Host, htoolbox.network)
htoolbox.register("population", tools.initRepeat, list, htoolbox.individual)

ptoolbox.register("parasite", getParasite, dimension=INPUTS)
ptoolbox.register("individual", tools.initRepeat, creator.Parasite, ptoolbox.parasite, 20)
ptoolbox.register("population", tools.initRepeat, list, ptoolbox.individual)

htoolbox.register("evaluate", evalNetwork, dimension=INPUTS)
htoolbox.register("mate", tools.cxTwoPoints)
htoolbox.register("mutate", mutNetwork, dimension=INPUTS, mutpb=0.2, addpb=0.01, 
    delpb=0.01, indpb=0.05)
htoolbox.register("select", tools.selTournament, tournsize=3)

ptoolbox.register("mate", tools.cxTwoPoints)
ptoolbox.register("indMutate", tools.mutFlipBit, indpb=0.05)
ptoolbox.register("mutate", mutParasite, indmut=ptoolbox.indMutate, indpb=0.05)
ptoolbox.register("select", tools.selTournament, tournsize=3)

def cloneHost(individual):
    """Specialized copy function that will work only on a list of tuples
    with no other member than a fitness.
    """
    clone = individual.__class__(individual)
    clone.fitness.values = individual.fitness.values
    return clone

def cloneParasite(individual):
    """Specialized copy function that will work only on a list of lists
    with no other member than a fitness.
    """
    clone = individual.__class__(list(seq) for seq in individual)
    clone.fitness.values = individual.fitness.values
    return clone

htoolbox.register("clone", cloneHost)
ptoolbox.register("clone", cloneParasite)

def main():
    random.seed(64)
    
    hosts = htoolbox.population(n=300)
    parasites = ptoolbox.population(n=300)
    hof = tools.HallOfFame(1)
    hstats = tools.Statistics(lambda ind: ind.fitness.values)
    hstats.register("avg", tools.mean)
    hstats.register("std", tools.std)
    hstats.register("min", min)
    hstats.register("max", max)
    
    logger = tools.EvolutionLogger(["gen", "evals"] + hstats.functions.keys())
    logger.logHeader()
    
    MAXGEN = 50
    H_CXPB, H_MUTPB = 0.5, 0.3
    P_CXPB, P_MUTPB = 0.5, 0.3
    
    fits = htoolbox.map(htoolbox.evaluate, hosts, parasites)
    for host, parasite, fit in zip(hosts, parasites, fits):
        host.fitness.values = parasite.fitness.values = fit
    
    hof.update(hosts)
    hstats.update(hosts)
    
    logger.logGeneration(gen=0, evals=len(hosts), stats=hstats)
    
    for g in range(1, MAXGEN):
        
        hosts = htoolbox.select(hosts, len(hosts))
        hosts = [htoolbox.clone(ind) for ind in hosts]
        parasites = ptoolbox.select(parasites, len(parasites))
        parasites = [ptoolbox.clone(ind) for ind in parasites]
        
        hosts = algorithms.varSimple(htoolbox, hosts, H_CXPB, H_MUTPB)
        parasites = algorithms.varSimple(ptoolbox, parasites, P_CXPB, P_MUTPB)
        
        fits = htoolbox.map(htoolbox.evaluate, hosts, parasites)
        for host, parasite, fit in zip(hosts, parasites, fits):
            host.fitness.values = parasite.fitness.values = fit
        
        hof.update(hosts)
        hstats.update(hosts)
        logger.logGeneration(gen=g, evals=len(hosts), stats=hstats)
    
    best_network = sn.SortingNetwork(INPUTS, hof[0])
    print best_network
    print best_network.draw()
    print "%i errors" % best_network.assess()

    return hosts, hstats, hof

if __name__ == "__main__":
    main()
