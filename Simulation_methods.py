import copy
import math
import logging
from copy import deepcopy
import pandas as pd
from Environment import MarketEnvironment

def run_simulation(market_env:MarketEnvironment, steps=12):
    for step in range(steps):
        logging.info(f"\n========== Day {step + 1} ==========")
        for agent in list(market_env.public_variables['companies'].values()):
            agent.perceive_environment(market_env, show_logs=True)
            agent.form_desires(show_logs=True)
            agent.plan_intentions(show_logs=True)
            agent.act(market_env, show_logs=True)


        for agent in list(market_env.public_variables['clients'].values()):
            agent.perceive_environment(market_env, show_logs=True)
            agent.form_desires(show_logs=True)
            agent.plan_intentions(show_logs=True)
            agent.act(market_env, show_logs=True)
            
        
        market_env.public_variables['product_prices_old']=deepcopy(market_env.public_variables['product_prices'])
        log_environment_data(market_env)

def run_short_simulation(current_env, company_name, company_product_budget, steps=1):
    # Create a deep copy of current_env and update the product_budget for selected company
    market_copy = copy.deepcopy(current_env)
    
    for p in market_copy.public_variables["companies"][company_name].revenue:
        market_copy.public_variables["companies"][company_name].revenue[p]*=4/5


    total_money = sum(list(market_copy.public_variables["companies"][company_name].revenue.values()))
    product_money={}
    for product in company_product_budget:
        product_money[product]= total_money*company_product_budget[product]/100
    
    market_copy.public_variables["companies"][company_name].product_budget = total_money

    company = market_copy.public_variables['companies'][company_name]
    company.beliefs = {}
    company.desires = []
    company.intentions = []

    for step in range(steps):
        company.perceive_environment(market_copy, show_logs=False)

        for agent in list(market_copy.public_variables['companies'].values()):
            agent.perceive_environment(market_copy, show_logs=False)
            if agent.name != company.name:
                for prod in agent.product_stock:
                    agent.product_stock[prod] = math.inf
        
        company.plan_intentions(show_logs=False)
        company.act(market_copy, show_logs=False)

        for agent in list(market_copy.public_variables['clients'].values()):
            agent.perceive_environment(market_copy, show_logs=False)
            agent.form_desires(show_logs=False)
            agent.plan_intentions(show_logs=False)
            agent.act(market_copy, show_logs=False)
            
    return market_copy.public_variables["companies"][company_name].revenue


def log_environment_data(market_env):
    #available_products_df = pd.DataFrame(list(market_env.public_variables['available_products'].items()), columns=['Product', 'Available Stock'])
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue=[]
    for company in list(market_env.public_variables['companies'].values()):
        for item in company.revenue.items():
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

