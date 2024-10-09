import logging
import math
import numpy as np
import multiprocessing
from deap import creator
from functools import partial
from copy import deepcopy
from src.BaseAgent import BDI_Agent
import json
from src.utils import calculate_percent, negotiate, popularity_percent
import random
from src.Simulation_methods import run_short_simulation
from src.Genetic_Algorithm import Genetic_algorith

des_int_json_file = open('./src/Desires-Intentions/Companies.json',)
int_exec_json_file = open('./src/Intentions-Execution/Companies.json',)

desires_intentions = json.load(des_int_json_file)
intentions_execution = json.load(int_exec_json_file)


logging.basicConfig(filename='src/simulation_logs.log', level=logging.INFO, format='%(message)s')

class CompanyAgent(BDI_Agent):
    def __init__(self, name, knowledge, revenue, subproduct_stock, product_stock,max_revenue_percent,total_inversion):
        super().__init__(name)
        self.revenue = revenue
        self.total_revenue = 0
        self.subproduct_stock = subproduct_stock
        self.product_stock = product_stock
        self.product_budget = {}
        self.knowledge = knowledge
        self.s_offers = {}
        self.agreements = []
        self.total_budget = 0
        self.total_inversion=total_inversion
        self.max_revenue_percent=max_revenue_percent
        self.total_inversion=total_inversion
        self.sales={}
        self.popularity={}
        self.predicted_revenue = {}
        self.products={
            product: {
            "prices_list": [],
            "produced_quantity": 0,
            "sold_quantity": 0,
            "initial_popularity": -1,
            "final_popularity": 0
            } for product in product_stock.keys()
        }
        


    def perceive_environment(self,market_env, show_logs):
        self.beliefs['product_prices'] = deepcopy(market_env.public_variables['product_prices_old'])
        for product in self.beliefs['product_prices'].get(self.name, {}):
            #print(self.total_inversion)
            #print(self.beliefs['product_prices'][self.name])
            #print(self.product_stock[product])
            self.total_inversion[product]-= self.beliefs['product_prices'][self.name][product]['price']* (self.product_stock[product]-self.beliefs['product_prices'][self.name][product]['stock'])
            if self.total_inversion[product]<0: self.total_inversion[product]=0

        #for prod in self.beliefs['product_prices'][self.name].keys():
            #self.product_stock[prod] = self.beliefs['product_prices'][self.name][prod]["stock"]

        self.beliefs['subproducts'] = market_env.public_variables['subproducts']
        self.beliefs['subproduct_suppliers'] = market_env.public_variables['subproduct_suppliers']
        self.beliefs['company_popularity'] = market_env.public_variables['company_popularity']
        #for company in self.beliefs['company_popularity']:
        #    for product in self.beliefs['company_popularity'][company]:
        #        self.beliefs['company_popularity'][company][product]= random.normalvariate(self.beliefs['company_popularity'][company][product],7)
        #        if self.beliefs['company_popularity'][company][product] > 100: self.beliefs['company_popularity'][company][product] = 100
        #        if self.beliefs['company_popularity'][company][product] < 0: self.beliefs['company_popularity'][company][product] = 0
        if show_logs: logging.info(f"{self.name} perceived the environment and updated beliefs.")

    def form_desires(self, show_logs):
        self.desires.append('manage_profit')
        if show_logs: logging.info(f"{self.name} formed desire to manage_profit.")
        self.desires.append('manage_production')
        if show_logs: logging.info(f"{self.name} formed desire to manage_production.")
        self.desires.append('manage_sales')
        if show_logs: logging.info(f"{self.name} formed desire to manage_sales.")
    
    def plan_intentions(self, show_logs):
        for desire in self.desires:
            self.intentions += desires_intentions[desire]
            if show_logs: logging.info(f"{self.name} has planned to {desires_intentions[desire]}")
        self.desires=[]

    def execute_intention(self, intention, market_env, show_logs):
        execution = intentions_execution[intention]
        eval(execution["actions"])
        if show_logs: logging.info(eval(execution["log"]))

    def adjust_price(self,market_env, show_logs):
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            if self.product_stock[product]!=0:
                sales = self.sales[product]
                popularity = self.popularity[product]
                price_percent = self.knowledge.adjust_prices(sales, popularity)
                new_price_percent=self.max_revenue_percent[product]*price_percent/100
                competitive_factor=0
                competitive_count=0
               
                for company in self.beliefs['product_prices']:
                    if company != self.name:
                        if product in self.beliefs['product_prices'][company]:
                            competitive_factor+=self.beliefs['product_prices'][company][product]['price']
                            competitive_count+=1
                mean_competitive_factor=competitive_factor/competitive_count if competitive_count!=0 else self.beliefs['product_prices'][product]
                new_price = int(self.total_inversion[product]/self.product_stock[product] * (1+new_price_percent/100))
                percent_diference=((new_price-mean_competitive_factor)/mean_competitive_factor)*100
                new_balance=percent_diference/(-10)
                new_price= int(new_price * (1+ new_balance/100))
                
                if new_price < int(self.total_inversion[product]/self.product_stock[product]):                    
                    new_price= int(self.total_inversion[product]/self.product_stock[product] * (1.05))

                market_env.public_variables['product_prices'][self.name][product]['price'] = new_price
                
                self.update_product_prices_list(product, new_price)
                
                if show_logs: logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")

    def designate_budget(self, show_logs,market_env):
        
        if show_logs:
            # ALGORITMO GENETICO para definir product_budget
            budget_distribuitor=Genetic_algorith(fitness_function=partial(self.calcular_fitness,market_env=market_env),
                                                 individual_function=partial(self.crear_individuo),
                                                 mut_function=partial(self.mut_rebalance, market_env=market_env), cx_function=partial(self.cx_rebalance))
            product_budget_percent=budget_distribuitor.optimize(1,1,0.7,0)
            budget_distribuitor.close_pool()
            if 'info' in product_budget_percent:
                self.predicted_revenue = deepcopy(product_budget_percent['info'])
                product_budget_percent.pop('info')
            
            for p in self.revenue:
                self.revenue[p]*=4/5

            total=sum(list(self.revenue.values()))
            product_budget = {}
            for p in product_budget_percent:
                product_budget[p]=total*product_budget_percent[p]/100
            self.product_budget=product_budget
            
        #else:
        #    for p in self.revenue:
        #        self.product_budget[p]=self.revenue[p]*4/5



    def produce(self, market_env, show_logs):
        """
        Produce products based on available subproducts in self.subproduct_stock and the allocated budget for each product.
        The goal is to produce until the product's allocated budget (from self.product_budget) is covered or the available subproducts run out.
        
        :param market_env: Environment that contains product-subproduct dependencies
        """
        # Step 1: Reset product stock to 0 for all products
        self.product_stock = {product: self.beliefs['product_prices'][self.name][product]['stock'] for product in self.beliefs['product_prices'][self.name]}

        # Step 2: Reset the product quantities in market_env.public_variables['product_prices'] while keeping prices
        product_prices = market_env.public_variables['product_prices'].get(self.name, {})
        #for product, details in product_prices.items():
        #    details['stock'] = 0  # Reset quantity but keep the price

        # Step 3: Save the maximum budget for each product
        #product_max_budget = {
        #    product: self.product_budget[product] for product in self.product_budget
        #}

        products_created = 0
        
        # Step 4: Sort products by revenue (highest to lowest)
        sorted_products = sorted(self.predicted_revenue, key=lambda x: self.predicted_revenue[x], reverse=True) if show_logs else sorted(self.revenue, key=lambda x: self.revenue[x], reverse=True)
        # Step 5: Produce products based on revenue priority and budgeself.predictself.predicted_revenue.items()ed_revenue.items()t limit
        for product in sorted_products:
            if product not in self.product_budget:
                continue  # Skip if product does not have an allocated budget
            
            # Check the subproduct requirements for the current product
            required_subproducts = market_env.public_variables["subproducts"].get(product, {})

            # Produce as many units as possible until budget or subproducts run out
            while True:
                can_produce = all(
                    self.subproduct_stock.get(subproduct, 0)["stock"] >= required_quantity
                    for subproduct, required_quantity in required_subproducts.items()
                )

                if can_produce:

                    # Deduct the required subproducts from stock
                    for subproduct, required_quantity in required_subproducts.items():
                        self.total_inversion[product]+= required_quantity*self.subproduct_stock[subproduct]['price']
                        self.subproduct_stock[subproduct]["stock"] -= required_quantity

                    # Update product stock, product prices and products count
                    self.product_stock[product] += 1
                    product_prices[product]['stock'] += 1
                    self.products[product]["produced_quantity"] += 1
                    # Track production
                    products_created += 1

                    
                else:
                    break

        
        for p in self.revenue:
            self.revenue[p]=0
        if show_logs: logging.info(f"Production complete. Total products created by company: {products_created}")

    def adjust_popularity(self, product, quantity, show_logs):
        if self.beliefs['company_popularity'][self.name][product] - quantity >= 0 : 
            self.beliefs['company_popularity'][self.name][product] -= quantity  
        else: 
            self.beliefs['company_popularity'][self.name][product] = 0
        if show_logs: logging.info(f"{self.name}'s {product} lost {quantity} of popularity due to time. Now has {self.beliefs['company_popularity'][self.name][product]} of popularity")


    def plan_investment(self, market_env, show_logs):
        
        for product in self.product_stock:
            sales = calculate_percent(self.product_stock[product], self.product_stock[product] - self.beliefs['product_prices'][self.name][product]['stock'])
            #self.adjust_popularity(product, market_env.public_variables['marketing_config']['lose_popularity'], show_logs)
            popularity = popularity_percent(self,product)
            self.sales[product]=sales
            self.popularity[product]=popularity
            investment = self.knowledge.plan_investment(sales, popularity)
            marketing_money = self.product_budget[product] * (100 - investment) / 100
            self.total_inversion[product]+=marketing_money
            if show_logs: logging.info(f"{self.name} decided to invest {self.product_budget[product] * investment / 100} dollars in production and {marketing_money} in marketing of {product}")
            market_env.hidden_variables['marketing_stonks'].append((self.name, product, marketing_money, show_logs))
            self.product_budget[product] -= marketing_money
            

    def initial_proposals(self):
        for product in self.beliefs['product_prices'][self.name]:
            cost = 0
            for sub_product in self.beliefs['subproducts'][product]:
                cost += self.subproduct_stock[sub_product]['price'] * self.beliefs['subproducts'][product][sub_product]
            
            units = int(self.product_budget[product]/cost)

            for sub_product in self.beliefs['subproducts'][product]:
                if sub_product in self.s_offers:
                    self.s_offers[sub_product]['units']=units*self.beliefs['subproducts'][product][sub_product]
                    self.s_offers[sub_product]['price']= self.subproduct_stock[sub_product]['price']
                else:
                    self.s_offers[sub_product]={}
                    self.s_offers[sub_product]['units']=units*self.beliefs['subproducts'][product][sub_product]
                    self.s_offers[sub_product]['price']= self.subproduct_stock[sub_product]['price']

    def secure_subproduct_supply(self, market_env, show_logs):
        negotiate(self, market_env.public_variables["suppliers"], show_logs)

    def evaluate_counteroffer(self, offer, counteroffer, show_logs):
            """
            The company evaluates the supplier's counteroffer and decides whether to accept it or propose a new offer.
            This version checks the budget allocated for the specific product before evaluating or making a counteroffer.
            
            :param offer: The company's original offer
            :param counteroffer: The supplier's counteroffer
            :param show_logs: Boolean flag to control logging output
            :return: True if agreement is reached, otherwise a new counteroffer within budget constraints
            """
            product = offer['product']
            
            # Retrieve budget information for the product
            product_budget_info = self.s_offers.get(product)
            if not product_budget_info:
                if show_logs: logging.warning(f"No budget information available for {product}.")
                return False

            # Calculate allocated budget based on quantity and price
            allocated_quantity = product_budget_info['units']
            allocated_price = product_budget_info['price']
            allocated_budget = allocated_quantity * allocated_price

            # Calculate total cost of the counteroffer
            total_cost = counteroffer['price'] * counteroffer['quantity']
            
            if counteroffer is None:
                if show_logs: logging.info(f"{self.name} did not receive a valid counteroffer from the supplier.")
                return False

            if show_logs:
                logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

            # If total cost of counteroffer exceeds allocated budget, adjust counteroffer to fit within budget
            if total_cost > allocated_budget:
                affordable_quantity = allocated_budget // counteroffer['price']  # Maximum quantity within budget
                new_offer = {
                    'product': product,
                    'quantity': affordable_quantity,
                    'price': counteroffer['price']
                }
                if show_logs: logging.warning(f"{self.name} cannot afford {counteroffer['quantity']} units at {counteroffer['price']} per unit.")
                if show_logs: logging.info(f"{self.name} counters with {affordable_quantity} units at {counteroffer['price']} per unit (within budget).")
                return new_offer

            # Calculate acceptability of the counteroffer
            price_percentage = (counteroffer['price'] - offer['price']) / offer['price'] * 100
            quantity_percentage = (counteroffer['quantity'] / offer['quantity']) * 100
            acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

            # If counteroffer is acceptable, agree to it
            if acceptability > 75:
                if show_logs: logging.info(f"{self.name} accepts the counteroffer.")
                return True

            # Otherwise, propose a new counteroffer within budget constraints
            new_price = (offer['price'] + counteroffer['price']) / 2
            new_quantity = min((offer['quantity'] + counteroffer['quantity']) / 2, allocated_budget // new_price)
            new_offer = {
                'product': product,
                'quantity': new_quantity,
                'price': new_price
            }

            if show_logs: logging.info(f"{self.name} counters the supplier's offer with {new_quantity} units at {new_price} per unit.")
            return new_offer


    def calcular_fitness(self,individuo,market_env):
        if 'info' in individuo:
            individuo.pop('info')
        prediction= run_short_simulation(market_env,self.name,deepcopy(individuo),steps=1)
        individuo['info']=prediction
        return sum(list(prediction.values())),


    def crear_individuo(self):
        indiv={}
        for product in self.revenue:
            indiv[product]=random.uniform(0, 1)
        total = sum(list(indiv.values()))
        for p in indiv:
            indiv[p]= indiv[p]*100/total
        
        return creator.Individual(indiv)



    # Mutación personalizada: redistribuye el presupuesto entre dos productos
    def mut_rebalance(self,individual,market_env):
        ind_copy=deepcopy(individual)
        self.calcular_fitness(ind_copy,market_env)
        min_val=float('inf')
        min_p=None
        for p in ind_copy:
            if p !='info':
                if ind_copy[p]==0: ind_copy[p]=1
                if ind_copy['info'][p] /ind_copy[p]<min_val:
                    min_val=ind_copy['info'][p] /ind_copy[p]
                    min_p=[p]
                if ind_copy['info'][p] /ind_copy[p]==min_val:
                    min_val=ind_copy['info'][p] /ind_copy[p]
                    min_p.append(p)
        if len(min_p)>0:
            product=random.choice(min_p)
        individual[product]=0
        return (individual,)

        


    # Cruce personalizado: mezcla de porcentajes asegurando que la suma sea 100
    def cx_rebalance(self,ind1, ind2):

        ind1_copy=deepcopy(ind1)
        ind2_copy=deepcopy(ind2)
        for p in ind1:
            if p !='info':
                if ind1_copy[p]==0: ind1_copy[p]=1
                if ind2_copy[p]==0: ind2_copy[p]=1
                if ind1_copy['info'][p] /ind1_copy[p] <= ind2_copy['info'][p] /ind2_copy[p]:
                    ind1[p] = ind2[p]
                        
        total1 = sum([ind1[p] for p in ind1 if p!='info'])
        if total1 > 0:
            for p in ind1:
                if p != 'info': 
                    ind1[p] = ind1[p] * 100 / total1
        else:
            # Repartir uniformemente si la suma es cero
            for p in ind1:
                if p != 'info':
                    ind1[p] = 100/(len(ind1)-1)


        alpha = random.random()
        if alpha<0.5: alpha=1-alpha
        for p in ind1_copy:
            if p!='info':
                if ind1.fitness.values[0] > ind2.fitness.values[0]:
                    ind2[p] = alpha * ind1[p] + (1 - alpha) * ind2[p]
                else:
                    ind2[p] = alpha * ind2[p] + (1 - alpha) * ind1[p]
            
        total2 = sum([ind2[p] for p in ind2 if p!='info'])
        if total2 > 0:
            for p in ind2:
                if p != 'info': 
                    ind2[p] = ind2[p] * 100 / total2
        else:
            # Repartir uniformemente si la suma es cero
            for p in ind2:
                if p != 'info':
                    ind2[p] = 100/(len(ind2)-1)

        return ind1, ind2



    def update_product_prices_list(self, product_name, new_price):
        self.products[product_name]["prices_list"].append(new_price)