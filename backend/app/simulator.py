from __future__ import annotations

import copy
import math
import time
from dataclasses import dataclass

import simpy

from .models import BeamState, BusState, KpiState, SceneId, TwinSnapshot


@dataclass
class MovingBus:
    bus: BusState
    path: list[tuple[float, float]]
    speed: float
    t: float = 0.0


def _scene_seed(scene: SceneId) -> tuple[str, str, list[MovingBus], list[BeamState], KpiState]:
    if scene == 'grid':
        buses = [
            MovingBus(BusState(id='Bus-03-EV', fleet='risk', x=22, y=55, angle=12, battery=77, delayMinutes=1.2, nextRelayMinutes=7, thermalRisk='high'), [(22, 55), (29, 58), (37, 62)], 0.006),
            MovingBus(BusState(id='Bus-12-EV', fleet='risk', x=34, y=51, angle=8, battery=73, delayMinutes=1.6, nextRelayMinutes=8, thermalRisk='high'), [(34, 51), (40, 54), (47, 58)], 0.005),
            MovingBus(BusState(id='Bus-19-EV', fleet='risk', x=52, y=61, angle=-10, battery=69, delayMinutes=2.1, nextRelayMinutes=9, thermalRisk='high'), [(52, 61), (57, 58), (64, 53)], 0.007),
            MovingBus(BusState(id='DEPOT-NODE', fleet='traffic', x=61, y=48, angle=0, battery=100, delayMinutes=0, nextRelayMinutes=0, thermalRisk='low'), [(61, 48), (61, 48)], 0.0),
        ]
        beams = [
            BeamState(id='v2g-1', fromId='Bus-03-EV', toId='DEPOT-NODE', mode='v2g', color='#ff5168'),
            BeamState(id='v2g-2', fromId='Bus-12-EV', toId='DEPOT-NODE', mode='v2g', color='#ff5168'),
            BeamState(id='v2g-3', fromId='Bus-19-EV', toId='DEPOT-NODE', mode='v2g', color='#ff5168'),
        ]
        return (
            'Okhla Depot, ISBT',
            'Grid-responsive V2G load-shaving in the 3 PM - 5 PM policy window.',
            buses,
            beams,
            KpiState(fleetOptimization=92, gridLoad='Critical', activeAlerts=3),
        )

    if scene == 'relay':
        buses = [
            MovingBus(BusState(id='DTC-101E', fleet='risk', x=32, y=46, angle=13, battery=88, delayMinutes=0.4, nextRelayMinutes=4, thermalRisk='low'), [(32, 46), (38, 48), (43, 49)], 0.004),
            MovingBus(BusState(id='DTC-303E', fleet='cluster', x=57, y=44, angle=22, battery=81, delayMinutes=0.0, nextRelayMinutes=0, thermalRisk='low'), [(57, 44), (57, 44)], 0.0),
            MovingBus(BusState(id='DTC-540E', fleet='cluster', x=66, y=59, angle=14, battery=79, delayMinutes=1.1, nextRelayMinutes=11, thermalRisk='medium'), [(66, 59), (61, 55), (56, 51)], 0.006),
        ]
        beams = [
            BeamState(id='relay-1', fromId='DTC-101E', toId='DTC-303E', mode='handover', color='#00E5FF'),
        ]
        return (
            'Sarai Kale Khan ISBT',
            'Unlinked relay crew handover and continuity state.',
            buses,
            beams,
            KpiState(fleetOptimization=94, gridLoad='Stable', activeAlerts=2),
        )

    if scene == 'v2i':
        buses = [
            MovingBus(BusState(id='DTC-43EEV', fleet='risk', x=34, y=58, angle=-12, battery=71, delayMinutes=4.5, nextRelayMinutes=16, thermalRisk='medium'), [(34, 58), (43, 56), (51, 54), (59, 52)], 0.012),
            MovingBus(BusState(id='SIGNAL-01', fleet='traffic', x=61, y=43, angle=0, battery=100, delayMinutes=0, nextRelayMinutes=0, thermalRisk='low'), [(61, 43), (61, 43)], 0.0),
            MovingBus(BusState(id='CAR-11', fleet='traffic', x=18, y=34, angle=-9, battery=100, delayMinutes=0, nextRelayMinutes=0, thermalRisk='low'), [(18, 34), (25, 36), (32, 37)], 0.007),
        ]
        beams = [
            BeamState(id='v2i-1', fromId='DTC-43EEV', toId='SIGNAL-01', mode='v2i', color='#00E5FF'),
        ]
        return (
            'Tilak Marg, Delhi',
            'V2I greenwave extension for buses delayed over 3 minutes.',
            buses,
            beams,
            KpiState(fleetOptimization=93, gridLoad='Elevated', activeAlerts=2),
        )

    buses = [
        MovingBus(BusState(id='DTC-402EV', fleet='dtc', x=21, y=30, angle=-18, battery=82, delayMinutes=0.7, nextRelayMinutes=7, thermalRisk='low'), [(20, 30), (28, 34), (37, 39), (45, 43)], 0.012),
        MovingBus(BusState(id='DTC-303E', fleet='dtc', x=57, y=51, angle=20, battery=78, delayMinutes=0.1, nextRelayMinutes=5, thermalRisk='low'), [(56, 51), (62, 48), (70, 45)], 0.01),
        MovingBus(BusState(id='DTC-101E', fleet='cluster', x=67, y=45, angle=18, battery=88, delayMinutes=0.0, nextRelayMinutes=4, thermalRisk='low'), [(67, 45), (67, 45)], 0.0),
        MovingBus(BusState(id='CL-924', fleet='cluster', x=12, y=42, angle=-16, battery=76, delayMinutes=1.2, nextRelayMinutes=9, thermalRisk='medium'), [(10, 42), (18, 38), (27, 35)], 0.011),
        MovingBus(BusState(id='CL-551', fleet='cluster', x=74, y=63, angle=12, battery=84, delayMinutes=0.9, nextRelayMinutes=12, thermalRisk='low'), [(71, 62), (66, 58), (59, 55)], 0.009),
    ]
    beams = [
        BeamState(id='relay-main', fromId='DTC-303E', toId='DTC-101E', mode='handover', color='#00E5FF'),
        BeamState(id='flow-main', fromId='DTC-402EV', toId='DTC-303E', mode='handover', color='#36ffb1'),
    ]
    return (
        'Kashmere Gate ISBT',
        'Unified command digital twin with fleet and relay visibility.',
        buses,
        beams,
        KpiState(fleetOptimization=94, gridLoad='Stable', activeAlerts=2),
    )


