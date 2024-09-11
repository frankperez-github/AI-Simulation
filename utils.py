import numpy as np
from copy import deepcopy

def distribute_budgets(households, initial_min_budget, mean_budget):
    budgets = np.random.exponential(scale=mean_budget - initial_min_budget, size=len(households))
    budgets += initial_min_budget
    mean_actual = np.mean(budgets)
    
    # Asegurar que ningún hogar tenga un presupuesto de 0
    budgets[budgets <= initial_min_budget] = initial_min_budget
    
    # Normalizar el presupuesto para que el promedio sea 100
    normalized_budgets = (budgets * (100 / mean_actual)).round(3)

    # Asignar los presupuestos a los hogares
    for i, household in enumerate(households):
        household.beliefs['budget'] = normalized_budgets[i]
    
    return households

# Calcular el índice de Gini
def calculate_gini(households):
    budgets = sorted([household.budget for household in households])
    total_budget = sum(budgets)
    budget_sum_so_far = 0
    gini = 0
    
    for i, budget in enumerate(budgets, 1):
        budget_sum_so_far += budget
        gini += (i / len(budgets)) - (budget_sum_so_far / total_budget)
    
    gini_index = (gini / len(budgets)) * 2
    return gini_index

# Calcular la relación P90/P10
def calculate_p90_p10(households):
    budgets = sorted([household.budget for household in households])
    
    bottom_decile = budgets[int(0.1 * len(budgets))]
    top_decile = budgets[int(0.9 * len(budgets))]
    
    return top_decile / bottom_decile


# Clasificación de los hogares en quintiles
def classify_quintiles(households):
    budgets = sorted([household.beliefs['budget'] for household in households])
    quintiles = np.percentile(budgets, [20, 40, 60, 80])
    quintile_groups = np.digitize([household.beliefs['budget'] for household in households], quintiles)
    for i in range(len(households)):
        households[i].beliefs['quintil']=quintile_groups[i]
    return households

# Asignación de parámetros Cobb-Douglas (alpha y beta)
def assign_alpha(households,count_prodcuts,mean_alpha_quintiles,sd_alpha):
    for i in range(count_prodcuts):
        for quintile in range(5):
            mean_alpha = mean_alpha_quintiles[i][quintile]
            for household in households:
                if household.beliefs['quintil']==quintile:
                    household.beliefs['alpha'][i]= np.random.normal(mean_alpha,sd_alpha[i])
                    if household.beliefs['alpha'][i] <=0: household.beliefs['alpha'][i]=0.001
    return households

# Cálculo de demanda y utilidad para un bien A
def calculate_demand_utility(households, price,count_products):
    households_new_price= deepcopy(households)
    for i in range(count_products):
        for household in households_new_price:
            household.beliefs['demand'][i] = household.beliefs['budget'] * household.beliefs['alpha'][i] / price[i]
            household.beliefs['expenditure'][i] = household.beliefs['demand'][i] * price[i]
            household.beliefs['utility'][i] = (household.beliefs['demand'][i] ** household.beliefs['alpha'][i]) * ((household.beliefs['budget'] - household.beliefs['expenditure'][i]) ** (1 - household.beliefs['alpha'][i]))
    return households_new_price

