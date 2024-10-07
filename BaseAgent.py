class BDI_Agent:
    def __init__(self, name):
        self.name = name
        self.beliefs = {}
        self.desires = []
        self.intentions = []

    def perceive_environment(self, show_logs=True):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def form_desires(self, show_logs=True):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def plan_intentions(self, show_logs=True):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def act(self,market_env, show_logs=True):
        for intention in self.intentions:
            self.execute_intention(intention,market_env, show_logs)
        self.intentions=[]
            
    def execute_intention(self, intention, show_logs=True):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")
