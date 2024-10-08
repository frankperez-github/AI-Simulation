import random
from Simulation_settings import set_and_run_simulation

if __name__ == '__main__':

    n_households = 50
    products=["product_1","product_2","product_3"]
    min_salary = 600
    mean_salary = 1200
    mean_alpha_quintiles = { i: [0.15, 0.13, 0.12, 0.1, 0.08] for i in range(len(products)) }
    sd_alpha = { i: 0.02 for i in range(len(products)) }
    customer_attitudes = {'stingy': 0.25, 'populist': 0.25, 'cautious': 0.25, 'random': 0.25}
    customer_customer_attitudes = [random.choices(list(customer_attitudes.keys()), list(customer_attitudes.values()))[0] for _ in range(n_households)]
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
            'product_1': {'quantity': 5000, 'min_price': 30},
            'product_2': {'quantity': 5000, 'min_price': 30},
            'product_3': {'quantity': 5000, 'min_price': 30},
        }
    ]
    subproducts={"product_1":{"product_1":1},"product_2":{"product_2":1},"product_3":{"product_3":1}}
    supplied_subproducts_by_supplier={"Suministrador1":["product1","product2","product3"]}
    marketing_config = {'lose_popularity': 15, 'marketing_cost' : 100, 'popularity_by_sales': 0.1}
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


set_and_run_simulation(
    min_salary=min_salary,
    mean_salary=mean_salary,
    mean_alpha_quintiles=mean_alpha_quintiles,
    sd_alpha=sd_alpha,
    products=products,
    customer_attitudes=customer_attitudes,
    companies_names=companies_names,
    initial_products_stock=initial_products_stock,
    initial_product_revenue=initial_product_revenue,
    subproduct_stock=subproduct_stock,
    products_prices=products_prices,
    max_revenue_percent=max_revenue_percent,
    total_inversion=total_inversion,
    suppliers_products=suppliers_products,
    subproducts=subproducts,
    supplied_subproducts_by_supplier=supplied_subproducts_by_supplier,
    marketing_config=marketing_config,
    company_products_popularity=company_products_popularity,
    n_clients= n_households
)