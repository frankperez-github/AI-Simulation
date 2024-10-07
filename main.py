import logging
import random
import os
import pandas as pd
from copy import deepcopy
from Environment import MarketEnvironment
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent
from utils import distribute_budgets, classify_quintiles, assign_alpha
from Company_Knowledge import Company_Knowledge
from Suppliers_Knowledge import Suppliers_Knowledge
from Simulation_methods import run_simulation

companies_rules = './Knowledge/Companies_Rules.json'
companies_functions = './Knowledge/Companies_Functions.json'
companies_vars = './Knowledge/Companies_Vars.json'

suppliers_rules = './Knowledge/Suppliers_Rules.json'
suppliers_functions = './Knowledge/Suppliers_Functions.json'
suppliers_vars = './Knowledge/Suppliers_Vars.json'

log_file_path = os.path.join(os.getcwd(), 'simulation_logs.log')

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=log_file_path,
    filemode='w',  
    level=logging.INFO,
    format='%(message)s',
)

n_households = 10

# Parámetros del modelo
initial_min_budget = 600
initial_mean_budget = 1500
count_products = 3
#base_price = {}
#change_in_price_pct = {}
mean_alpha_quintiles = {}
sd_alpha = {}
for i in range(count_products):
    #base_price[i] = 200
    #change_in_price_pct[i] = 20
    mean_alpha_quintiles[i] = [0.15, 0.13, 0.12, 0.1, 0.08]
    sd_alpha[i] = 0.02

    
products=["product_1","product_2","product_3"]


# Configuración de clientes (hogares)
Customers = []
for i in range(n_households):
    actitudes=['stingy','populist','cautious','random']
    actitud=random.choices(actitudes,[0.25,0.25,0.25,0.25])[0]
    Customers.append(CustomerAgent("Cliente" + str(i),actitud))

Customers = distribute_budgets(Customers, initial_min_budget, initial_mean_budget)
Customers = classify_quintiles(Customers)
Customers = assign_alpha(Customers, products, mean_alpha_quintiles, sd_alpha)
#Customers = calculate_demand_utility(Customers, base_price, count_products)

companies_knowledge = Company_Knowledge(companies_rules,companies_functions, companies_vars)
suppleirs_knowledge = Suppliers_Knowledge(suppliers_rules,suppliers_functions, suppliers_vars)

product_stock={
    'product_1':200,'product_2':200,'product_3':200
}
revenue={
    'product_1':6000,'product_2':6000,'product_3':6000
}
subproduct_stock={
    "product_1":{"stock":0,"price":30},
    "product_2":{"stock":0,"price":30},
    "product_3":{"stock":0,"price":30}
}


companies = {"A":CompanyAgent("A",companies_knowledge, deepcopy(revenue),deepcopy(subproduct_stock),deepcopy(product_stock)),
    "B":CompanyAgent("B", companies_knowledge,deepcopy(revenue),deepcopy(subproduct_stock),deepcopy(product_stock)),
    "C":CompanyAgent("C", companies_knowledge,deepcopy(revenue),deepcopy(subproduct_stock),deepcopy(product_stock))}

products_supplier={
               'product_1': {'quantity': 100, 'min_price': 5.0},
               'product_2': {'quantity': 200, 'min_price': 10.0},
               'product_3': {'quantity': 100, 'min_price': 5.0},
       }

suppliers = {
    "Suministrador1": SupplierAgent("Suministrador1",products_supplier, suppleirs_knowledge)
}
cust={}
for customer in Customers:
    cust[customer.name]=customer

#agents=companies+suppliers+cust

product_prices={
    "A":{
            "product_1":{"stock":100,"price":60},
            "product_2":{"stock":100,"price":60},
            "product_3":{"stock":100,"price":60}
        },
    "B":{
            "product_1":{"stock":100,"price":60},
            "product_2":{"stock":100,"price":60},
            "product_3":{"stock":100,"price":60}
        },
    "C":{
            "product_1":{"stock":100,"price":60},
            "product_2":{"stock":100,"price":60},
            "product_3":{"stock":100,"price":60}
        }
}

company_popularity={
        "A":{
                "product_1": 1,"product_2": 1,"product_3": 1
            },
        "B":{
                "product_1": 1,"product_2": 1,"product_3": 1
            },
        "C":{
                "product_1": 1,"product_2": 1,"product_3": 1
            }
    }


subproducts={"product_1":{"product_1":1},"product_2":{"product_2":1},"product_3":{"product_3":1}}
subproduct_suppliers={"Suministrador1":["product1","product2","product3"]}




market_env= MarketEnvironment(
    subproducts_suppliers=subproduct_suppliers,
    subproducts=subproducts,
    company_pop=company_popularity,
    companies=companies,
    suppliers=suppliers,
    clients=cust,
    product_prices=product_prices
)


run_simulation(market_env, short_version=False)