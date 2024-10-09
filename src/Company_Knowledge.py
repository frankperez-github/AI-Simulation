from src.Knowledge import Knowledge


class Company_Knowledge(Knowledge):
    def __init__(self, companies_rules, companies_functions, companies_vars):
        super().__init__()
        self.load_vars(companies_vars)
        self.load_functions(companies_functions)
        self.load_rules(companies_rules)
      
    def plan_investment(self, sales, popularity):
            self.simulation.input['sales'] = sales 
            self.simulation.input['popularity'] = popularity
            self.simulation.input['price'] = 0
            self.simulation.input['quantity'] = 0
            
            self.simulation.compute()
            return self.simulation.output['production']
    
    def evaluate_offer(self, price, quantity):
        self.simulation.input['price'] = price
        self.simulation.input['quantity'] = quantity
        self.simulation.input['sales'] = 0
        self.simulation.input['popularity'] = 0

        self.simulation.compute()

        return self.simulation.output['acceptability']
    
    def adjust_prices(self, sales, popularity):
        self.simulation.input['sales'] = sales 
        self.simulation.input['popularity'] = popularity
        self.simulation.input['price'] = 0
        self.simulation.input['quantity'] = 0
        
        self.simulation.compute()
        return self.simulation.output['adj_price']
