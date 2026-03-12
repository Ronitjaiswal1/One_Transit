import pandas as pd

class DigitalBus:
    def __init__(self, bus_id, route_id, battery_capacity=250):
        self.bus_id = bus_id
        self.route_id = route_id
        self.battery_level = battery_capacity # in kWh
        self.is_merger_fleet = True # Marking as April 2026 merger fleet
        self.current_stop = None

    def consume_energy(self, distance_km):
        # 2026 Realistic Physics: 1.3 kWh per km
        consumption = distance_km * 1.3
        self.battery_level -= consumption
        
    def check_status(self):
        if self.battery_level < 50: # 20% Safety Buffer
            return "ALARM: Need Charging at Okhla/Dwarka Hub"
        return "Operational"