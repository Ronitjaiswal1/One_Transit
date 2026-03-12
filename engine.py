import simpy
import random

class BusAgent:
    def __init__(self, env, name, battery=250):
        self.env = env
        self.name = name
        self.battery = battery # kWh
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Simulate travel between stops
            travel_time = random.randint(10, 30)
            yield self.env.timeout(travel_time)
            
            # 2026 Physics: 1.3 kWh per km
            self.battery -= (travel_time * 0.5) 
            
            if self.battery < 50: # 20% Threshold
                print(f"{self.env.now}: {self.name} redirecting to Okhla EV Hub.")
                yield self.env.process(self.charge())

    def charge(self):
        # 240kW Fast Charging simulation
        charge_needed = 250 - self.battery
        duration = (charge_needed / 240) * 60
        yield self.env.timeout(duration)
        self.battery = 250
        print(f"{self.env.now}: {self.name} fully charged.")

env = simpy.Environment()
buses = [BusAgent(env, f"Bus_{i}") for i in range(5)] # Test with 5 agents
env.run(until=500)