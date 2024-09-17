import random
import logging
from BaseAgent import BDI_Agent
from Environment import market_env

# Configurar el logger para mostrar solo mensajes
logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CustomerAgent(BDI_Agent):
    def __init__(self, name, market_env,actitud):
        super().__init__(name, market_env)
        self.beliefs['actitud']=actitud
        self.beliefs['budget'] = 0
        self.beliefs['quintil'] = -1
        self.beliefs['alpha'] = {}
        self.beliefs['demand'] = {}
        self.beliefs['expenditure'] = {}
        self.beliefs['utility'] = {}


    def perceive_environment(self):
        self.beliefs['available_products'] = market_env.public_variables['available_products']
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['company_popularity']=market_env.public_variables['company_popularity']
        logging.info(f"{self.name} has perceived the environment and updated beliefs about available products and prices.")

    def form_desires(self):
        self.desires['buy_products'] = random.choice([True, False])
        logging.info(f"{self.name} formed the desire to buy products: {self.desires['buy_products']}")

    def plan_intentions(self):
        if self.desires.get('buy_products'):
            if self.beliefs['actitud']=='tacanno':
                self.intentions.append('buy_cheap_products')
                logging.info(f"{self.name} planned the intention to buy the cheapest products.")
            elif self.beliefs['actitud']=='populista':
                self.intentions.append('buy_products_by_popularity')
                logging.info(f"{self.name} planned the intention to buy products from most popular companies.")            
            elif self.beliefs['actitud']=='random':
                self.intentions.append('buy_products_randomly')
                logging.info(f"{self.name} planned the intention to buy products randomly.") 
            elif self.beliefs['actitud']=='precavido':
                self.intentions.append('buy_products_but_think_about_it')
                logging.info(f"{self.name} planned the intention to buy products.")  
   
    def execute_intention(self, intention):
        if intention == 'buy_cheap_products':
            logging.info(f"{self.name} will execute the intention: {intention}")
            selected_products, cheapest_companies, quantities = self.buy_cheapest_products()
            if selected_products:
                self.buy(selected_products, cheapest_companies, quantities)
        elif intention == 'buy_products_by_popularity':
            logging.info(f"{self.name} will execute the intention: {intention}")
            selected_products, cheapest_companies, quantities = self.buy_products_by_popularity()
            if selected_products:
                self.buy(selected_products, cheapest_companies, quantities)  
        elif intention == 'buy_products_randomly':
            logging.info(f"{self.name} will execute the intention: {intention}")
            selected_products, cheapest_companies, quantities = self.buy_products_randomlys()
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
            if quantity>0:
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

    def buy_cheapest_products(self):
        available_products = set()
        for branch in self.beliefs['product_prices']:
            available_products = available_products.union(set(self.beliefs['product_prices'][branch]))

        if not available_products:
            logging.warning(f"{self.name} found no available products to buy.")
            return [], [], [], []

        selected_products = list(available_products)

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


    def buy_products_by_popularity(self):
            available_products = set()
            for branch in self.beliefs['product_prices']:
                available_products = available_products.union(set(self.beliefs['product_prices'][branch]))

            if not available_products:
                logging.warning(f"{self.name} found no available products to buy.")
                return [], [], [], []

            selected_products = list(available_products)

            populars_companies = []
            quantities = []

            popular_company = None
            pop = float('inf')*-1

            for company, popularity in self.beliefs['company_popularity'].items():
                if popularity>pop:
                    pop=popularity
                    popular_company=company

            for selected_product in selected_products:
                if selected_product in self.beliefs['product_prices'][popular_company]:
                    quantity = int(self.beliefs['alpha'][market_env.public_variables['product_dict'][selected_product]] * self.beliefs['budget'] / self.beliefs['product_prices'][popular_company][selected_product])
                    populars_companies.append(popular_company)
                    quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {cheapest_companies}")
            return selected_products, populars_companies, quantities


    def buy_products_randomly(self):
            available_products = set()
            for branch in self.beliefs['product_prices']:
                available_products = available_products.union(set(self.beliefs['product_prices'][branch]))

            if not available_products:
                logging.warning(f"{self.name} found no available products to buy.")
                return [], [], [], []

            selected_products = list(available_products)

            companies = []
            quantities = []

            for selected_product in selected_products:

                comp=[x for x in self.self.beliefs['product_prices'] if selected_product in self.beliefs['product_prices'][x]]
                company=random.choice(comp)
                quantity = int(self.beliefs['alpha'][market_env.public_variables['product_dict'][selected_product]] * self.beliefs['budget'] / self.beliefs['product_prices'][company][selected_product])
                companies.append(company)
                quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {cheapest_companies}")
            return selected_products,companies, quantities
