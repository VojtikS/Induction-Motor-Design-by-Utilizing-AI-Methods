import random as rd
import numpy as np
import costF




class DE():


    def __init__(self, popSize, F, CR, gens, optimPar):
        self.popSize = popSize
        self.F = F
        self.CR = CR
        self.gens = gens
        self.optimPar = optimPar
        self.dim = len(optimPar)

        #   Converting bounds into array, T means transposed
        #   It must be transposed so the boundaries are stored in bmin, bmax
        self.bmin, self.bmax = np.asarray(optimPar).T

        #   diff = search range of every parameter (array)
        #   Can't use bmax-bmin, it might result in 0
        self.diff = np.fabs(self.bmin - self.bmax)

        self.optimize()



    def optimize(self):
        gens = self.gens
        popSize = self.popSize

        population, pop = self.get_population()
        costEval, \
        bestIndex, \
        bestIndividual, \
        bestValue = self.evaluate_population(population)

        g = gens
        yCostVal = (bestValue,)

        while gens:
            for i in range(popSize):
                # Pick the current individual
                currentIndividual = population[i]
                currInd = pop[i]
                # Create a list of indices of other individuals to pick other parents
                indices = [index for index in range(popSize) if index != i]

                # Pick 3 indices from list, don't replace it with anything
                r1, r2, r3 = pop[np.random.choice(indices, 3, replace=False)]

                # Noise vector (in range <0,1>)
                nV = self.noise_vector(r1, r2, r3)

                # Crossing
                tV = self.crossing(currInd, nV)

                trialVector = self.bmin + tV * self.diff

                # Cost evaluation of trial vector
                costTrial = costF.costF(trialVector)

                if costTrial < costEval[i]:
                    costEval[i] = costTrial
                    population[i] = trialVector
                    pop[i] = tV
                    if costTrial < bestValue:
                        bestIndex = i
                        bestValue = costTrial
                        best = trialVector
                        # convergence check
                        g = gens

            if g > gens+10:
                break

            # Adding plot values
            yCostVal = yCostVal + (bestValue,)

            gens -= 1

        return bestIndividual, bestValue, yCostVal


    def get_population(self):
        popSize = self.popSize
        dim = self.dim

        #   Array of random numbers in range [0,1]
        pop = np.random.rand(popSize, dim)

        #   Get the <0,1> population (pop) into boundaries (=ppl)
        #   (can't do pop*bmax - it wouldn't cover numbers <0)
        population = self.bmin + pop * self.diff

        return population, pop



    def evaluate_population(self, individuals):
        costEval = np.asarray([costF.costF(ind) for ind in individuals])
        # Marking the best individual
        bestIndex = np.argmin(costEval)
        bestIndividual = individuals[bestIndex]
        bestValue = costEval[bestIndex]

        return costEval, bestIndex, bestIndividual, bestValue



    def noise_vector(self, r1, r2, r3):
        F = self.F
        nV = r1 + F * (r2 - r3)

        #   This returns parameters ejected from boundaries
        #   to random position near the edge
        nV[nV > 1] = np.random.uniform(0.8, 1)
        nV[nV < 0] = np.random.uniform(0, 0.2)

        return nV



    def crossing(self, currInd, nV):
        CR = self.CR
        dim = self.dim
        # Trial vector in interval <0,1>
        tV = np.asarray([nV[j] if np.random.rand() < CR
                        else currInd[j] for j in range(dim)])

        return tV
