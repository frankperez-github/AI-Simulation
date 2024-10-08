import logging
import os
from copy import deepcopy
from Environment import MarketEnvironment
from Company import CompanyAgent
from Customer import CustomerAgent
from Supplier import SupplierAgent
from utils import distribute_budgets, classify_quintiles, assign_alpha
from Simulation_methods import run_simulation
from Company_Knowledge import Company_Knowledge
from Suppliers_Knowledge import Suppliers_Knowledge


def set_and_run_simulation(
    min_salary,
    mean_salary,
    mean_alpha_quintiles,
    sd_alpha,
    customer_attitudes,

    products,
    subproducts,

    companies_names,
    company_products_popularity,
    initial_products_stock,
    initial_product_revenue,
    subproduct_stock,
    products_prices,
    max_revenue_percent,

    suppliers_products,
    supplied_subproducts_by_supplier,

    marketing_config
):
    
    companies_rules = './Knowledge/Companies_Rules.json'
    companies_functions = './Knowledge/Companies_Functions.json'
    companies_vars = './Knowledge/Companies_Vars.json'

    suppliers_rules = './Knowledge/Suppliers_Rules.json'
    suppliers_functions = './Knowledge/Suppliers_Functions.json'
    suppliers_vars = './Knowledge/Suppliers_Vars.json'

    companies_knowledge = Company_Knowledge(companies_rules,companies_functions, companies_vars)
    suppliers_knowledge = Suppliers_Knowledge(suppliers_rules,suppliers_functions, suppliers_vars)

    log_file_path = os.path.join(os.getcwd(), 'simulation_logs.log')

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file_path,
        filemode='w',  
        level=logging.INFO,
        format='%(message)s',
    )
    
    customers = [CustomerAgent(f"Cliente{i}", attitude) for i, attitude in enumerate(customer_attitudes)]
    customers = distribute_budgets(customers, min_salary, mean_salary)
    customers = classify_quintiles(customers)
    customers = assign_alpha(customers, products, mean_alpha_quintiles, sd_alpha)

    companies = {
        companies_names[i]: CompanyAgent(
            companies_names[i],
            companies_knowledge,
            initial_product_revenue[i],
            subproduct_stock[i],
            initial_products_stock[i],
            max_revenue_percent[i]
        )
        for i in range(len(companies_names))
    }
    suppliers = {
        f"Suministrador{i+1}": SupplierAgent(f"Suministrador{i+1}", suppliers_products[i], suppliers_knowledge)
        for i in range(len(suppliers_products))
    }

    company_products_prices = {
        companies_names[i]: {
            product: {
                "stock": initial_products_stock[i][product],
                "price": products_prices[i][product]["price"]
            }
            for product in initial_products_stock[i]
        }
        for i in range(len(companies_names))
    }

    market_env= MarketEnvironment(
        subproducts_suppliers=supplied_subproducts_by_supplier,
        subproducts=subproducts,
        company_pop=company_products_popularity,
        companies=companies,
        suppliers=suppliers,
        clients={customer.name: customer for customer in customers},
        product_prices=company_products_prices,
        marketing_config=marketing_config
    )
    run_simulation(market_env)
