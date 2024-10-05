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

        for supplier_name, subproducts in company.beliefs['subproduct_suppliers'].items():
            supplier = suppliers[supplier_name]
            logging.info(f"{company.name} is negotiating with {supplier_name} for {subproduct}.")
            
            offer = {
                'product': subproduct,
                'quantity': target_quantity,
            }

            final_offer = None

            previous_offer = None
            previous_counteroffer = None

            while True:
                # Step 1: Supplier evaluates the company's initial offer
                counteroffer = supplier.evaluate_offer(offer)

                offer["price"] = target_price

                if counteroffer is None:
                    logging.info(f"{supplier.name} could not make an offer for {subproduct}.")
                    break

                # Step 2: Check if negotiation is stuck in a loop
                if previous_offer == offer and previous_counteroffer == counteroffer:
                    logging.info(f"Negotiation loop detected for {subproduct}. Terminating negotiation.")
                    final_offer = None
                    break


                # Step 3: Company evaluates the supplier's counteroffer
                new_offer = company.evaluate_counteroffer(offer, counteroffer)

                if new_offer == True:
                    logging.info(f"Negotiation successful! {company.name} and {supplier.name} reached an agreement for {subproduct}.")
                    final_offer = counteroffer
                    break  # Agreement reached, exit negotiation loop
                
                if new_offer == False:
                    logging.info(f"Negotiation failed for {subproduct} with {supplier.name}.")
                    final_offer = None
                    break  # Exit negotiation loop due to failure
                
                # Step 4: Supplier evaluates the new offer from the company (new counter-counteroffer)
                counteroffer = supplier.evaluate_counteroffer(offer, new_offer)

                if counteroffer == True:
                    logging.info(f"{supplier.name} accepts the new offer for {subproduct}.")
                    final_offer = new_offer
                    break  # Supplier accepts the offer
                
                if counteroffer == False:
                    logging.info(f"Negotiation failed from {supplier.name}'s side for {subproduct}.")
                    final_offer = None
                    break  # Supplier rejects the offer and negotiation fails

                # If the negotiation keeps going, set offer for next round
                offer = new_offer
                
                # Store the current offer and counteroffer for comparison in the next iteration
                previous_offer = offer
                previous_counteroffer = counteroffer

            # After negotiation loop ends, check for best offer
            if final_offer and (best_offer is None or final_offer['price'] < best_offer['price']):
                best_offer = final_offer
                best_supplier = supplier_name
                make_transaction(company, supplier, best_offer)

        # Store the best offer for each subproduct
        if best_offer:
            best_offers[subproduct] = {
                'supplier': best_supplier,
                'offer': best_offer
            }
            logging.info(f"Best offer for {subproduct}: {best_offer['quantity']} units at {best_offer['price']} per unit from {best_supplier}.")
        else:
            logging.info(f"No successful negotiation for {subproduct}.")
    
    return best_offers



def make_transaction(company, supplier, offer):
    """
    This function handles the transaction between the company and the supplier after an offer is accepted.
    It updates the supplier's stock, the company's product budget, and the company's subproduct stock.
    
    :param company: The company making the purchase
    :param supplier: The supplier providing the goods
    :param offer: The accepted offer with details of the transaction (product, quantity, price)
    """
    product = offer['product']
    quantity = offer['quantity']
    price = offer['price']
    
    # Update supplier's stock (reduce the quantity of the product in supplier conditions)
    supplier_conditions = supplier.beliefs['supplier_conditions'].get(product, {})
    if not supplier_conditions:
        logging.error(f"Supplier does not provide {product}.")
        return False  # Transaction fails if the product is not found
    
    # Deduct the quantity from the supplier's stock
    supplier.beliefs['supplier_conditions'][product]['quantity'] -= quantity
    logging.info(f"{supplier.name} sold {quantity} units of {product} to {company.name}.")

    # Deduct the money from the company's product budget
    allocated_budget = company.s_offers[product]['units'] * company.s_offers[product]['price']
    total_cost = quantity * price
    
    # Update the product-specific budget in company's s_offers
    company.s_offers[product]['units'] -= quantity  # Reduce the quantity in the product budget

    # Update the company's subproduct stock
    if product not in company.subproduct_stock:
        company.subproduct_stock[product] = {"stock": 0, "price": price}
    company.subproduct_stock[product]['stock'] += quantity 
    company.subproduct_stock[product]['price'] = price 

    logging.info(f"{company.name} added {quantity} units of {product} to stock at {price} per unit.")
    
    # Update the company's total budget only for this specific product
    company.total_budget += allocated_budget - total_cost 
    logging.info(f"{company.name}'s total budget updated to {company.total_budget}.")

    return True
