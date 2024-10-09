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


def negotiate(company, suppliers, show_logs):
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

        if target_quantity == 0:
            continue
        
        best_offer = None
        best_supplier = None

        for supplier_name, subproducts in company.beliefs['subproduct_suppliers'].items():
            supplier = suppliers[supplier_name]
            if show_logs:
                logging.info(f"{company.name} is negotiating with {supplier_name} for {subproduct}.")
            
            offer = {
                'product': subproduct,
                'quantity': target_quantity,
                'price': target_price  # Set initial price for negotiation
            }

            final_offer = None

            previous_offer = None
            previous_counteroffer = None

            # Flag to track whose turn it is to evaluate
            is_company_turn = False

            while True:
                # Supplier's turn to evaluate the initial offer
                if not is_company_turn:
                    counteroffer = supplier.evaluate_offer(offer, show_logs)

                    if counteroffer is None:
                        if show_logs:
                            logging.info(f"{supplier.name} could not make an offer for {subproduct}.")
                        break

                    # Check for negotiation loop
                    if previous_offer == offer and previous_counteroffer == counteroffer:
                        if show_logs:
                            logging.info(f"Negotiation loop detected for {subproduct}. Terminating negotiation.")
                        final_offer = None
                        break

                    # Store the current offer and counteroffer for loop detection
                    previous_offer = offer
                    previous_counteroffer = counteroffer

                    is_company_turn = True  # Toggle turn

                else:
                    # Company evaluates the supplier's counteroffer
                    new_offer = company.evaluate_counteroffer(offer, counteroffer, show_logs)

                    if new_offer is True:
                        if show_logs:
                            logging.info(f"Negotiation successful! {company.name} and {supplier.name} reached an agreement for {subproduct}.")
                        final_offer = counteroffer
                        break  # Agreement reached, exit negotiation loop

                    if new_offer is False:
                        if show_logs:
                            logging.info(f"Negotiation failed for {subproduct} with {supplier.name}.")
                        final_offer = None
                        break  # Exit negotiation loop due to failure

                    # Supplier evaluates the new offer from the company
                    counteroffer = supplier.evaluate_counteroffer(offer, new_offer, show_logs)

                    if counteroffer is True:
                        if show_logs:
                            logging.info(f"{supplier.name} accepts the new offer for {subproduct}.")
                        final_offer = new_offer
                        break  # Supplier accepts the offer

                    if counteroffer is False:
                        if show_logs:
                            logging.info(f"Negotiation failed from {supplier.name}'s side for {subproduct}.")
                        final_offer = None
                        break  # Supplier rejects the offer and negotiation fails

                    # Update the offer for the next round
                    offer = new_offer

            # After negotiation loop ends, check for best offer
            if final_offer and (best_offer is None or final_offer['price'] < best_offer['price']):
                best_offer = final_offer
                best_supplier = supplier_name
                make_transaction(company, supplier, best_offer, show_logs)

        # Store the best offer for each subproduct
        if best_offer:
            best_offers[subproduct] = {
                'supplier': best_supplier,
                'offer': best_offer
            }
            if show_logs:
                logging.info(f"Best offer for {subproduct}: {best_offer['quantity']} units at {best_offer['price']} per unit from {best_supplier}.")
        else:
            if show_logs:
                logging.info(f"No successful negotiation for {subproduct}.")
    
    return best_offers




def make_transaction(company, supplier, offer, show_logs):
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
   
    if show_logs: logging.info(f"{supplier.name} sold {quantity} units of {product} to {company.name}.")

    # Deduct the money from the company's revenue
    company.total_revenue -= offer["quantity"]*offer["price"]
    
    # Update the product-specific budget in company's s_offers
    company.s_offers[product]['units'] -= quantity  # Reduce the quantity in the product budget

    # Update the company's subproduct stock
    if product not in company.subproduct_stock:
        company.subproduct_stock[product] = {"stock": 0, "price": price}
    company.subproduct_stock[product]['stock'] += quantity 
    company.subproduct_stock[product]['price'] = max(company.subproduct_stock[product]['price'], price) 

    if show_logs: logging.info(f"{company.name} added {quantity} units of {product} to stock at {price} per unit.")
    
    return True


def popularity_percent(company, product):
    popularity = {}
    for comp in company.beliefs['company_popularity']:
        if product in company.beliefs['company_popularity'][comp]:
            popularity[comp] = company.beliefs['company_popularity'][comp][product]
    
    maxi = max(popularity.values())
    mini = min(popularity.values())
    if maxi == mini: return popularity[company.name]
    else:
        popularity_ = ((((popularity[company.name] -mini)/(maxi-mini))*100) + popularity[company.name])/2
        return popularity_

def marketing(comp, product, money, show_logs, market_env):
    unit_price = market_env.public_variables['marketing_config']['marketing_cost']
    if market_env.public_variables['company_popularity'][comp][product] + money/unit_price <= 100: 
        market_env.public_variables['company_popularity'][comp][product] += int(money/unit_price) 
    else: 
       market_env.public_variables['company_popularity'][comp][product] = 100
    if show_logs: logging.info(f"{comp}'s {product} now has {market_env.public_variables['company_popularity'][comp][product]} popularity ")
        