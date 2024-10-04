import random
import logging
from BaseAgent import BDI_Agent
from Environment import MarketEnvironment
import json
 
des_int_json_file = open('./Desires-Intentions/Suppliers.json',)
int_exec_json_file = open('./Intentions-Execution/Suppliers.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class SupplierAgent(BDI_Agent):
    def __init__(self, name,products):
        super().__init__(name)
        self.beliefs['supplier_conditions']=products
        self.beliefs['r_offers']=[]
        self.beliefs['s_offers']=[]
        self.beliefs['agreements']=[]
    
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
'''
        for product, demand in market_env.public_variables['market_demand'].items():
            supplier_data = market_env.hidden_variables['supplier_conditions'][self.name].get(product, None)
            if supplier_data and supplier_data['quantity'] > 0:
                supply_quantity = min(demand + 10, supplier_data['quantity']) if demand > 0 else random.randint(1, supplier_data['quantity'])
                
                market_price = market_env.public_variables['product_prices'].get(self.name, {}).get(product, 0)
                if market_price >= supplier_data['min_price']:
                    market_env.public_variables['market_demand'][product] = max(0, demand - supply_quantity)
                    self.update_stock(product, supply_quantity)
                    
                    market_env.hidden_variables['supplier_conditions'][self.name][product]['quantity'] -= supply_quantity
                    logging.info(f"{self.name} has supplied {supply_quantity} units of {product} at price {market_price} (min price: {supplier_data['min_price']}).")
                
                else:
                    logging.info(f"{self.name} could not supply {product} as the market price {market_price} is below the minimum price {supplier_data['min_price']}.")
            else:
                logging.info(f"{self.name} has no stock or data for {product}.")

    def update_stock(self, product, quantity):
        if product in market_env.public_variables['available_products']:
            market_env.public_variables['available_products'][product] += quantity
        else:
            market_env.public_variables['available_products'][product] = quantity
        logging.info(f"{self.name} has updated the stock of {product}. New quantity: {market_env.public_variables['available_products'][product]}")'''