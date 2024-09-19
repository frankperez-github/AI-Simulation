import logging
import os
import pandas as pd
from Environment import market_env
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent
from utils import distribute_budgets, classify_quintiles, assign_alpha, calculate_demand_utility

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
initial_min_budget = 1830
initial_mean_budget = 4127
count_products = 6
base_price = {}
change_in_price_pct = {}
mean_alpha_quintiles = {}
sd_alpha = {}
for i in range(count_products):
    base_price[i] = 200
    change_in_price_pct[i] = 20
    mean_alpha_quintiles[i] = [0.15, 0.13, 0.12, 0.1, 0.08]
    sd_alpha[i] = 0.02

def log_environment_data(market_env):
    available_products_df = pd.DataFrame(list(market_env.public_variables['available_products'].items()), columns=['Product', 'Available Stock'])
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue_df = pd.DataFrame(list(market_env.public_variables['revenue'].items()), columns=['Company', 'Revenue'])

    logging.info("\n----- Market Environment Data -----")
    logging.info("\nAvailable Products (Stock):")
    logging.info(available_products_df.to_string(index=False))
    logging.info("\nProduct Prices:")
    logging.info(product_prices_df.to_string(index=False))
    logging.info("\nCompany Revenue:")
    logging.info(revenue_df.to_string(index=False))
    logging.info("-----------------------------------\n")

def run_simulation(agents, market_env, steps=30):
    for step in range(steps):
        logging.info(f"\n========== Day {step + 1} ==========")
        for agent in agents:
            agent.perceive_environment()
            agent.form_desires()
            agent.plan_intentions()
            agent.act()
        market_env.update_environment()

        log_environment_data(market_env)

# Configuración de clientes (hogares)
Customers = []
for i in range(n_households):
    Customers.append(CustomerAgent("Cliente" + str(i)))

Customers = distribute_budgets(Customers, initial_min_budget, initial_mean_budget)
Customers = classify_quintiles(Customers)
Customers = assign_alpha(Customers, count_products, mean_alpha_quintiles, sd_alpha)
Customers = calculate_demand_utility(Customers, base_price, count_products)

agents = [
    CompanyAgent("A"),
    CompanyAgent("B"),
    CompanyAgent("C"),
    SupplierAgent("Suministrador1")
]
agents += Customers

# Ejecutar la simulación
run_simulation(agents, market_env)
