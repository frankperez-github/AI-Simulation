from Knowledge import Knowledge


class Company_Knowledge(Knowledge):
    def __init__(self, companies_rules, companies_functions, companies_vars):
        super().__init__()
        self.load_vars(companies_vars)
        self.load_functions(companies_functions)
        self.load_rules(companies_rules)
      
    def plan_investment(self, sales, popularity):
            self.simulation.input['sales'] = sales 
            self.simulation.input['popularity'] = popularity
            self.simulation.compute()
            return self.simulation.output['production']
