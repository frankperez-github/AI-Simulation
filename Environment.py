import random

import pandas as pd

class MarketEnvironment:
    def __init__(self, data):
        self.public_variables = {
            'product_prices': {},
            'product_gross_income': {},
            'available_products': {},
            'selling_companies': {},
            'market_demand': {},
            'competition_levels': {},
            'market_trends': {},
            'revenue': {},
            'company_popularity': {'A':1,'B':1,'C':1},
            'dollar_behavior': 0,
            'product_dict':{},
            'subproducts': {}
        }

        self.hidden_variables = {
            'company_strategies': {},
            'supplier_conditions': {},
        }

        self.load_data(data)
        self.initialize_market_variables()

    def load_data(self, data):

        unique_products = data['Product line'].unique()

        product_dict = {product: idx for idx, product in enumerate(unique_products)}
        self.public_variables['product_dict'] = product_dict

        product_competition = {}

        for _, row in data.iterrows():
            product = row['Product line']
            income = row['gross income']
            branch = row['Branch']
            price = row['Unit price']
            quantity = row['Quantity']

            if branch not in self.public_variables['product_prices']:
                self.public_variables['product_prices'][branch] = {}
                self.public_variables['product_gross_income'][branch] = {}

            self.public_variables['product_prices'][branch][product] = price
            self.public_variables['product_gross_income'][branch][product] = income

            if product not in self.public_variables['available_products']:
                self.public_variables['available_products'][product] = 0
            self.public_variables['available_products'][product] += quantity

            if product not in product_competition:
                product_competition[product] = set()
            product_competition[product].add(branch)

        for product in unique_products:
            subproducts = {f"subproduct_{i}": random.randint(1, 5) for i in range(random.randint(1, 4))}
            self.public_variables['subproducts'][product] = subproducts

        for product, branches in product_competition.items():
            self.public_variables['competition_levels'][product] = len(branches)

    def initialize_market_variables(self):
        product_lines = self.public_variables['available_products'].keys()
        for product in product_lines:
            self.public_variables['market_demand'][product] = 0
            self.public_variables['market_trends'][product] = 0

    def update_environment(self):
        self.public_variables['dollar_behavior'] = random.choice([-1, 0, 1])
        self.adjust_prices_based_on_dollar()

        for company in self.public_variables['company_popularity']:
            change = random.uniform(-0.5, 0.5)
            new_popularity = self.public_variables['company_popularity'][company] + change
            self.public_variables['company_popularity'][company] = min(max(new_popularity, 1), 10)

    def adjust_prices_based_on_dollar(self):
        for company, products in self.public_variables['product_prices'].items():
            for product, price in products.items():
                if self.public_variables['dollar_behavior'] == 1:  
                    self.public_variables['product_prices'][company][product] = price * 1.05
                elif self.public_variables['dollar_behavior'] == -1: 
                    self.public_variables['product_prices'][company][product] = price * 0.95



file_path = './supermarket_sales.csv'
data = pd.read_csv(file_path)


market_env = MarketEnvironment(data)