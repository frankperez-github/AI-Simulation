class BDI_Agent:
    def __init__(self, name):
        self.name = name
        self.beliefs = {}
        self.desires = {}
        self.intentions = []

    def perceive_environment(self):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def form_desires(self):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def plan_intentions(self):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")

    def act(self):
        for intention in self.intentions:
            self.execute_intention(intention)

    def execute_intention(self, intention):
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas.")
