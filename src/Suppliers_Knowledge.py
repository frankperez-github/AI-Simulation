from src.Knowledge import Knowledge

class Suppliers_Knowledge(Knowledge):
    def __init__(self, suppliers_rules, suppliers_functions, suppliers_vars):
        super().__init__()
        self.load_vars(suppliers_vars)
        self.load_functions(suppliers_functions)
        self.load_rules(suppliers_rules)
      
    def evaluate_offer(self, price, quantity):
        """
        Evaluates the offer based on price and quantity using fuzzy logic.
        :param price: The price offered for the product
        :param quantity: The quantity requested in the offer
        :return: The computed acceptability of the offer
        """
        self.simulation.input['price'] = price
        self.simulation.input['quantity'] = quantity
        
        self.simulation.compute()
        
        return self.simulation.output['acceptability']