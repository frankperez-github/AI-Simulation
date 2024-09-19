import logging
from BaseAgent import BDI_Agent
from Environment import market_env

# Configurar el logger para registrar solo mensajes
logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def perceive_environment(self):
        # Update beliefs about prices, competition, demand, and subproducts
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['competition_levels'] = market_env.public_variables['competition_levels']
        self.beliefs['market_demand'] = market_env.public_variables['market_demand']
        self.beliefs['subproducts'] = market_env.public_variables['subproducts']
        logging.info(f"{self.name} perceived the environment and updated beliefs.")

    def form_desires(self):
        # Form desires based on competition level and subproduct needs
        for product, _ in self.beliefs['product_prices'].get(self.name, {}).items():
            competition_level = self.beliefs['competition_levels'].get(product, 0)
            subproducts_needed = self.beliefs['subproducts'].get(product, [])

            if competition_level > 5:
                self.desires['maximize_profit'] = True
                logging.info(f"{self.name} formed desire to maximize profit for {product}.")
            else:
                self.desires['expand_market_share'] = True
                logging.info(f"{self.name} formed desire to expand market share for {product}.")

            # Example: Consider subproducts in desire formation
            if subproducts_needed:
                self.desires['secure_subproducts'] = True
                logging.info(f"{self.name} formed desire to secure subproducts for {product}.")

    def plan_intentions(self):
        # Plan intentions based on desires
        if self.desires.get('maximize_profit'):
            self.intentions.append('increase_prices')
            logging.info(f"{self.name} planned to increase prices.")
        if self.desires.get('expand_market_share'):
            self.intentions.append('lower_prices')
            logging.info(f"{self.name} planned to lower prices.")
        if self.desires.get('secure_subproducts'):
            self.intentions.append('secure_subproduct_supply')
            logging.info(f"{self.name} planned to secure subproduct supply.")

    def execute_intention(self, intention):
        # Execute the intentions of the company
        if intention == 'increase_prices':
            self.adjust_price(0.1)
            logging.info(f"{self.name} executed intention to increase prices.")
        elif intention == 'lower_prices':
            self.adjust_price(-0.1)
            logging.info(f"{self.name} executed intention to lower prices.")
        elif intention == 'secure_subproduct_supply':
            self.secure_subproduct_supply()
            logging.info(f"{self.name} executed intention to secure subproduct supply.")
        self.intentions.remove(intention)

    def adjust_price(self, adjustment):
        # Adjust the prices of the company's products
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product] = new_price
            logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")

    def secure_subproduct_supply(self):
        # Secure the subproducts needed for the company's products
        for product in self.beliefs['product_prices'].get(self.name, {}):
            subproducts = self.beliefs['subproducts'].get(product, [])
            logging.info(f"{self.name} is securing supply for subproducts: {', '.join(subproducts)}.")
            # Add logic to secure subproduct supply (e.g., negotiate with suppliers)
