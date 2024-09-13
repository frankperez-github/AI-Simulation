import random

class MarketEnvironment:
    def __init__(self, data):
        self.public_variables = {
            'product_prices': {},
            'product_gross_income': {},
            'available_products': {},
            'selling_companies': {},
            'market_demand': {},
            'competition_levels': {},
            'market_trends': {},
            'revenue': {},
            'company_popularity': {},
            'dollar_behavior': 0,
            'product_dict':{}
        }

        self.hidden_variables = {
            'company_strategies': {},
            'supplier_conditions': {},
        }

        self.load_data(data)
        self.initialize_market_variables()

    def load_data(self, data):

        # Obtener los nombres únicos de la columna 'Product line'
        unique_products = data['Product line'].unique()

        # Crear el diccionario con un ID único para cada producto, comenzando desde 0
        product_dict = {product: idx for idx, product in enumerate(unique_products)}
        self.public_variables['product_dict']=product_dict

        # Temporarily store the companies (branches) selling each product to compute competition levels
        product_competition = {}

        # Populate product_prices and available_products
        for _, row in data.iterrows():
            product = row['Product line']
            income = row['gross income']  # Se usará solo el gross income
            branch = row['Branch']
            price = row['Unit price']
            quantity = row['Quantity']

            # Add product prices by company (branch)
            if branch not in self.public_variables['product_prices']:
                self.public_variables['product_prices'][branch] = {}
                self.public_variables['product_gross_income'][branch] = {}  # Se almacena el ingreso bruto

            self.public_variables['product_prices'][branch][product] = price
            self.public_variables['product_gross_income'][branch][product] = income

            # Add available products (stock)
            if product not in self.public_variables['available_products']:
                self.public_variables['available_products'][product] = 0
            self.public_variables['available_products'][product] += quantity

            # Track which branches sell this product for competition level calculation
            if product not in product_competition:
                product_competition[product] = set()
            product_competition[product].add(branch)

        # Update competition_levels based on how many branches sell each product
        for product, branches in product_competition.items():
            self.public_variables['competition_levels'][product] = len(branches)

    def initialize_market_variables(self):
        product_lines = self.public_variables['available_products'].keys()
        for product in product_lines:
            self.public_variables['market_demand'][product] = 0
            self.public_variables['market_trends'][product] = 0

    def update_environment(self):
        self.public_variables['dollar_behavior'] = random.choice([-1, 0, 1])
        self.adjust_prices_based_on_dollar()

        for company in self.public_variables['company_popularity']:
            change = random.uniform(-0.5, 0.5)
            new_popularity = self.public_variables['company_popularity'][company] + change
            self.public_variables['company_popularity'][company] = min(max(new_popularity, 1), 10)

        print("El entorno del mercado ha sido actualizado.")

    def adjust_prices_based_on_dollar(self):
        for company, products in self.public_variables['product_prices'].items():
            for product, price in products.items():
                if self.public_variables['dollar_behavior'] == 1:  # Dólar en aumento
                    self.public_variables['product_prices'][company][product] = price * 1.05  # Aumentar precios un 5%
                elif self.public_variables['dollar_behavior'] == -1:  # Dólar en caída
                    self.public_variables['product_prices'][company][product] = price * 0.95  # Reducir precios un 5%