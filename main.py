import pandas as pd
from Environment import MarketEnvironment
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent
from utils import distribute_budgets,classify_quintiles, assign_alpha, calculate_demand_utility

# Número de hogares
n_households = 10

# Parámetros del modelo
initial_min_budget = 1830
initial_mean_budget = 4127
count_products=6
base_price={}
change_in_price_pct={}
mean_alpha_quintiles={}
sd_alpha={}
for i in range(count_products):
    base_price[i] = 200
    change_in_price_pct[i] = 20
    mean_alpha_quintiles[i] = [0.15, 0.13, 0.12, 0.1, 0.08]
    sd_alpha[i] = 0.02

def print_environment_data(market_env):
    available_products_df = pd.DataFrame(list(market_env.public_variables['available_products'].items()), columns=['Product', 'Available Stock'])
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue_df = pd.DataFrame(list(market_env.public_variables['revenue'].items()), columns=['Company', 'Revenue'])

    print("\n----- Market Environment Data -----")
    print("\nAvailable Products (Stock):")
    #print(available_products_df)
    print("\nProduct Prices:")
    #print(product_prices_df)
    print("\nCompany Revenue:")
    print(revenue_df)
    print("-----------------------------------\n")

def run_simulation(agents, market_env, steps=30):
    for step in range(steps):
        print(f"\n========== Day {step + 1} ==========")
        for agent in agents:
            agent.perceive_environment()
            agent.form_desires()
            agent.plan_intentions()
            agent.act()
        market_env.update_environment()

        print_environment_data(market_env)

file_path = './supermarket_sales.csv'
data = pd.read_csv(file_path)


market_env = MarketEnvironment(data)

Customers=[]
for i in range(n_households):
    Customers.append(CustomerAgent("Cliente"+str(i),market_env))

Customers=distribute_budgets(Customers,initial_min_budget,initial_mean_budget)
Customers=classify_quintiles(Customers)
Customers=assign_alpha(Customers,count_products,mean_alpha_quintiles,sd_alpha)
Customers=calculate_demand_utility(Customers,base_price,count_products)

agents = [
    CompanyAgent("A", market_env),
    CompanyAgent("B", market_env),
    CompanyAgent("C", market_env),
    SupplierAgent("Suministrador1", market_env)
]
agents+=Customers

run_simulation(agents, market_env)
