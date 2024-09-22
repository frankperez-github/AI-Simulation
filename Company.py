import logging
from BaseAgent import BDI_Agent

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
                self.desires['maximize_profit'] = True
                logging.info(f"{self.name} formed desire to maximize profit for {product}.")
            else:
                self.desires['expand_market_share'] = True
                logging.info(f"{self.name} formed desire to expand market share for {product}.")

            if subproducts_needed:
                self.desires['secure_subproducts'] = True
                logging.info(f"{self.name} formed desire to secure subproducts for {product}.")
    
    def plan_intentions(self):
        if self.desires.get('maximize_profit'):
            self.intentions.append('increase_prices')
            logging.info(f"{self.name} planned to increase prices.")
        if self.desires.get('expand_market_share'):
            self.intentions.append('lower_prices')
            logging.info(f"{self.name} planned to lower prices.")
        if self.desires.get('secure_subproducts'):
            self.intentions.append('secure_subproduct_supply')
            logging.info(f"{self.name} planned to secure subproduct supply.")

    def execute_intention(self, intention,market_env):
        if intention == 'increase_prices':
            self.adjust_price(0.1,market_env)
            logging.info(f"{self.name} executed intention to increase prices.")
        elif intention == 'lower_prices':
            self.adjust_price(-0.1,market_env)
            logging.info(f"{self.name} executed intention to lower prices.")
        elif intention == 'secure_subproduct_supply':
            self.secure_subproduct_supply()
            logging.info(f"{self.name} executed intention to secure subproduct supply.")
        self.intentions.remove(intention)

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