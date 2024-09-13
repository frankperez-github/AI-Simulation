import random
import logging
from BaseAgent import BDI_Agent
from Environment import market_env

# Configurar el logger para mostrar solo mensajes
logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CustomerAgent(BDI_Agent):
    def __init__(self, name, market_env):
        super().__init__(name, market_env)
        self.beliefs['budget'] = 0
        self.beliefs['quintil'] = -1
        self.beliefs['alpha'] = {}
        self.beliefs['demand'] = {}
        self.beliefs['expenditure'] = {}
        self.beliefs['utility'] = {}

    def perceive_environment(self):
        self.beliefs['available_products'] = market_env.public_variables['available_products']
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        logging.info(f"{self.name} has perceived the environment and updated beliefs about available products and prices.")

    def form_desires(self):
        self.desires['buy_products'] = random.choice([True, False])
        logging.info(f"{self.name} formed the desire to buy products: {self.desires['buy_products']}")

    def plan_intentions(self):
        if self.desires.get('buy_products'):
            self.intentions.append('buy_cheap_products')
            logging.info(f"{self.name} planned the intention to buy the cheapest products.")

    def execute_intention(self, intention):
        if intention == 'buy_cheap_products':
            logging.info(f"{self.name} will execute the intention: {intention}")
            selected_products, cheapest_companies, quantities = self.buy_random_cheapest_products()
            if selected_products:
                self.buy(selected_products, cheapest_companies, quantities)
        # Remover la intención ejecutada
        self.intentions.remove(intention)

    def buy(self, selected_products, cheapest_companies, quantities):
        for i in range(len(selected_products)):
            selected_product = selected_products[i]
            cheapest_company = cheapest_companies[i]
            quantity = quantities[i]

            available_stock = market_env.public_variables['available_products'].get(selected_product, 0)
            if available_stock >= quantity:
                # Reduce stock
                market_env.public_variables['available_products'][selected_product] -= quantity

                # Obtener el ingreso bruto por unidad para el producto
                revenue_per_unit = market_env.public_variables['product_gross_income'][cheapest_company][selected_product]

                # Actualizar los ingresos de la empresa
                if cheapest_company in market_env.public_variables['revenue']:
                    market_env.public_variables['revenue'][cheapest_company] += revenue_per_unit * quantity
                else:
                    market_env.public_variables['revenue'][cheapest_company] = revenue_per_unit * quantity

                # Incrementar la demanda del mercado
                if selected_product in market_env.public_variables['market_demand']:
                    market_env.public_variables['market_demand'][selected_product] += quantity
                else:
                    market_env.public_variables['market_demand'][selected_product] = quantity

                # Actualizar las tendencias del mercado
                if selected_product in market_env.public_variables['market_trends']:
                    market_env.public_variables['market_trends'][selected_product] += 1
                else:
                    market_env.public_variables['market_trends'][selected_product] = 1

                # Registrar la compra en el log
                logging.info(f"{self.name} bought {quantity} units of {selected_product} from {cheapest_company}. Gross income per unit: {revenue_per_unit}.")
            else:
                # No hay suficiente stock
                logging.warning(f"{self.name} attempted to buy {quantity} units of {selected_product}, but only {available_stock} units were available.")

    def buy_random_cheapest_products(self):
        available_products = set()
        for branch in self.beliefs['product_prices']:
            available_products = available_products.union(set(self.beliefs['product_prices'][branch]))

        if not available_products:
            logging.warning(f"{self.name} found no available products to buy.")
            return [], [], [], []

        num_products_to_buy = random.randint(1, 6)
        selected_products = random.sample(list(available_products), min(num_products_to_buy, len(available_products)))

        cheapest_companies = []
        quantities = []

        for selected_product in selected_products:
            cheapest_company = None
            cheapest_price = float('inf')

            for company, products in self.beliefs['product_prices'].items():
                if selected_product in products:
                    price = products[selected_product]
                    if price < cheapest_price:
                        cheapest_price = price
                        cheapest_company = company

            quantity = int(self.beliefs['alpha'][market_env.public_variables['product_dict'][selected_product]] * self.beliefs['budget'] / cheapest_price)
            cheapest_companies.append(cheapest_company)
            quantities.append(quantity)

        logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {cheapest_companies}")
        return selected_products, cheapest_companies, quantities
