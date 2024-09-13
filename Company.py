from BaseAgent import BDI_Agent
from Environment import market_env


class CompanyAgent(BDI_Agent):
    def perceive_environment(self):
        self.beliefs['product_prices'] = market_env.public_variables['product_prices']
        self.beliefs['competition_levels'] = market_env.public_variables['competition_levels']
        self.beliefs['market_demand'] = market_env.public_variables['market_demand']

    def form_desires(self):
        for product, _ in self.beliefs['product_prices'].get(self.name, {}).items():
            competition_level = self.beliefs['competition_levels'].get(product, 0)

            if competition_level > 5:
                self.desires['maximize_profit'] = True
            else:
                self.desires['expand_market_share'] = True

    def plan_intentions(self):
        if self.desires.get('maximize_profit'):
            self.intentions.append('increase_prices')
        if self.desires.get('expand_market_share'):
            self.intentions.append('lower_prices')

    def execute_intention(self, intention):
        if intention == 'increase_prices':
            self.adjust_price(0.1)
        elif intention == 'lower_prices':
            self.adjust_price(-0.1)
        self.intentions.remove(intention)

    def adjust_price(self, adjustment):
        for product, price in market_env.public_variables['product_prices'].get(self.name, {}).items():
            new_price = price * (1 + adjustment)
            market_env.public_variables['product_prices'][self.name][product] = new_price
