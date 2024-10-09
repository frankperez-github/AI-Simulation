import random
import csv
from src.Simulation_settings import set_and_run_simulation

def generate_statistics(selected_company_name, filename="simulation_results.csv"):
    base_header = [
        "simulacion_id",
        "ganancia_empresa",
        "min_salary",
        "mean_salary",
        "customer_attitude_stingy",
        "customer_attitude_populist",
        "customer_attitude_cautious",
        "customer_attitude_random",
        "lose_popularity",
        "marketing_cost"
    ]
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        header_written = False

        for i in range(10):
            min_salary = random.randint(500, 2000)
            mean_salary = random.randint(min_salary + 100, min_salary + 1000) 

            attitudes = [random.random() for _ in range(4)]
            total = sum(attitudes)
            customer_attitudes = {
                'stingy': attitudes[0] / total,
                'populist': attitudes[1] / total,
                'cautious': attitudes[2] / total,
                'random': attitudes[3] / total
            }

            marketing_config = {
                'lose_popularity': random.randint(5, 20),
                'marketing_cost': random.randint(30, 100),
                'popularity_by_sales': 0.1
            }

            market = set_and_run_simulation(
                min_salary=min_salary,
                mean_salary=mean_salary,
                customer_attitudes=customer_attitudes,
                marketing_config=marketing_config,
            )

            selected_company = market.get_company_data(selected_company_name)

            row = [
                i + 1,
                selected_company.total_revenue,
                min_salary,
                mean_salary,
                customer_attitudes['stingy'],
                customer_attitudes['populist'],
                customer_attitudes['cautious'],
                customer_attitudes['random'],
                marketing_config['lose_popularity'],
                marketing_config['marketing_cost']
            ]

            if not header_written:
                header = base_header[:]
                for product in selected_company.products.keys():
                    product_name = product.replace(" ", "_").lower()
                    header.extend([
                        f"precio_medio_{product_name}",
                        f"unidades_producidas_{product_name}",
                        f"unidades_vendidas_{product_name}",
                        f"precio_minimo_{product_name}",
                        f"precio_maximo_{product_name}",
                        f"popularidad_inicial_{product_name}",
                        f"popularidad_final_{product_name}"
                    ])
                writer.writerow(header)
                header_written = True

            for product in selected_company.products:
                row.extend([
                    selected_company.products[product]["produced_quantity"],
                    selected_company.products[product]["sold_quantity"],
                    min(selected_company.products[product]["prices_list"]),
                    sum(selected_company.products[product]["prices_list"])/len(selected_company.products[product]["prices_list"]),
                    max(selected_company.products[product]["prices_list"]),
                    selected_company.products[product]["initial_popularity"],
                    selected_company.products[product]["final_popularity"]
                ])

            writer.writerow(row)

if __name__ == '__main__':
    generate_statistics("A")
