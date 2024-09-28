import random
import logging
from BaseAgent import BDI_Agent
import numpy as np
from Environment import MarketEnvironment
import json

des_int_json_file = open('./Desires-Intentions/Customers.json',)
int_exec_json_file = open('./Intentions-Execution/Customers.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CustomerAgent(BDI_Agent):
    def __init__(self, name, actitud):
        super().__init__(name)
        self.attitude = actitud
        self.alpha = {}
        self.budget = 0
        self.quintil = -1


    def perceive_environment(self,market_env:MarketEnvironment):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['company_popularity']=market_env.public_variables['company_popularity']
        logging.info(f"{self.name} has perceived the environment and updated beliefs about available products and prices.")

    def form_desires(self):
        self.desires.append('buy_products')
        logging.info(f"{self.name} formed the desire to buy products")

    def plan_intentions(self):
        for desire in self.desires:
            intention = desires_intentions[f"{desire}_{self.attitude}"]
            self.intentions.append(intention)
            logging.info(f"{self.name} planned the intention to {intention}")

    def execute_intention(self, intention, market_env):
        logging.info(f"{self.name} will execute the intention: {intention}")
        products = [product for product in self.alpha if self.alpha[product]>0]
        execution = intentions_execution[intention]
        for action in execution["actions"]:
            exec(action)
        self.intentions.remove(intention)
        logging.info(execution["log"])

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

            quantity = int(self.alpha[selected_product] * self.budget / cheapest_price)
            cheapest_companies.append(cheapest_company)
            quantities.append(quantity)

        logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {cheapest_companies}")
        return [selected_products, cheapest_companies, quantities]


    def buy_products_by_popularity(self,selected_products):
            populars_companies = []
            quantities = []

            for selected_product in selected_products:
                popular_company = None
                pop = float('inf')*-1
                for company in self.beliefs['company_popularity']:
                    if selected_product in self.beliefs['company_popularity'][company]:
                        popularity= self.beliefs['company_popularity'][company][selected_product]
                        if popularity>pop:
                            pop=popularity
                            popular_company=company
                quantity = int(self.alpha[selected_product] * self.budget / self.beliefs['product_prices'][popular_company][selected_product]['price'])
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
                quantity = int(self.alpha[selected_product] * self.budget / self.beliefs['product_prices'][company][selected_product]['price'])
                companies.append(company)
                quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {companies}")
            return [selected_products,companies, quantities]


    def buy_products_but_think_about_it(self,selected_products):

            companies = []
            quantities = []

            for selected_product in selected_products:

                comp=[x for x in self.beliefs['product_prices'] if selected_product in self.beliefs['product_prices'][x]]
                most_populars=sorted(comp,key=lambda x: self.beliefs['company_popularity'][x][selected_product] ,reverse=True)[:3]

                cheapest_comp=None
                cheapest_price=float('inf')

                for company in most_populars:
                    if self.beliefs['product_prices'][company][selected_product]['price']<cheapest_price:
                        cheapest_price=self.beliefs['product_prices'][company][selected_product]['price']
                        cheapest_comp=company

                quantity = int(self.alpha[selected_product] * self.budget / cheapest_price)
                companies.append(cheapest_comp)
                quantities.append(quantity)

            logging.info(f"{self.name} selected products: {selected_products} with quantities: {quantities} from companies: {companies}")
            return [selected_products,companies, quantities]
