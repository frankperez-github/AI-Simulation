import logging
from BaseAgent import BDI_Agent
import json
from utils import calculate_percent, negotiate

des_int_json_file = open('./Desires-Intentions/Companies.json',)
int_exec_json_file = open('./Intentions-Execution/Companies.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def __init__(self, name, knowledge):
        super().__init__(name)
        self.beliefs['revenue']={}
        self.subproduct_stock = {}
        self.product_stock = {}
        self.product_budget = {}
        self.knowledge = knowledge
        self.s_offers = {}
        self.agreements = []

    def perceive_environment(self,market_env):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']

        for prod in self.beliefs['product_prices'][self.name].keys():
            self.product_stock[prod] = self.beliefs['product_prices'][self.name][prod]["stock"]

        self.beliefs['subproducts'] = market_env.public_variables['subproducts']

        self.beliefs['subproduct_suppliers']=market_env.public_variables['subproduct_suppliers']
        
        self.beliefs['company_popularity'] = market_env.public_variables['company_popularity']

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
            self.desires.remove(desire)

    def execute_intention(self, intention, market_env):
        execution = intentions_execution[intention]
        eval(execution["actions"])
        self.intentions.remove(intention)
        logging.info(eval(execution["log"]))

    def adjust_price(self, adjustment, market_env):
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

    def designate_budget(self):
        for product, revenue in self.beliefs['revenue'].items():
            self.product_budget[product] = revenue * 4/5

    def plan_investment(self):
        for product in self.beliefs['product_prices'][self.name]:
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
                self.s_offers[sub_product]['units']=units*self.beliefs['subproducts'][product][sub_product]
                self.s_offers[sub_product]['price']= self.subproduct_stock[sub_product]['price']
        
        self.agreements.append(negotiate(self))
        print(self.agreements)

    def evaluate_counteroffer(self, offer, counteroffer):
        """
        The company evaluates the supplier's counteroffer and decides whether to accept it or propose a new offer.
        This version uses fuzzy logic to evaluate the counteroffer.
        :param offer: The company's original offer
        :param counteroffer: The supplier's counteroffer
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        if counteroffer is None:
            logging.info(f"{self.name} did not receive a valid counteroffer from the supplier.")
            return False 

        logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        self.knowledge.simulation.input['price'] = (counteroffer['price'] - offer['price']) / offer['price'] * 100
        self.knowledge.simulation.input['quantity'] = (counteroffer['quantity'] / offer['quantity']) * 100

        self.knowledge.simulation.compute()

        acceptability = self.knowledge.simulation.output['acceptability']

        if acceptability > 75: 
            logging.info(f"{self.name} accepts the counteroffer.")
            return True

        new_price = (offer['price'] + counteroffer['price']) / 2
        new_quantity = (offer['quantity'] + counteroffer['quantity']) / 2
        new_offer = {
            'product': offer['product'],
            'quantity': new_quantity,
            'price': new_price
        }

        logging.info(f"{self.name} counters the supplier's offer with {new_quantity} units at {new_price} per unit.")
        return new_offer
