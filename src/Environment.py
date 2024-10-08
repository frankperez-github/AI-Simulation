import random
from copy import deepcopy

import pandas as pd

class MarketEnvironment:
    def __init__(self,product_prices,company_pop,subproducts,subproducts_suppliers,clients,suppliers,companies, marketing_config):
        self.public_variables = {
            'product_prices': product_prices,
            'product_prices_old':deepcopy(product_prices),
            'company_popularity': company_pop,
            'subproducts': subproducts,
            'subproduct_suppliers':subproducts_suppliers,
            'clients':clients,
            'suppliers':suppliers,
            'companies':companies,
            'marketing_config':marketing_config
        }

        self.hidden_variables = {
            'marketing_stonks' : []
        }
    def get_company_data(self, company_name):
        return self.public_variables["companies"][company_name]
