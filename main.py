import pandas as pd
from Environment import MarketEnvironment
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent

def print_environment_data(market_env):
    available_products_df = pd.DataFrame(list(market_env.public_variables['available_products'].items()), columns=['Product', 'Available Stock'])
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue_df = pd.DataFrame(list(market_env.public_variables['revenue'].items()), columns=['Company', 'Revenue'])

    print("\n----- Market Environment Data -----")
    print("\nAvailable Products (Stock):")
    print(available_products_df)
    print("\nProduct Prices:")
    print(product_prices_df)
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

agents = [
    CompanyAgent("A", market_env),
    CompanyAgent("B", market_env),
    CompanyAgent("C", market_env),
    CustomerAgent("Cliente1", market_env),
    CustomerAgent("Cliente2", market_env),
    CustomerAgent("Cliente3", market_env),
    CustomerAgent("Cliente4", market_env),
    CustomerAgent("Cliente5", market_env),
    CustomerAgent("Cliente6", market_env),
    CustomerAgent("Cliente7", market_env),
    CustomerAgent("Cliente8", market_env),
    CustomerAgent("Cliente9", market_env),
    CustomerAgent("Cliente10", market_env),
    SupplierAgent("Suministrador1", market_env)
]

run_simulation(agents, market_env)
