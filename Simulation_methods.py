import copy
import logging

import pandas as pd
from Environment import MarketEnvironment

def run_simulation(market_env:MarketEnvironment, steps=30, short_version=False):
    for step in range(steps):
        if not short_version: logging.info(f"\n========== Day {step + 1} ==========")
        for agent in list(market_env.public_variables['companies'].values()):
            agent.perceive_environment(market_env, show_logs=(not short_version))
            agent.form_desires(show_logs=(not short_version))
            agent.plan_intentions(show_logs=(not short_version))
            agent.act(market_env, show_logs=(not short_version))

        for agent in list(market_env.public_variables['clients'].values()):
            agent.perceive_environment(market_env, show_logs=(not short_version))
            agent.form_desires(show_logs=(not short_version))
            agent.plan_intentions(show_logs=(not short_version))
            agent.act(market_env, show_logs=(not short_version))
            
        if not short_version: log_environment_data(market_env)

def run_short_simulation(current_env, company_name, company_product_budget, steps=1):
    # Create a deep copy of current_env and update the product_budget for selected company
    market_copy = copy.deepcopy(current_env)
    market_copy.public_variables["companies"][company_name].product_budget = company_product_budget

    for step in range(steps):
        company = market_copy.public_variables['companies'][company_name]
        
        company.beliefs = {}
        company.desires = []
        company.intentions = []

        company.perceive_environment(market_copy, show_logs=False)
        company.form_desires(show_logs=False)
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

