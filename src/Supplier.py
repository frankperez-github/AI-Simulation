import random
import logging
from src.BaseAgent import BDI_Agent
from src.Environment import MarketEnvironment
import json
from src.Knowledge import *
 
des_int_json_file = open('./src/Desires-Intentions/Suppliers.json',)
int_exec_json_file = open('./src/Intentions-Execution/Suppliers.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='src/simulation_logs.log', level=logging.INFO, format='%(message)s')

class SupplierAgent(BDI_Agent):
    def __init__(self, name, products, knowledge):
        super().__init__(name)
        self.beliefs['supplier_conditions']=products
        self.knowledge = knowledge
    
    def perceive_environment(self,market_env, show_logs):
        self.beliefs['product_prices']=market_env.public_variables['product_prices']
        self.beliefs['subproducts']=market_env.public_variables['subproducts']
        if show_logs: logging.info(f"{self.name} has perceived the environment and updated beliefs about market demand and available products.")

    def form_desires(self, show_logs):
        supply = random.choice([True, False]) 
        if supply:
            self.desires.append('supply_products')
        if show_logs: logging.info(f"{self.name} has formed desires. Supply products: {supply}")

    def plan_intentions(self, show_logs):
        for desire in self.desires:
            self.intentions += desires_intentions[desire]
            if show_logs: logging.info(f"{self.name} has planned to {desires_intentions[desire]}")
        self.desires=[]

    def execute_intention(self,intention, market_env, show_logs):
        execution = intentions_execution[intention]
        for action in execution["actions"]:
            eval(action)
        if show_logs: logging.info(eval(execution["log"]))

    def supply_products(self, market_env: MarketEnvironment):
        for company in self.beliefs['product_prices']:
            for product in self.beliefs['product_prices'][company]:
                subproducts=self.beliefs['subproducts'][product]
                for subproduct in subproducts:
                    if subproduct in self.beliefs['supplier_conditions']:
                        market_env.public_variables['companies'][company].subproduct_stock[subproduct]['stock']+=100

    def evaluate_offer(self, offer, show_logs):
        """
        The supplier evaluates the offer using fuzzy logic to decide whether to accept, reject, or make a counteroffer.
        If the requested quantity exceeds available stock, the supplier offers the available quantity instead and counters.
        :param offer: The initial offer from the company
        """
        product = offer['product']
        requested_quantity = offer['quantity']

        # Retrieve the supplier's conditions for the product
        supplier_conditions = self.beliefs['supplier_conditions'].get(product, {})
        min_price = supplier_conditions.get('min_price', None)
        available_quantity = supplier_conditions.get('quantity', 0)

        if min_price is None:
            if show_logs: logging.info(f"{self.name} does not supply {product}.")
            return None
        
        if available_quantity == 0:
            return None

        # Adjust quantity if stock is less than requested
        if requested_quantity > available_quantity:
            if show_logs: logging.info(f"{self.name} does not have enough stock to supply {requested_quantity} units of {product}. Offering available stock: {available_quantity}")
            requested_quantity = available_quantity  # Adjust to available stock

        # Calculate price based on requested quantity using fuzzy logic
        price_to_offer = self.calculate_price_based_on_quantity(requested_quantity, available_quantity, min_price)

        # Evaluate the acceptability of the offer using fuzzy logic
        price_percentage = (price_to_offer - min_price) / min_price * 100
        quantity_percentage = (requested_quantity / available_quantity) * 100
        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        # If acceptability is high, accept the offer
        if acceptability > 75:
            if show_logs: logging.info(f"{self.name} accepts the offer for {requested_quantity} units of {product} at {price_to_offer} per unit.")
            return {
                'product': product,
                'quantity': requested_quantity,
                'price': price_to_offer
            }

        # If the offer is not acceptable, propose a counteroffer
        counter_price = round(price_to_offer * 1.10, 2)  # Increase price by 10% for counteroffer
        if show_logs: logging.info(f"{self.name} counters the company's offer with {requested_quantity} units at {counter_price} per unit.")
        return {
            'product': product,
            'quantity': requested_quantity,
            'price': counter_price
        }

    def calculate_price_based_on_quantity(self, quantity, available_quantity, min_price):
        """
        Use fuzzy logic to calculate the price based on the requested quantity and available stock.
        :param quantity: The quantity requested by the buyer
        :param available_quantity: The available stock the supplier has
        :param min_price: The minimum price the supplier is willing to sell at
        :return: The price the supplier is willing to offer based on fuzzy logic
        """
        # Define fuzzy variables
        quantity_var = ctrl.Antecedent(np.arange(0, available_quantity + 1, 1), 'quantity')
        price = ctrl.Consequent(np.arange(min_price, min_price * 2, 1), 'price')

        # Membership functions for quantity
        quantity_var['low'] = fuzz.trimf(quantity_var.universe, [0, 0, available_quantity * 0.5])
        quantity_var['medium'] = fuzz.trimf(quantity_var.universe, [available_quantity * 0.3, available_quantity * 0.5, available_quantity * 0.7])
        quantity_var['high'] = fuzz.trimf(quantity_var.universe, [available_quantity * 0.6, available_quantity, available_quantity])

        # Membership functions for price
        price['low'] = fuzz.trimf(price.universe, [min_price, min_price, min_price * 1.2])
        price['medium'] = fuzz.trimf(price.universe, [min_price * 1.1, min_price * 1.5, min_price * 1.8])
        price['high'] = fuzz.trimf(price.universe, [min_price * 1.5, min_price * 2, min_price * 2])

        # Define fuzzy rules
        rule1 = ctrl.Rule(quantity_var['low'], price['high'])  # Low quantity, supplier wants higher price
        rule2 = ctrl.Rule(quantity_var['medium'], price['medium'])  # Medium quantity, medium price
        rule3 = ctrl.Rule(quantity_var['high'], price['low'])  # High quantity, discount price

        # Create control system and simulation
        price_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        price_sim = ctrl.ControlSystemSimulation(price_ctrl)

        # Input the requested quantity
        price_sim.input['quantity'] = quantity

        # Perform fuzzy computation
        price_sim.compute()

        # Output the fuzzy-calculated price
        calculated_price = price_sim.output['price']

        # Ensure price is not below minimum
        return max(calculated_price, min_price)



    def evaluate_counteroffer(self, offer, counteroffer, show_logs):
        """
        The supplier evaluates the company's counteroffer and decides whether to accept it or propose a new offer.
        Ensures the counteroffer is not worse than the company's counteroffer.
        
        :param offer: The supplier's original offer
        :param counteroffer: The company's counteroffer
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        if counteroffer is None:
            if show_logs: logging.info(f"{self.name} did not receive a valid counteroffer from the company.")
            return False

        if show_logs:
            logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        product = counteroffer['product']
        offered_price = counteroffer['price']
        requested_quantity = counteroffer['quantity']

        # Retrieve supplier's conditions
        supplier_conditions = self.beliefs['supplier_conditions'].get(product, {})
        min_price = supplier_conditions.get('min_price', None)
        available_quantity = supplier_conditions.get('quantity', 0)

        if min_price is None:
            if show_logs: logging.info(f"{self.name} does not supply {product}.")
            return False

        # Use `evaluate_offer` to check if the current counteroffer is acceptable
        simulated_offer = {
            'product': product,
            'quantity': requested_quantity,
            'price': offered_price
        }
        
        # Check acceptance of the counteroffer directly
        evaluated_offer = self.evaluate_offer(simulated_offer, False)
        
        # If `evaluate_offer` accepts, return True
        if evaluated_offer:
            return True

        # If not accepted, create a new counteroffer
        quantity_to_sell = int(self.calculate_quantity_based_on_price(offered_price, available_quantity, min_price))
        counter_price = max(offered_price, self.calculate_price_based_on_quantity(quantity_to_sell, available_quantity, min_price))

        # Avoid deadlocks by ensuring a reasonable price adjustment
        counter_price = max(counter_price, offered_price * 1.05)
        if abs(counter_price - offered_price) < 0.01:
            if show_logs: logging.info(f"Negotiation deadlock detected for {product}. Terminating negotiation.")
            return False

        if show_logs: logging.info(f"{self.name} counters with {quantity_to_sell} units at {counter_price} per unit.")
        return {
            'product': product,
            'quantity': quantity_to_sell,
            'price': counter_price
        }




    def calculate_quantity_based_on_price(self, price, available_quantity, min_price):
        """
        Use fuzzy logic to calculate the quantity based on the offered price and available stock.
        :param price: The price offered by the buyer
        :param available_quantity: The available stock the supplier has
        :param min_price: The minimum price the supplier is willing to sell at
        :return: The quantity the supplier is willing to offer based on fuzzy logic
        """
        # Define fuzzy variables
        price_var = ctrl.Antecedent(np.arange(min_price, min_price * 2, 1), 'price')
        quantity = ctrl.Consequent(np.arange(0, available_quantity + 1, 1), 'quantity')

        # Membership functions for price
        price_var['low'] = fuzz.trimf(price_var.universe, [min_price, min_price, min_price * 1.2])
        price_var['medium'] = fuzz.trimf(price_var.universe, [min_price * 1.1, min_price * 1.5, min_price * 1.8])
        price_var['high'] = fuzz.trimf(price_var.universe, [min_price * 1.5, min_price * 2, min_price * 2])

        # Membership functions for quantity
        quantity['small'] = fuzz.trimf(quantity.universe, [0, 0, available_quantity * 0.4])
        quantity['medium'] = fuzz.trimf(quantity.universe, [available_quantity * 0.3, available_quantity * 0.5, available_quantity * 0.7])
        quantity['large'] = fuzz.trimf(quantity.universe, [available_quantity * 0.6, available_quantity, available_quantity])

        # Define fuzzy rules
        rule1 = ctrl.Rule(price_var['low'], quantity['small'])  # Low price, small quantity
        rule2 = ctrl.Rule(price_var['medium'], quantity['medium'])  # Medium price, medium quantity
        rule3 = ctrl.Rule(price_var['high'], quantity['large'])  # High price, large quantity

        # Create control system and simulation
        quantity_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        quantity_sim = ctrl.ControlSystemSimulation(quantity_ctrl)

        # Input the offered price
        quantity_sim.input['price'] = price

        # Perform fuzzy computation
        quantity_sim.compute()

        # Output the fuzzy-calculated quantity
        calculated_quantity = quantity_sim.output['quantity']

        # Ensure calculated quantity does not exceed available stock
        return min(calculated_quantity, available_quantity)
