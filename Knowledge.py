import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import json

class Knowledge:
    def __init__(self):
        self.vars = {}
        self.rules = []
        self.simulation = None

    def load_vars(self, path):
        vars = json.load(open(path,))
        for var in vars:
            self.vars[var] = eval(vars[var])
        
    def load_functions(self, path):
        vars = json.load(open(path,))
        for var in vars:
            for elem in vars[var]:
                self.vars[var][elem] = eval(vars[var][elem])
        
    def load_rules(self, path):
        rules = json.load(open(path))
        for rule in rules['rules']:
            self.rules.append(eval(rule))
        control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(control_system)
