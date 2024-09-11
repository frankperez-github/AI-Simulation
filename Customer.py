import random
from BaseAgent import BDI_Agent

class CustomerAgent(BDI_Agent):
    def __init__(self, name, market_env):
        super().__init__(name, market_env)
        self.beliefs['budget'] = 0
        self.beliefs['quintil']=-1
        self.beliefs['alpha']={}
        self.beliefs['demand']={}
        self.beliefs['expenditure']={}
        self.beliefs['utility']={}


    def perceive_environment(self):
        self.beliefs['available_products'] = self.market_env.public_variables['available_products']
        self.beliefs['product_prices'] = self.market_env.public_variables['product_prices']

    def form_desires(self):
        self.desires['buy_products'] = random.choice([True, False])

    def plan_intentions(self):
        if self.desires.get('buy_products'):
            self.intentions.append('buy_cheap_products')

    def execute_intention(self, intention):
        if intention == 'buy_cheap_products':
            selected_products, cheapest_companies, quantities = self.buy_random_cheapest_products()
            if selected_products:
                self.buy(selected_products, cheapest_companies, quantities)
        # New intentions here
        self.intentions.remove(intention)
    
    def buy(self, selected_products, cheapest_companies, quantities):
        for i in range(len(selected_products)):
            selected_product = selected_products[i]
            cheapest_company = cheapest_companies[i]
            quantity = quantities[i]

            available_stock = self.market_env.public_variables['available_products'].get(selected_product, 0)
            if available_stock >= quantity:
                # Reduce stock
                self.market_env.public_variables['available_products'][selected_product] -= quantity

                # Get the revenue (gross income) per unit for the selected product from the cheapest company
                revenue_per_unit = self.market_env.public_variables['product_gross_income'][cheapest_company][selected_product]

                # Update revenue for the company
                if cheapest_company in self.market_env.public_variables['revenue']:
                    self.market_env.public_variables['revenue'][cheapest_company] += revenue_per_unit * quantity
                else:
                    self.market_env.public_variables['revenue'][cheapest_company] = revenue_per_unit * quantity

                # Increase market demand
                if selected_product in self.market_env.public_variables['market_demand']:
                    self.market_env.public_variables['market_demand'][selected_product] += quantity
                else:
                    self.market_env.public_variables['market_demand'][selected_product] = quantity

                # Update market trend (increase trend for the product)
                if selected_product in self.market_env.public_variables['market_trends']:
                    self.market_env.public_variables['market_trends'][selected_product] += 1
                else:
                    self.market_env.public_variables['market_trends'][selected_product] = 1

                # Print confirmation (optional)
                # print(f"Customer {self.name} bought {quantity} units of {selected_product} from {cheapest_company}, gross income per unit: {revenue_per_unit}")
            else:
                # Not enough stock
                # print(f"Not enough stock for {selected_product}.")
                pass



    def buy_random_cheapest_products(self):
        available_products = set()
        for branch in self.beliefs['product_prices']:
            available_products = available_products.union(set(self.beliefs['product_prices'][branch]))

        if not available_products:
            # No products available
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

            quantity = random.randint(1, 10)

            cheapest_companies.append(cheapest_company)
            quantities.append(quantity)

        return selected_products, cheapest_companies, quantities
