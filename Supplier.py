import random
import logging
from BaseAgent import BDI_Agent
from Environment import market_env

logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class SupplierAgent(BDI_Agent):
    def __init__(self, name):
        super().__init__(name)
        self.initialize_supplier()
    
    def initialize_supplier(self):
        market_env.hidden_variables['supplier_conditions'][self.name] = {
                'product_1': {'quantity': 100, 'min_price': 5.0},
                'product_2': {'quantity': 200, 'min_price': 10.0}
        }

    def perceive_environment(self):
        self.beliefs['market_demand'] = market_env.public_variables['market_demand']
        self.beliefs['available_products'] = market_env.public_variables['available_products']
        self.beliefs['supplier_conditions'] = market_env.hidden_variables['supplier_conditions'].get(self.name, {})
        logging.info(f"{self.name} has perceived the environment and updated beliefs about market demand and available products.")

    def form_desires(self):
        self.desires['supply_products'] = random.choice([True, False])
        logging.info(f"{self.name} has formed desires. Supply products: {self.desires['supply_products']}")

    def plan_intentions(self):
        if self.desires.get('supply_products'):
            self.intentions.append('supply_to_companies')
            logging.info(f"{self.name} has planned to supply products to companies.")

    def execute_intention(self, intention):
        if intention == 'supply_to_companies':
            self.supply_products()
        self.intentions.remove(intention)
        logging.info(f"{self.name} has executed the intention to {intention}.")

    def supply_products(self):
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
        logging.info(f"{self.name} has updated the stock of {product}. New quantity: {market_env.public_variables['available_products'][product]}")