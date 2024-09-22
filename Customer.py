import random
import logging
from BaseAgent import BDI_Agent
import numpy as np
from Environment import MarketEnvironment

# Configurar el logger para mostrar solo mensajes
logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CustomerAgent(BDI_Agent):
    def __init__(self, name,actitud):
        super().__init__(name)
        self.beliefs['attitude']=actitud
        self.beliefs['budget'] = 0
        self.beliefs['quintil'] = -1
        self.beliefs['alpha'] = {}
        self.beliefs['demand'] = {}
        self.beliefs['expenditure'] = {}
        self.beliefs['utility'] = {}



    def perceive_environment(self,market_env:MarketEnvironment):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['company_popularity']=market_env.public_variables['company_popularity']
        logging.info(f"{self.name} has perceived the environment and updated beliefs about available products and prices.")

    def form_desires(self):
        self.desires['buy_products'] = [product for product in self.beliefs['alpha'] if self.beliefs['alpha'][product]>0]
        logging.info(f"{self.name} formed the desire to buy products: {self.desires['buy_products']}")

    def plan_intentions(self):
        self.intentions={}
        if self.beliefs['attitude']=='stingy':
            self.intentions['buy_products']=self.buy_cheapest_products(self.desires['buy_products'])
            logging.info(f"{self.name} planned the intention to buy the cheapest products.")
        elif self.beliefs['attitude']=='populist':
            self.intentions['buy_products']=self.buy_products_by_popularity(self.desires['buy_products'])                        
        elif self.beliefs['attitude']=='random':
            self.intentions['buy_products']=self.buy_products_randomly(self.desires['buy_products'])
            logging.info(f"{self.name} planned the intention to buy products randomly.") 
        elif self.beliefs['attitude']=='cautious':
            self.intentions['buy_products']=self.buy_products_but_think_about_it(self.desires['buy_products'])
            logging.info(f"{self.name} planned the intention to buy products.")  
   
    def execute_intention(self, intention,market_env):
        selected_products, companies, quantities = self.intentions[intention]
        logging.info(f"{self.name} will execute the intention: {self.intentions[intention]}")
        self.buy(selected_products, companies, quantities,market_env)
        # Remover la intención ejecutada
        self.intentions[intention]=[]

    def buy(self, selected_products, cheapest_companies, quantities,market_env:MarketEnvironment):
        for i in range(len(selected_products)):
            selected_product = selected_products[i]
            cheapest_company = cheapest_companies[i]
            quantity = quantities[i]
            available_stock = market_env.public_variables['companies'][cheapest_company].beliefs['product_prices'][cheapest_company][selected_product]['stock'] 
            if quantity>0:
                if available_stock >= quantity:
                    # Reduce stock
                    market_env.public_variables['companies'][cheapest_company].beliefs['product_prices'][cheapest_company][selected_product]['stock'] -= quantity
                    #Actualizar ganancia
                    if selected_product in market_env.public_variables['companies'][cheapest_company].beliefs['revenue']:
                        market_env.public_variables['companies'][cheapest_company].beliefs['revenue'][selected_product]+= quantity * market_env.public_variables['product_prices'][cheapest_company][selected_product]['price']
                    else:
                        market_env.public_variables['companies'][cheapest_company].beliefs['revenue'][selected_product]= quantity * market_env.public_variables['product_prices'][cheapest_company][selected_product]['price']

                    # Registrar la compra en el log
                    logging.info(f"{self.name} bought {quantity} units of {selected_product} from {cheapest_company}.")
                else:
                    # No hay suficiente stock
                    logging.warning(f"{self.name} attempted to buy {quantity} units of {selected_product}, but only {available_stock} units were available.")

    def buy_cheapest_products(self,selected_products):

        cheapest_companies = []
        quantities = []

        for selected_product in selected_products:
            cheapest_company = None
            cheapest_price = float('inf')

            for company, products in self.beliefs['product_prices'].items():
                if selected_product in products:
                    price = products[selected_product]['price']
                    if price < cheapest_price:
                        cheapest_price = price
                        cheapest_company = company

            quantity = int(self.beliefs['alpha'][selected_product] * self.beliefs['budget'] / cheapest_price)
            cheapest_companies.append(cheapest_company)
            quantities.append(quantity)

        logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {cheapest_companies}")
        return [selected_products, cheapest_companies, quantities]


    def buy_products_by_popularity(self,selected_products):
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
                    quantity = int(self.beliefs['alpha'][selected_product] * self.beliefs['budget'] / self.beliefs['product_prices'][popular_company][selected_product]['price'])
                    populars_companies.append(popular_company)
                    quantities.append(quantity)
            
            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {populars_companies}")
            return [selected_products, populars_companies, quantities]


    def buy_products_randomly(self,selected_products):
            companies = []
            quantities = []

            for selected_product in selected_products:

                comp=[x for x in self.beliefs['product_prices'] if selected_product in self.beliefs['product_prices'][x]]
                company=random.choice(comp)
                quantity = int(self.beliefs['alpha'][selected_product] * self.beliefs['budget'] / self.beliefs['product_prices'][company][selected_product]['price'])
                companies.append(company)
                quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {companies}")
            return [selected_products,companies, quantities]


    def buy_products_but_think_about_it(self,selected_products):

            companies = []
            quantities = []

            for selected_product in selected_products:

                comp=[x for x in self.beliefs['product_prices'] if selected_product in self.beliefs['product_prices'][x]]
                popularity_mean=np.mean([self.beliefs['company_popularity'][x] for x in comp])
                most_populars=[x for x in comp if self.beliefs['company_popularity'][x]>=popularity_mean]

                cheapest_comp=None
                cheapest_price=float('inf')

                for company in most_populars:
                    if self.beliefs['product_prices'][company][selected_product]['price']<cheapest_price:
                        cheapest_price=self.beliefs['product_prices'][company][selected_product]['price']
                        cheapest_comp=company

                quantity = int(self.beliefs['alpha'][selected_product] * self.beliefs['budget'] / cheapest_price)
                companies.append(cheapest_comp)
                quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {companies}")
            return [selected_products,companies, quantities]
