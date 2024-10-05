import logging
from BaseAgent import BDI_Agent
import json
from utils import calculate_percent, negotiate
import random

des_int_json_file = open('./Desires-Intentions/Companies.json',)
int_exec_json_file = open('./Intentions-Execution/Companies.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def __init__(self, name, knowledge, revenue, subproduct_stock, product_stock):
        super().__init__(name)
        self.revenue = revenue
        self.subproduct_stock = subproduct_stock
        self.product_stock = product_stock
        self.product_budget = {}
        self.total_budget = 0
        self.knowledge = knowledge
        self.s_offers = {}
        self.agreements = []

    def perceive_environment(self,market_env):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']

        for prod in self.beliefs['product_prices'][self.name].keys():
            self.product_stock[prod] = self.beliefs['product_prices'][self.name][prod]["stock"]

        self.beliefs['subproducts'] = market_env.public_variables['subproducts']

        self.beliefs['subproduct_suppliers'] = market_env.public_variables['subproduct_suppliers']
        self.beliefs['company_popularity'] = market_env.public_variables['company_popularity']
        for company in self.beliefs['company_popularity']:
            for product in self.beliefs['company_popularity'][company]:
                self.beliefs['company_popularity'][company][product]= random.normalvariate(self.beliefs['company_popularity'][company][product],7)
        logging.info(f"{self.name} perceived the environment and updated beliefs.")

    def form_desires(self):
        self.desires.append('manage_profit')
        logging.info(f"{self.name} formed desire to manage_profit.")
        self.desires.append('manage_production')
        logging.info(f"{self.name} formed desire to manage_production.")
        self.desires.append('manage_sales')
        logging.info(f"{self.name} formed desire to manage_sales.")
    
    def plan_intentions(self):
        for desire in self.desires:
            self.intentions += desires_intentions[desire]
            logging.info(f"{self.name} has planned to {desires_intentions[desire]}")
        self.desires=[]

    def execute_intention(self, intention, market_env):
        execution = intentions_execution[intention]
        eval(execution["actions"])
        logging.info(eval(execution["log"]))

    def adjust_price(self, adjustment, market_env):
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price['price'] * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product]['price'] = new_price
            logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")

    def designate_budget(self):
        for product, revenue in self.revenue.items():
            self.product_budget[product] = revenue *4/5

    def produce(market_env):
        print("Producing...")

    def plan_investment(self):
        for product in self.product_stock:
            sales = calculate_percent(self.product_stock[product], self.product_stock[product] - self.beliefs['product_prices'][self.name][product]['stock'])
            popularity = self.beliefs['company_popularity'][self.name][product]
            investment = self.knowledge.plan_investment(sales, popularity)
            marketing = self.product_budget[product] * (100 - investment) / 100
            #FUNCION PARA AUMENTAR MARKETING
            self.product_budget[product] -= marketing

    def initial_proposals(self):
        for product in self.beliefs['product_prices'][self.name]:
            cost = 0
            for sub_product in self.beliefs['subproducts'][product]:
                cost += self.subproduct_stock[sub_product]['price'] * self.beliefs['subproducts'][product][sub_product]
            
            units= int(self.product_budget[product]/cost)

            for sub_product in self.beliefs['subproducts'][product]:
                if sub_product in self.s_offers:
                    self.s_offers[sub_product]['units']=units*self.beliefs['subproducts'][product][sub_product]
                    self.s_offers[sub_product]['price']= self.subproduct_stock[sub_product]['price']
                else:
                    self.s_offers[sub_product]={}
                    self.s_offers[sub_product]['units']=units*self.beliefs['subproducts'][product][sub_product]
                    self.s_offers[sub_product]['price']= self.subproduct_stock[sub_product]['price']

    def secure_subproduct_supply(self, market_env):
        negotiate(self, market_env.public_variables["suppliers"])

    def evaluate_counteroffer(self, offer, counteroffer):
        """
        The company evaluates the supplier's counteroffer and decides whether to accept it or propose a new offer.
        This version checks the budget allocated for the specific product before evaluating or making a counteroffer.
        
        :param offer: The company's original offer
        :param counteroffer: The supplier's counteroffer
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        product = offer['product']
        
        product_budget_info = self.s_offers.get(product)
        
        if not product_budget_info:
            logging.warning(f"No budget information available for {product}.")
            return False

        allocated_quantity = product_budget_info['units']
        allocated_price = product_budget_info['price']
        allocated_budget = allocated_quantity * allocated_price

        total_cost = counteroffer['price'] * counteroffer['quantity']
        
        if counteroffer is None:
            logging.info(f"{self.name} did not receive a valid counteroffer from the supplier.")
            return False

        logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        if total_cost > allocated_budget:
            logging.warning(f"{self.name} does not have enough budget to accept the counteroffer for {product}.")
            return False
        
        price_percentage = (counteroffer['price'] - offer['price']) / offer['price'] * 100
        quantity_percentage = (counteroffer['quantity'] / offer['quantity']) * 100

        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        if acceptability > 75:
            logging.info(f"{self.name} accepts the counteroffer.")
            return True

        new_price = (offer['price'] + counteroffer['price']) / 2
        new_quantity = (offer['quantity'] + counteroffer['quantity']) / 2
        new_total_cost = new_price * new_quantity

        if new_total_cost > allocated_budget:
            logging.warning(f"{self.name} does not have enough budget to propose the counteroffer for {product}.")
            return False

        new_offer = {
            'product': offer['product'],
            'quantity': new_quantity,
            'price': new_price
        }

        logging.info(f"{self.name} counters the supplier's offer with {new_quantity} units at {new_price} per unit.")
        return new_offer


