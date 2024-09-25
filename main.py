import logging
import random
import os
import pandas as pd
from Environment import MarketEnvironment
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent
from utils import distribute_budgets, classify_quintiles, assign_alpha

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

def log_environment_data(market_env):
    #available_products_df = pd.DataFrame(list(market_env.public_variables['available_products'].items()), columns=['Product', 'Available Stock'])
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue=[]
    for company in list(market_env.public_variables['companies'].values()):
        for item in company.beliefs['revenue'].items():
            revenue.append(tuple([company.name])+item)
    revenue_df = pd.DataFrame(revenue, columns=['Company','Product', 'Revenue'])



    logging.info("\n----- Market Environment Data -----")
    #logging.info("\nAvailable Products (Stock):")
    #logging.info(available_products_df.to_string(index=False))
    logging.info("\nProduct Prices:")
    logging.info(product_prices_df.to_string(index=False))
    logging.info("\nCompany Revenue:")
    logging.info(revenue_df.to_string(index=False))
    logging.info("-----------------------------------\n")


def run_simulation(market_env:MarketEnvironment, steps=30):
    for step in range(steps):
        logging.info(f"\n========== Day {step + 1} ==========")

        for agent in list(market_env.public_variables['suppliers'].values()):
            agent.perceive_environment(market_env)
            agent.form_desires()
            agent.plan_intentions()
            agent.act(market_env)
        for agent in list(market_env.public_variables['companies'].values()):
            agent.perceive_environment(market_env)
            agent.form_desires()
            agent.plan_intentions()
            agent.act(market_env)
        for agent in list(market_env.public_variables['clients'].values()):
            agent.perceive_environment(market_env)
            agent.form_desires()
            agent.plan_intentions()
            agent.act(market_env)

        #market_env.update_environment()

        log_environment_data(market_env)


'''
def run_simulation(agents, market_env, steps=30):
    for step in range(steps):
        logging.info(f"\n========== Day {step + 1} ==========")
        for agent in agents:
            agent.perceive_environment(market_env)
            agent.form_desires()
            agent.plan_intentions()
            agent.act(market_env)
        #market_env.update_environment()

        log_environment_data(market_env)'''


products=["product1","product2","product3"]


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


companies = {"A":CompanyAgent("A"),
    "B":CompanyAgent("B"),
    "C":CompanyAgent("C")}

product_supplier={
               'product_1': {'quantity': 100, 'min_price': 5.0, 'start_price':7},
               'product_2': {'quantity': 200, 'min_price': 10.0, 'start_price':13},
               'product_3': {'quantity': 100, 'min_price': 5.0, 'start_price':7},
       }

suppliers = {
    "Suministrador1": SupplierAgent("Suministrador1",product_supplier)
}
cust={}
for customer in Customers:
    cust[customer.name]=customer

#agents=companies+suppliers+cust

product_prices={
    "A":{"product1":{"stock":100,"price":60},"product2":{"stock":100,"price":60},"product3":{"stock":100,"price":60}},
    "B":{"product1":{"stock":100,"price":60},"product2":{"stock":100,"price":60},"product3":{"stock":100,"price":60}},
    "C":{"product1":{"stock":100,"price":60},"product2":{"stock":100,"price":60},"product3":{"stock":100,"price":60}}
}

company_popularity={"A":1,"B":1,"C":1}
subproducts={"product1":{"product1":1},"product2":{"product2":1},"product3":{"product3":1}}
subproduct_suppliers={"Suministrador1":["product1","product2","product3"]}




market_env= MarketEnvironment(subproducts_suppliers=subproduct_suppliers,subproducts=subproducts,company_pop=company_popularity,companies=companies,suppliers=suppliers,clients=cust,product_prices=product_prices)


# Ejecutar la simulación
run_simulation(market_env)
