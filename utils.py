import logging
import numpy as np
from copy import deepcopy

def distribute_budgets(households, initial_min_budget, mean_budget):
    budgets = np.random.exponential(scale=mean_budget - initial_min_budget, size=len(households))
    budgets += initial_min_budget
    mean_actual = np.mean(budgets)
    
    # Asegurar que ningún hogar tenga un presupuesto de 0
    budgets[budgets <= initial_min_budget] = initial_min_budget
    
    # Normalizar el presupuesto para que el promedio sea 100
    #normalized_budgets = (budgets * (100 / mean_actual)).round(3)

    # Asignar los presupuestos a los hogares
    for i, household in enumerate(households):
        household.budget = budgets[i]
    
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
    budgets = sorted([household.budget for household in households])
    quintiles = np.percentile(budgets, [20, 40, 60, 80])
    quintile_groups = np.digitize([household.budget for household in households], quintiles)
    for i in range(len(households)):
        households[i].quintil = quintile_groups[i]
    return households

# Asignación de parámetros Cobb-Douglas (alpha y beta)
def assign_alpha(households,products,mean_alpha_quintiles,sd_alpha):
    for i in range(len(products)):
        for quintile in range(5):
            mean_alpha = mean_alpha_quintiles[i][quintile]
            for household in households:
                if household.quintil == quintile:
                    household.alpha[products[i]]= np.random.normal(mean_alpha,sd_alpha[i])
                    if household.alpha[products[i]] <=0: household.alpha[products[i]]=0
    return households


def calculate_percent(total,part):
    return part*100/total if total != 0 else 0


def negotiate(company, suppliers):
    """
    The negotiation process between the company and multiple suppliers for each subproduct in the company's s_offers.
    The company selects the best offer (lowest price and/or highest quantity) from multiple suppliers.
    
    :param company: The company initiating the negotiation
    """
    best_offers = {}

    # Iterate over each subproduct in the company's s_offers
    for subproduct, offer_details in company.s_offers.items():
        target_quantity = offer_details['units']
        target_price = offer_details['price']
        
        best_offer = None
        best_supplier = None

        # Iterate through each supplier available to the company
        for supplier_name, subproducts in company.beliefs['subproduct_suppliers'].items():
            supplier = suppliers[supplier_name]
            logging.info(f"{company.name} is negotiating with {supplier_name} for {subproduct}.")
            
            # Create the initial offer
            offer = {
                'product': subproduct,
                'quantity': target_quantity,
                'price': target_price
            }

            while True:
                counteroffer = supplier.evaluate_offer(offer)
                
                decision = company.evaluate_counteroffer(offer, counteroffer)
                
                if decision:
                    logging.info(f"Negotiation successful! {company.name} and {supplier.name} reached an agreement for {subproduct}.")
                    final_offer = counteroffer
                    break  
                elif decision:
                    logging.info(f"Negotiation failed for {subproduct} with {supplier.name}.")
                    final_offer = None
                    break 

                offer = decision 
            
            if final_offer and (best_offer is None or final_offer['price'] < best_offer['price']):
                best_offer = final_offer
                best_supplier = supplier_name
        
        if best_offer:
            best_offers[subproduct] = {
                'supplier': best_supplier,
                'offer': best_offer
            }
            logging.info(f"Best offer for {subproduct}: {best_offer['quantity']} units at {best_offer['price']} per unit from {best_supplier}.")
        else:
            logging.info(f"No successful negotiation for {subproduct}.")
    
    return best_offers
