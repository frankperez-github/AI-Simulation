import copy
import math
import logging
from copy import deepcopy
import random
import pandas as pd
from src.Environment import MarketEnvironment
from src.utils import marketing


def run_simulation(market_env:MarketEnvironment, steps=3):
    for step in range(steps):
        logging.info(f"\n========== Month {step + 1} ==========")
        
        companies_list = list(market_env.public_variables['companies'].values())
        random.shuffle(companies_list)
        for agent in companies_list:
            agent.perceive_environment(market_env, show_logs=True)
            agent.form_desires(show_logs=True)
            agent.plan_intentions(show_logs=True)
            agent.act(market_env, show_logs=True)

        for company, product, money, show_logs in market_env.hidden_variables['marketing_stonks']:
            marketing(company, product, money, show_logs, market_env)

        market_env.hidden_variables['marketing_stonks'] = []

        clients_list = list(market_env.public_variables['clients'].values())
        random.shuffle(clients_list)
        for agent in clients_list:
            agent.perceive_environment(market_env, show_logs=True)
            agent.form_desires(show_logs=True)
            agent.plan_intentions(show_logs=True)
            agent.act(market_env, show_logs=True)

        update_companies_revenue(market_env.public_variables["companies"])
        
        for company in market_env.public_variables['company_popularity']:
            for product in market_env.public_variables['company_popularity'][company]:
                quantity = market_env.public_variables['marketing_config']['lose_popularity']
                if market_env.public_variables['company_popularity'][company][product] - quantity >= 0 : 
                    market_env.public_variables['company_popularity'][company][product] = int(market_env.public_variables['company_popularity'][company][product] - quantity)
                else: 
                    market_env.public_variables['company_popularity'][company][product] = 0
                if market_env.public_variables["companies"][company].products[product]["initial_popularity"] == -1:
                    market_env.public_variables["companies"][company].products[product]["initial_popularity"] = market_env.public_variables['company_popularity'][company][product]
                market_env.public_variables["companies"][company].products[product]["final_popularity"] = market_env.public_variables['company_popularity'][company][product]
                if show_logs: logging.info(f"{company}'s {product} lost {quantity} of popularity due to time. Now has {market_env.public_variables['company_popularity'][company][product]} of popularity")

        
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
    product_prices_df = pd.DataFrame([(company, product, price) for company, products in market_env.public_variables['product_prices'].items() for product, price in products.items()], columns=['Company', 'Product', 'Price'])
    revenue=[]
    for company_name in list(market_env.public_variables['companies'].keys()):
        revenue.append((company_name, market_env.public_variables['companies'][company_name].total_revenue))
    revenue_df = pd.DataFrame((revenue), columns=['Company', 'Revenue'])
    logging.info("\n----- Market Environment Data -----")
    logging.info("\nProduct Prices:")
    logging.info(product_prices_df.to_string(index=False))
    logging.info("\nCompanies Revenue:")
    logging.info(revenue_df.to_string(index=False))
    logging.info("-----------------------------------\n")

def update_companies_revenue(companies):
    for company_name in companies.keys():
        company = companies[company_name]
        for product_name in company.revenue.keys():
            product_revenue = company.revenue[product_name]
            company.total_revenue += product_revenue