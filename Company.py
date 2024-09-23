import logging
from BaseAgent import BDI_Agent
import json

des_int_json_file = open('./Desires-Intentions/Companies.json',)
int_exec_json_file = open('./Intentions-Execution/Companies.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def __init__(self, name):
        super().__init__(name)
        self.beliefs['revenue']={}
        self.beliefs['subproduct_stock']={}


    def perceive_environment(self,market_env):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['subproducts'] = market_env.public_variables['subproducts']
        self.beliefs['subproduct_suppliers']=market_env.public_variables['subproduct_suppliers']
        self.beliefs['r_offers']=[]
        self.beliefs['s_offers']=[]
        self.beliefs['agreements']=[]

        logging.info(f"{self.name} perceived the environment and updated beliefs.")

    def form_desires(self):
        for product, _ in self.beliefs['product_prices'].get(self.name, {}).items():
            stock = self.beliefs['product_prices'][self.name][product]['stock']
            subproducts_needed = self.beliefs['subproducts'].get(product, {})

            if stock == 0:
                self.desires.append('maximize_profit')
                logging.info(f"{self.name} formed desire to maximize profit for {product}.")
            else:
                self.desires.append('expand_market_share')
                logging.info(f"{self.name} formed desire to expand market share for {product}.")

            if subproducts_needed:
                self.desires.append('secure_subproducts')
                logging.info(f"{self.name} formed desire to secure subproducts for {product}.")
    
    def plan_intentions(self):
        for desire in self.desires:
            self.intentions += desires_intentions[desire]
            logging.info(f"{self.name} has planned to {desires_intentions[desire]}")

    def execute_intention(self, intention, market_env):
        for intention in self.intentions:
            execution = intentions_execution[intention]
            eval(execution["action"])
            self.intentions.remove(intention)
            logging.info(execution["log"])

    def adjust_price(self, adjustment,market_env):
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price['price'] * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product]['price'] = new_price
            logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")

    def secure_subproduct_supply(self):
        for product in self.beliefs['product_prices'].get(self.name, {}):
            subproducts = self.beliefs['subproducts'].get(product, {})
            for subproduct, quantity in subproducts.items():
                logging.info(f"{self.name} is securing supply for {quantity} units of subproduct: {subproduct}.")
                # Add logic to secure subproduct supply (negotiate with suppliers)