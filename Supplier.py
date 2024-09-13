import random
from BaseAgent import BDI_Agent
from Environment import market_env



class SupplierAgent(BDI_Agent):
    def perceive_environment(self):
        # Update beliefs about market demand and available products
        self.beliefs['market_demand'] = market_env.public_variables['market_demand']
        self.beliefs['available_products'] = market_env.public_variables['available_products']

    def form_desires(self):
        # The supplier wants to supply products
        self.desires['supply_products'] = random.choice([True, False])

    def plan_intentions(self):
        if self.desires.get('supply_products'):
            # Plan to supply products to companies
            self.intentions.append('supply_to_companies')

    def execute_intention(self, intention):
        if intention == 'supply_to_companies':
            self.supply_products()
        self.intentions.remove(intention)

    def supply_products(self):
        for product, demand in self.beliefs['market_demand'].items():
            if demand > 0:
                supply_quantity = demand  # Supply demand
                market_env.public_variables['market_demand'][product] = 0
                self.update_stock(product, supply_quantity)
            else:
                if random.random() < 0.3:  # 30% of chance of supply the product
                    supply_quantity = random.randint(1, 20)  # Supply between 1 and 20 items of the product
                    self.update_stock(product, supply_quantity)

            # Update market trend (increase trend for the product if supplied)
            if product in market_env.public_variables['market_trends']:
                market_env.public_variables['market_trends'][product] += 1
            else:
                market_env.public_variables['market_trends'][product] = 1


    def update_stock(self, product, quantity):
        # Update the inventory in the environment
        if product in market_env.public_variables['available_products']:
            market_env.public_variables['available_products'][product] += quantity
        else:
            market_env.public_variables['available_products'][product] = quantity