class TwinSimulator:
    def __init__(self, scene: SceneId):
        self.scene = scene
        self.env = simpy.Environment()
        self.title, self.subtitle, self._moving_buses, self._beams, self._kpi = _scene_seed(scene)
        self.env.process(self._tick())

    @staticmethod
    def _point(path: list[tuple[float, float]], t: float) -> tuple[float, float, float]:
        if len(path) < 2:
            return path[0][0], path[0][1], 0.0

        t = max(0.0, min(0.999, t))
        segs = len(path) - 1
        p = t * segs
        i = int(p)
        r = p - i

        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        x = x1 + (x2 - x1) * r
        y = y1 + (y2 - y1) * r
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        return x, y, angle

    def _tick(self):
        while True:
            for entry in self._moving_buses:
                if entry.speed > 0 and len(entry.path) > 1:
                    entry.t = (entry.t + entry.speed) % 1.0
                    x, y, angle = self._point(entry.path, entry.t)
                    entry.bus.x = x
                    entry.bus.y = y
                    entry.bus.angle = angle
                    entry.bus.battery = max(18.0, entry.bus.battery - 0.03)
                    if self.scene == 'v2i' and entry.bus.id == 'DTC-43EEV':
                        entry.bus.delayMinutes = max(3.2, entry.bus.delayMinutes - 0.002)
            yield self.env.timeout(1)

    def snapshot(self) -> TwinSnapshot:
        self.env.run(until=self.env.now + 1)
        buses = [copy.deepcopy(entry.bus) for entry in self._moving_buses]
        kpi = copy.deepcopy(self._kpi)

        if self.scene == 'grid':
            avg_battery = sum(bus.battery for bus in buses if bus.fleet != 'traffic') / max(1, len([b for b in buses if b.fleet != 'traffic']))
            kpi.fleetOptimization = 90 if avg_battery < 72 else 92
        elif self.scene == 'v2i':
            delayed = [bus for bus in buses if bus.delayMinutes > 3]
            kpi.activeAlerts = max(1, len(delayed))

        return TwinSnapshot(
            scene=self.scene,
            timestamp=time.time(),
            title=self.title,
            subtitle=self.subtitle,
            buses=buses,
            beams=copy.deepcopy(self._beams),
            kpi=kpi,
        )
