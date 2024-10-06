import logging
from BaseAgent import BDI_Agent
import json
from utils import calculate_percent, negotiate
import random
from Simulation_methods import run_short_simulation

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
        self.knowledge = knowledge
        self.s_offers = {}
        self.agreements = []
        self.total_budget = 0

    def perceive_environment(self,market_env, show_logs):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']

        for prod in self.beliefs['product_prices'][self.name].keys():
            self.product_stock[prod] = self.beliefs['product_prices'][self.name][prod]["stock"]

        self.beliefs['subproducts'] = market_env.public_variables['subproducts']

        self.beliefs['subproduct_suppliers'] = market_env.public_variables['subproduct_suppliers']
        self.beliefs['company_popularity'] = market_env.public_variables['company_popularity']
        for company in self.beliefs['company_popularity']:
            for product in self.beliefs['company_popularity'][company]:
                self.beliefs['company_popularity'][company][product]= random.normalvariate(self.beliefs['company_popularity'][company][product],7)
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

    def adjust_price(self, adjustment, market_env, show_logs):
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price['price'] * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product]['price'] = new_price
            if show_logs: logging.info(f"{self.name} adjusted the price of {product} from {price} to {new_price:.2f}.")

    def designate_budget(self, show_logs):
        if show_logs:
            # ALGORITMO GENETICO para definir product_budget
            for product, revenue in self.revenue.items():
                self.product_budget[product] = revenue * 4/5
            
        else:
            # Use defined product_budget
            for product, revenue in self.revenue.items():
                self.product_budget[product] = revenue * 4/5

    def produce(self, market_env, show_logs):
        """
        Produce products based on available subproducts in self.subproduct_stock and the allocated budget for each product.
        The goal is to produce until the product's allocated budget (from self.product_budget) is covered or the available 
        subproducts run out.
        
        :param market_env: Environment that contains product-subproduct dependencies
        """
        # Step 1: Reset product stock to 0 for all products
        self.product_stock = {product: 0 for product in market_env.public_variables["subproducts"].keys()}

        # Step 2: Reset the product quantities in market_env.public_variables['product_prices'] while keeping prices
        product_prices = market_env.public_variables['product_prices'].get(self.name, {})
        for product, details in product_prices.items():
            details['quantity'] = 0  # Reset quantity but keep the price

        # Step 3: Calculate the maximum budget for each product
        product_max_budget = {
            product: self.product_budget[product] * self.total_budget for product in self.product_budget
        }

        products_created = 0
        
        # Step 4: Sort products by revenue (highest to lowest)
        sorted_products = sorted(self.revenue.items(), key=lambda x: x[1], reverse=True)
        
        # Step 5: Produce products based on revenue priority and budget limit
        for product, revenue in sorted_products:
            if product not in self.product_budget:
                continue  # Skip if product does not have an allocated budget
            
            max_budget = product_max_budget[product]
            current_spent_budget = 0
            product_price = product_prices.get(product, {}).get('price', 0)

            # Check the subproduct requirements for the current product
            required_subproducts = market_env.public_variables["subproducts"].get(product, {})

            # Produce as many units as possible until budget or subproducts run out
            while current_spent_budget + product_price <= max_budget:
                can_produce = all(
                    self.subproduct_stock.get(subproduct, 0)["stock"] >= required_quantity
                    for subproduct, required_quantity in required_subproducts.items()
                )

                if can_produce:
                    # Deduct the required subproducts from stock
                    for subproduct, required_quantity in required_subproducts.items():
                        self.subproduct_stock[subproduct]["stock"] -= required_quantity

                    # Update product stock and product prices
                    self.product_stock[product] += 1
                    product_prices[product]['quantity'] += 1

                    # Update the budget spent on this product
                    current_spent_budget += product_price

                    # Track production
                    products_created += 1
                else:
                    # If can't produce more, break the loop for this product
                    break
        
        if show_logs: logging.info(f"Production complete. Total products created by company: {products_created}")


    def popularity_percent(self, product):
        popularity = {}
        for comp in self.beliefs['company_popularity']:
            if product in self.beliefs['company_popularity'][comp]:
                popularity[comp] = self.beliefs['company_popularity'][comp][product]
        
        maxi = max(popularity.values())
        mini = min(popularity.values())
        if maxi == mini: return popularity[self.name]
        else:
            popularity_ = ((((popularity[self.name] -mini)/(maxi-mini))*100) + popularity[self.name])/2
            return popularity_
        
    def plan_investment(self):
        for product in self.product_stock:
            sales = calculate_percent(self.product_stock[product], self.product_stock[product] - self.beliefs['product_prices'][self.name][product]['stock'])
            popularity = self.popularity_percent(product)
            investment = self.knowledge.plan_investment(sales, popularity)
            marketing = self.product_budget[product] * (100 - investment) / 100
            # FUNCION PARA AUMENTAR MARKETING
            self.product_budget[product] -= marketing

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
        :return: True if agreement is reached, otherwise a new counteroffer
        """
        product = offer['product']
        
        product_budget_info = self.s_offers.get(product)
        
        if not product_budget_info:
            if show_logs: logging.warning(f"No budget information available for {product}.")
            return False

        allocated_quantity = product_budget_info['units']
        allocated_price = product_budget_info['price']
        allocated_budget = allocated_quantity * allocated_price

        total_cost = counteroffer['price'] * counteroffer['quantity']
        
        if counteroffer is None:
            if show_logs: logging.info(f"{self.name} did not receive a valid counteroffer from the supplier.")
            return False

        if show_logs: logging.info(f"{self.name} received a counteroffer: {counteroffer['quantity']} units of {counteroffer['product']} at {counteroffer['price']} per unit.")

        if total_cost > allocated_budget:
            if show_logs: logging.warning(f"{self.name} does not have enough budget to accept the counteroffer for {product}.")
            return False
        
        price_percentage = (counteroffer['price'] - offer['price']) / offer['price'] * 100
        quantity_percentage = (counteroffer['quantity'] / offer['quantity']) * 100

        acceptability = self.knowledge.evaluate_offer(price_percentage, quantity_percentage)

        if acceptability > 75:
            if show_logs: logging.info(f"{self.name} accepts the counteroffer.")
            return True

        new_price = (offer['price'] + counteroffer['price']) / 2
        new_quantity = (offer['quantity'] + counteroffer['quantity']) / 2
        new_total_cost = new_price * new_quantity

        if new_total_cost > allocated_budget:
            if show_logs: logging.warning(f"{self.name} does not have enough budget to propose the counteroffer for {product}.")
            return False

        new_offer = {
            'product': offer['product'],
            'quantity': new_quantity,
            'price': new_price
        }

        if show_logs: logging.info(f"{self.name} counters the supplier's offer with {new_quantity} units at {new_price} per unit.")
        return new_offer


