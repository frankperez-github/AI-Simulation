import logging
from BaseAgent import BDI_Agent
from Environment import market_env

# Configurar el logger para registrar solo mensajes
logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def perceive_environment(self):
        # Actualizar las creencias sobre precios, competencia y demanda del mercado
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['competition_levels'] = market_env.public_variables['competition_levels']
        self.beliefs['market_demand'] = market_env.public_variables['market_demand']
        logging.info(f"{self.name} perceived the environment and updated beliefs.")

    def form_desires(self):
        # Formar deseos según el nivel de competencia
        for product, _ in self.beliefs['product_prices'].get(self.name, {}).items():
            competition_level = self.beliefs['competition_levels'].get(product, 0)

            if competition_level > 5:
                self.desires['maximize_profit'] = True
                logging.info(f"{self.name} formed desire to maximize profit for {product}.")
            else:
                self.desires['expand_market_share'] = True
                logging.info(f"{self.name} formed desire to expand market share for {product}.")

    def plan_intentions(self):
        # Planificar intenciones según los deseos formados
        if self.desires.get('maximize_profit'):
            self.intentions.append('increase_prices')
            logging.info(f"{self.name} planned to increase prices.")
        if self.desires.get('expand_market_share'):
            self.intentions.append('lower_prices')
            logging.info(f"{self.name} planned to lower prices.")

    def execute_intention(self, intention):
        # Ejecutar las intenciones de la empresa
        if intention == 'increase_prices':
            self.adjust_price(0.1)
            logging.info(f"{self.name} executed intention to increase prices.")
        elif intention == 'lower_prices':
            self.adjust_price(-0.1)
            logging.info(f"{self.name} executed intention to lower prices.")
        self.intentions.remove(intention)

    def adjust_price(self, adjustment):
        # Ajustar los precios de los productos de la empresa
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product] = new_price
            logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")
