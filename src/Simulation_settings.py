import logging
import os
import random
from copy import deepcopy
from src.Environment import MarketEnvironment
from src.Company import CompanyAgent
from src.Customer import CustomerAgent
from src.Supplier import SupplierAgent
from src.utils import distribute_budgets, classify_quintiles, assign_alpha
from src.Simulation_methods import run_simulation
from src.Company_Knowledge import Company_Knowledge
from src.Suppliers_Knowledge import Suppliers_Knowledge


def set_and_run_simulation(
    min_salary,
    mean_salary,
    customer_attitudes,
    marketing_config
):
    
    n_clients = 50
    products=["product_1","product_2","product_3"]
    mean_alpha_quintiles = { i: [0.15, 0.13, 0.12, 0.1, 0.08] for i in range(len(products)) }
    sd_alpha = { i: 0.02 for i in range(len(products)) }
    companies_names = ["A", "B", "C"]
    initial_products_stock=[{
        'product_1':50,'product_2':50,'product_3':50
    },
    {
        'product_1':50,'product_2':50,'product_3':50
    },
    {
        'product_1':50,'product_2':50,'product_3':50
    }]
    initial_product_revenue=[{
        'product_1':3600,'product_2':3600,'product_3':3600
    },
    {
        'product_1':3600,'product_2':3600,'product_3':3600
    },
    {
        'product_1':3600,'product_2':3600,'product_3':3600
    }]
    subproduct_stock=[{
        "product_1":{"stock":0,"price":60},
        "product_2":{"stock":0,"price":60},
        "product_3":{"stock":0,"price":60}
    },
    {
        "product_1":{"stock":0,"price":60},
        "product_2":{"stock":0,"price":60},
        "product_3":{"stock":0,"price":60}
    },
    {
        "product_1":{"stock":0,"price":60},
        "product_2":{"stock":0,"price":60},
        "product_3":{"stock":0,"price":60}
    }]
    products_prices = [
        {
            "product_1":{"stock":20,"price":120},
            "product_2":{"stock":20,"price":120},
            "product_3":{"stock":20,"price":120}
        },
        {
            "product_1":{"stock":20,"price":120},
            "product_2":{"stock":20,"price":120},
            "product_3":{"stock":20,"price":120}
        },
        {
            "product_1":{"stock":20,"price":120},
            "product_2":{"stock":20,"price":120},
            "product_3":{"stock":20,"price":120}
        }
    ]
    max_revenue_percent=[{
        "product_1":100,
        "product_2":100,
        "product_3":100
    },
    {
        "product_1":100,
        "product_2":100,
        "product_3":100
    },
    {
        "product_1":100,
        "product_2":100,
        "product_3":100
    }]
    total_inversion=[{
        "product_1":3000,
        "product_2":3000,
        "product_3":3000
    },
    {
        "product_1":3000,
        "product_2":3000,
        "product_3":3000
    },
    {
        "product_1":3000,
        "product_2":3000,
        "product_3":3000
    }]
    suppliers_products = [
        {
            'product_1': {'quantity': 500000, 'min_price': 30},
            'product_2': {'quantity': 500000, 'min_price': 30},
            'product_3': {'quantity': 500000, 'min_price': 30},
        }
    ]
    subproducts={"product_1":{"product_1":1},"product_2":{"product_2":1},"product_3":{"product_3":1}}
    supplied_subproducts_by_supplier={"Suministrador1":["product1","product2","product3"]}
    company_products_popularity={
        "A":{
                "product_1": 80,"product_2": 80,"product_3": 80
            },
        "B":{
                "product_1": 80,"product_2": 80,"product_3": 80
            },
        "C":{
                "product_1": 80,"product_2": 80,"product_3": 80
            }
    }

    
    companies_rules = './src/Knowledge/Companies_Rules.json'
    companies_functions = './src/Knowledge/Companies_Functions.json'
    companies_vars = './src/Knowledge/Companies_Vars.json'

    suppliers_rules = './src/Knowledge/Suppliers_Rules.json'
    suppliers_functions = './src/Knowledge/Suppliers_Functions.json'
    suppliers_vars = './src/Knowledge/Suppliers_Vars.json'

    companies_knowledge = Company_Knowledge(companies_rules,companies_functions, companies_vars)
    suppliers_knowledge = Suppliers_Knowledge(suppliers_rules,suppliers_functions, suppliers_vars)

    log_file_path = os.path.join(os.getcwd(), 'src/simulation_logs.log')

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file_path,
        filemode='w',  
        level=logging.INFO,
        format='%(message)s',
    )
    
    customers=[]
    for i in range(n_clients):
        attitude=random.choices([at for at in customer_attitudes],[customer_attitudes[at] for at in customer_attitudes])[0]
        customer = CustomerAgent(f"Cliente{i}", attitude)
        customers.append(customer)
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
            max_revenue_percent[i],
            total_inversion[i]
        )
        for i in range(len(companies_names))
    }
    suppliers = {
        f"Suministrador{i+1}": SupplierAgent(f"Suministrador{i+1}", suppliers_products[i], suppliers_knowledge)
        for i in range(len(suppliers_products))
    }

    company_products_prices = {
        companies_names[i]: {
            product:products_prices[i][product]
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

    run_simulation(market_env, 12)

    return market_env
