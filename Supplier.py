import random
import logging
from BaseAgent import BDI_Agent
from Environment import MarketEnvironment
import json
from Knowledge import *
 
des_int_json_file = open('./Desires-Intentions/Suppliers.json',)
int_exec_json_file = open('./Intentions-Execution/Suppliers.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class SupplierAgent(BDI_Agent):
    def __init__(self, name, products, knowledge):
        super().__init__(name)
        self.beliefs['supplier_conditions']=products
        self.agreements = []
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

        # Adjust quantity if stock is less than requested
        if requested_quantity > available_quantity:
            if show_logs: logging.info(f"{self.name} does not have enough stock to supply {requested_quantity} units of {product}. Offering available stock: {available_quantity}")
            requested_quantity = available_quantity  # Adjust quantity to available stock

        # Use fuzzy logic to calculate the price based on the adjusted quantity
        price_to_sell = self.calculate_price_based_on_quantity(requested_quantity, available_quantity, min_price)

        # Evaluate the acceptability of the offer using fuzzy logic
        price_percentage = (price_to_sell - min_price) / min_price * 100
        quantity_percentage = (requested_quantity / available_quantity) * 100
        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        # If acceptability is high and stock is sufficient
        if acceptability > 75 and requested_quantity == offer['quantity']:
            if show_logs: logging.info(f"{self.name} accepts the offer for {requested_quantity} units of {product} at {price_to_sell} per unit.")
            return {
                'product': product,
                'quantity': requested_quantity,
                'price': price_to_sell
            }

        # If stock is less than requested, propose a counteroffer with the adjusted quantity and price
        if show_logs: logging.info(f"{self.name} counters the company's offer with {requested_quantity} units at {price_to_sell} per unit.")
        return {
            'product': product,
            'quantity': requested_quantity,
            'price': price_to_sell
        }

    
    def calculate_price_based_on_quantity(self, quantity, available_quantity, min_price):
        """
        Use fuzzy logic to calculate the price based on the requested quantity and the available stock.
        :param quantity: The quantity requested by the buyer
        :param available_quantity: The available stock the supplier has
        :param min_price: The minimum price the supplier is willing to sell at
        :return: The price the supplier is willing to offer based on fuzzy logic
        """
        # Ensure available_quantity is greater than 0 to avoid invalid membership function
        if available_quantity <= 0:
            return min_price * 1.10  # Default to a higher price in case of zero stock

        # Define fuzzy variables
        quantity_var = ctrl.Antecedent(np.arange(0, available_quantity + 1, 1), 'quantity')
        price = ctrl.Consequent(np.arange(min_price, min_price * 2, 1), 'price')  # Price range between min_price and twice the min_price

        # Membership functions for quantity
        quantity_var['low'] = fuzz.trimf(quantity_var.universe, [0, 0, max(available_quantity * 0.5, 1)])
        quantity_var['medium'] = fuzz.trimf(quantity_var.universe, [available_quantity * 0.3, available_quantity * 0.5, available_quantity * 0.7])
        quantity_var['high'] = fuzz.trimf(quantity_var.universe, [available_quantity * 0.6, available_quantity, available_quantity])

        # Membership functions for price
        price['low'] = fuzz.trimf(price.universe, [min_price, min_price, min_price * 1.2])
        price['medium'] = fuzz.trimf(price.universe, [min_price * 1.1, min_price * 1.5, min_price * 1.8])
        price['high'] = fuzz.trimf(price.universe, [min_price * 1.5, min_price * 2, min_price * 2])

        # Define fuzzy rules
        rule1 = ctrl.Rule(quantity_var['low'], price['high'])  # Small quantity, supplier wants higher price
        rule2 = ctrl.Rule(quantity_var['medium'], price['medium'])  # Medium quantity, medium price
        rule3 = ctrl.Rule(quantity_var['high'], price['low'])  # Large quantity, supplier gives discount

        # Create control system and simulation
        price_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        price_sim = ctrl.ControlSystemSimulation(price_ctrl)

        # Input the requested quantity
        price_sim.input['quantity'] = quantity

        # Perform fuzzy computation
        price_sim.compute()

        # Output the fuzzy-calculated price
        calculated_price = price_sim.output['price']

        return calculated_price



    def evaluate_counteroffer(self, offer, counteroffer, show_logs):
        """
        The supplier evaluates the company's counteroffer and decides whether to accept it or propose a new offer.
        If the requested quantity exceeds the available stock, the supplier directly returns a counteroffer with adjusted quantity and price.
        
        :param offer: The supplier's original offer
        :param counteroffer: The company's counteroffer
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        if counteroffer is None:
            if show_logs: logging.info(f"{self.name} did not receive a valid counteroffer from the company.")
            return False

        if show_logs: logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        product = counteroffer['product']
        requested_quantity = counteroffer['quantity']

        # Retrieve the supplier's conditions for the product
        supplier_conditions = self.beliefs['supplier_conditions'].get(product, {})
        min_price = supplier_conditions.get('min_price', None)
        available_quantity = supplier_conditions.get('quantity', 0)

        if min_price is None:
            if show_logs: logging.info(f"{self.name} does not supply {product}.")
            return False

        # If the requested quantity exceeds the available stock, return a counteroffer with adjusted quantity and price
        if requested_quantity > available_quantity:
            if show_logs: logging.info(f"{self.name} does not have enough stock to supply {requested_quantity} units of {product}. Offering available stock: {available_quantity}")
            
            # Calculate the new price based on the available quantity
            counter_price = self.calculate_price_based_on_quantity(available_quantity, available_quantity, min_price)
            
            # Return the counteroffer with adjusted quantity and price
            if show_logs: logging.info(f"{self.name} counters the company's offer with {available_quantity} units at {counter_price} per unit.")
            return {
                'product': product,
                'quantity': available_quantity,
                'price': counter_price
            }

        # If the requested quantity is within stock limits, use fuzzy logic to evaluate the counteroffer
        price_to_sell = self.calculate_price_based_on_quantity(requested_quantity, available_quantity, min_price)

        # Evaluate the acceptability of the counteroffer using fuzzy logic
        price_percentage = (price_to_sell - min_price) / min_price * 100
        quantity_percentage = (requested_quantity / available_quantity) * 100
        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        # Decision: Accept or Counteroffer
        if acceptability > 75:
            if show_logs: logging.info(f"{self.name} accepts the counteroffer for {requested_quantity} units of {product} at {price_to_sell} per unit.")
            return {
                'product': product,
                'quantity': requested_quantity,
                'price': price_to_sell
            }

        # If the counteroffer is not acceptable, propose a new counteroffer with adjusted price
        counter_price = price_to_sell * 1.10  # Increase price by 10% in counteroffer
        logging.info(f"{self.name} counters the company's offer with {requested_quantity} units at {counter_price} per unit.")
        return {
            'product': product,
            'quantity': requested_quantity,
            'price': counter_price
        }
