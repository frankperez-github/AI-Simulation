import random

import pandas as pd

class MarketEnvironment:
    def __init__(self,product_prices,company_pop,subproducts,subproducts_suppliers,clients,suppliers,companies):
        self.public_variables = {
            'product_prices': product_prices,
            'company_popularity': company_pop,
            'subproducts': subproducts,
            'subproduct_suppliers':subproducts_suppliers,
            'clients':clients,
            'suppliers':suppliers,
            'companies':companies
        }

        self.hidden_variables = {
        }


