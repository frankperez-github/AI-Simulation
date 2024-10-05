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
    
    #def initialize_supplier(self):
    #    market_env.hidden_variables['supplier_conditions'][self.name] = {
    #            'product_1': {'quantity': 100, 'min_price': 5.0, 'start_price':7},
    #            'product_2': {'quantity': 200, 'min_price': 10.0, 'start_price':13}
    #    }

    def perceive_environment(self,market_env):
        self.beliefs['product_prices']=market_env.public_variables['product_prices']
        self.beliefs['subproducts']=market_env.public_variables['subproducts']
        #self.beliefs['market_demand'] = market_env.public_variables['market_demand']
        #self.beliefs['available_products'] = market_env.public_variables['available_products']
        logging.info(f"{self.name} has perceived the environment and updated beliefs about market demand and available products.")

    def form_desires(self):
        supply = random.choice([True, False]) 
        if supply:
            self.desires.append('supply_products')
        logging.info(f"{self.name} has formed desires. Supply products: {supply}")

    def plan_intentions(self):
        for desire in self.desires:
            self.intentions += desires_intentions[desire]
            logging.info(f"{self.name} has planned to {desires_intentions[desire]}")
        self.desires=[]

    def execute_intention(self,intention, market_env):
        execution = intentions_execution[intention]
        for action in execution["actions"]:
            eval(action)
        logging.info(eval(execution["log"]))

    def supply_products(self, market_env: MarketEnvironment):
        for company in self.beliefs['product_prices']:
            for product in self.beliefs['product_prices'][company]:
                subproducts=self.beliefs['subproducts'][product]
                for subproduct in subproducts:
                    if subproduct in self.beliefs['supplier_conditions']:
                        market_env.public_variables['companies'][company].subproduct_stock[subproduct]['stock']+=100

    def evaluate_offer(self, offer):
        """
        The supplier evaluates the offer using fuzzy logic to decide whether to accept, reject, or make a counteroffer.
        :param offer: The initial offer from the company
        """
        product = offer['product']
        quantity = offer['quantity']
        price = offer['price']
        
        # Retrieve the supplier's conditions for the product
        supplier_conditions = self.beliefs['supplier_conditions'].get(product, {})
        min_price = supplier_conditions.get('min_price', None)
        available_quantity = supplier_conditions.get('quantity', 0)
        
        if min_price is None:
            logging.info(f"{self.name} does not supply {product}.")
            return None
        
        price_percentage = (price - min_price) / min_price * 100
        quantity_percentage = (quantity / available_quantity) * 100 if available_quantity > 0 else 0
        
        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)
        
        if acceptability > 75:
            logging.info(f"{self.name} accepts the offer for {quantity} units of {product} at {price} per unit.")
            return offer  
        else:
            counter_quantity = min(available_quantity, quantity)
            counter_price = max(min_price, price * 1.10)
            counter_offer = {
                'product': product,
                'quantity': counter_quantity,
                'price': counter_price
            }
            logging.info(f"{self.name} counters the offer with {counter_quantity} units of {product} at {counter_price} per unit.")
            return counter_offer


    def evaluate_counteroffer(self, offer, counteroffer):
        """
        The company evaluates the supplier's counteroffer using fuzzy logic to decide whether to accept or propose a new offer.
        :param offer: The company's original offer
        :param counteroffer: The supplier's counteroffer
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        if counteroffer is None:
            logging.info(f"{self.name} did not receive a valid counteroffer from the supplier.")
            return False

        logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        # Normalize price and quantity for fuzzy logic input (percentage)
        price_percentage = (counteroffer['price'] - offer['price']) / offer['price'] * 100
        quantity_percentage = (counteroffer['quantity'] / offer['quantity']) * 100

        # Use the Company_Knowledge class to evaluate the acceptability of the counteroffer
        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        # Decision based on fuzzy logic output
        if acceptability > 75: 
            logging.info(f"{self.name} accepts the counteroffer.")
            return True  # Agreement reached

        # Otherwise, propose a new counteroffer
        new_price = (offer['price'] + counteroffer['price']) / 2
        new_quantity = (offer['quantity'] + counteroffer['quantity']) / 2
        new_offer = {
            'product': offer['product'],
            'quantity': new_quantity,
            'price': new_price
        }

        logging.info(f"{self.name} counters the supplier's offer with {new_quantity} units at {new_price} per unit.")
        return new_offer


