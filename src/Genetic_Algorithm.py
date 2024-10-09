from deap import base, creator, tools
import random
import multiprocessing
import numpy as np

class Genetic_algorith:
    def __init__(self,fitness_function,individual_function,cx_function,mut_function):
        # Configurar DEAP
        self.pool = multiprocessing.Pool()
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Maximizar el fitness
        creator.create("Individual", dict, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", individual_function)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # Registrar la función de fitness
        self.toolbox.register("evaluate", fitness_function)
                
        self.toolbox.register("mate", cx_function)
        self.toolbox.register("mutate", mut_function)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def optimize(self,population_len,n_generations,cx_prob,mut_prob):
        
        poblacion = self.toolbox.population(n=population_len)
        # Evaluar la fitness inicial de la población

        fitnesses = self.toolbox.map(self.toolbox.evaluate, poblacion)

        for ind, fit in zip(poblacion, fitnesses):
                ind.fitness.values = fit

        # Ejecutar el algoritmo genético
        for gen in range(n_generations):
            # Selección
            offspring = self.toolbox.select(poblacion, len(poblacion))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Cruza
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < cx_prob:
                    self.toolbox.mate(child1, child2)
                    # Resetear fitness
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Mutación
            for mutant in offspring:
                if random.random() < mut_prob:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluar fitness de los nuevos individuos
            invalidos = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalidos)
            for ind, fit in zip(invalidos, fitnesses):
                ind.fitness.values = fit
            
            # Reemplazar la población con la descendencia
            poblacion[:] = offspring
            
            # Opcional: imprimir el mejor fitness de cada generación
            #mejores = tools.selBest(poblacion, 1)
            #print(f"Generación {gen}: Mejor Fitness = {mejores[0]}")
        
        # Obtener el mejor individuo
        mejor = tools.selBest(poblacion, 1)[0]
        
        #print("\nMejor distribución de presupuesto:")
        return mejor

    def close_pool(self):
        """Método para cerrar el pool de procesos cuando finalice la optimización"""
        self.pool.close()
        self.pool.join()
