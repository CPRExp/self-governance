"""
Python model 'cpr.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np
import xarray as xr

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Delay, Integ, Initial
from pysd.py_backend.lookups import HardcodedLookups
from pysd import Component

__pysd_version__ = "3.14.1"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


_subscript_dict = {"F": ["F1", "F2", "F3", "F4"]}

component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 1,
    "final_time": lambda: 30,
    "time_step": lambda: 0.125,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Year",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Year",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Effect of Groundwater on Pumping",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "minimum_groundwater_effect_on_pumping": 2,
        "maximum_groundwater_effect_on_pumping": 1,
        "groundwater_ratio": 1,
    },
)
def effect_of_groundwater_on_pumping():
    return (
        minimum_groundwater_effect_on_pumping()
        + (
            maximum_groundwater_effect_on_pumping()
            - minimum_groundwater_effect_on_pumping()
        )
        * groundwater_ratio()
    )


@component.add(
    name="Maximum Groundwater Effect on Pumping",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def maximum_groundwater_effect_on_pumping():
    return 1


@component.add(
    name="Groundwater Ratio",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "groundwater": 1,
        "initial_groundwater": 1,
        "table_for_effect_of_groundwater_on_pumping": 1,
    },
)
def groundwater_ratio():
    return table_for_effect_of_groundwater_on_pumping(
        groundwater() / initial_groundwater()
    )


@component.add(
    name="Initial Groundwater",
    units="m3",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_groundwater": 1},
    other_deps={
        "_initial_initial_groundwater": {"initial": {"groundwater": 1}, "step": {}}
    },
)
def initial_groundwater():
    return _initial_initial_groundwater()


_initial_initial_groundwater = Initial(
    lambda: groundwater(), "_initial_initial_groundwater"
)


@component.add(
    name="Minimum Groundwater Effect on Pumping",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def minimum_groundwater_effect_on_pumping():
    return 0


@component.add(
    name="Table for Effect of Groundwater on Pumping",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_for_effect_of_groundwater_on_pumping"
    },
)
def table_for_effect_of_groundwater_on_pumping(x, final_subs=None):
    return _hardcodedlookup_table_for_effect_of_groundwater_on_pumping(x, final_subs)


_hardcodedlookup_table_for_effect_of_groundwater_on_pumping = HardcodedLookups(
    [
        0.0,
        0.0344828,
        0.0689655,
        0.103448,
        0.137931,
        0.172414,
        0.206897,
        0.241379,
        0.275862,
        0.310345,
        0.344828,
        0.37931,
        0.413793,
        0.448276,
        0.482759,
        0.517241,
        0.551724,
        0.586207,
        0.62069,
        0.655172,
        0.689655,
        0.724138,
        0.758621,
        0.793103,
        0.827586,
        0.862069,
        0.896552,
        0.931035,
        0.965517,
        1.0,
    ],
    [
        0.0,
        0.00942264,
        0.013251,
        0.0186055,
        0.0260666,
        0.0364086,
        0.0506406,
        0.0700314,
        0.0960957,
        0.130499,
        0.174837,
        0.230251,
        0.296907,
        0.373498,
        0.457003,
        0.542997,
        0.626502,
        0.703093,
        0.769749,
        0.825163,
        0.869501,
        0.903904,
        0.929969,
        0.949359,
        0.963591,
        0.973933,
        0.981394,
        0.986749,
        0.990577,
        1.0,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_for_effect_of_groundwater_on_pumping",
)


@component.add(
    name="Pumping",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_pumping": 1, "effect_of_groundwater_on_pumping": 1},
)
def pumping():
    return desired_pumping() * effect_of_groundwater_on_pumping()


@component.add(
    name="Pumping YO",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_pumping_yo": 1, "effect_of_groundwater_on_pumping": 1},
)
def pumping_yo():
    return desired_pumping_yo() * effect_of_groundwater_on_pumping()


@component.add(
    name="Orchard Growth",
    units="Hectares/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"profit": 1, "decision": 1},
)
def orchard_growth():
    return if_then_else(profit() > -5000, lambda: np.maximum(0, decision()), lambda: 0)


@component.add(
    name="Average Lifetime", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def average_lifetime():
    return 20


@component.add(
    name="Avg Water Cost",
    units="$/m3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_avg_water_cost": 1},
    other_deps={
        "_integ_avg_water_cost": {
            "initial": {"indicated_water_cost": 1},
            "step": {"change_in_water_cost": 1},
        }
    },
)
def avg_water_cost():
    return _integ_avg_water_cost()


_integ_avg_water_cost = Integ(
    lambda: change_in_water_cost(),
    lambda: indicated_water_cost(),
    "_integ_avg_water_cost",
)


@component.add(
    name="Change in Water Cost",
    units="$/m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "indicated_water_cost": 1,
        "avg_water_cost": 1,
        "time_to_change_water_cost": 1,
    },
)
def change_in_water_cost():
    return (indicated_water_cost() - avg_water_cost()) / time_to_change_water_cost()


@component.add(
    name="Constant Groundwater Inflow",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"treatment_delay": 1},
)
def constant_groundwater_inflow():
    return if_then_else(treatment_delay() == 1, lambda: 10.25, lambda: 11)


@component.add(
    name="Cost",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchard_cost": 1, "water_cost": 1},
)
def cost():
    return orchard_cost() + water_cost()


@component.add(
    name="Decision",
    units="Hectares/Year",
    limits=(-100.0, 100.0, 1.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def decision():
    return 100


@component.add(
    name="Desired Pumping",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchards": 1, "water_required": 1},
)
def desired_pumping():
    return orchards() * water_required()


@component.add(
    name="Desired Pumping YO",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"young_orchards": 1, "water_required_yo": 1},
)
def desired_pumping_yo():
    return young_orchards() * water_required_yo()


@component.add(
    name="Discard Rate",
    units="Hectares/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_discard_rate": 1, "discard_time": 1, "orchards": 1},
    other_deps={
        "_delay_discard_rate": {
            "initial": {"decision": 1, "growth_delay": 1},
            "step": {"decision": 1, "growth_delay": 1},
        }
    },
)
def discard_rate():
    return np.minimum(
        np.maximum(0, -_delay_discard_rate()), orchards() / discard_time()
    )


_delay_discard_rate = Delay(
    lambda: decision(),
    lambda: growth_delay() * 3,
    lambda: decision(),
    lambda: 3,
    time_step,
    "_delay_discard_rate",
)


@component.add(
    name="Discard Time", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def discard_time():
    return 1


@component.add(
    name="Elasticity of Orchards",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def elasticity_of_orchards():
    return 0.7


@component.add(
    name="Elasticity of Water",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def elasticity_of_water():
    return 0.3


@component.add(
    name="Revenue",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "production": 1,
        "price": 1,
        "orchard_unit_selling_price": 1,
        "discard_rate": 1,
    },
)
def revenue():
    return production() * price() + discard_rate() * orchard_unit_selling_price()


@component.add(
    name="Groundwater",
    units="m3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_groundwater": 1},
    other_deps={
        "_integ_groundwater": {
            "initial": {"gw_budget": 1},
            "step": {"total_inflow": 1, "total_pumping": 1},
        }
    },
)
def groundwater():
    """
    Multiplied by 4 to replicate the multi-agent scenario
    """
    return _integ_groundwater()


_integ_groundwater = Integ(
    lambda: total_inflow() - total_pumping(),
    lambda: gw_budget() * 4,
    "_integ_groundwater",
)


@component.add(
    name="Growth Delay",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"treatment_delay": 1},
)
def growth_delay():
    return treatment_delay() / 3


@component.add(
    name="GW Budget",
    units="m3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_gw_budget": 1},
    other_deps={
        "_integ_gw_budget": {
            "initial": {"initial_gw_budget": 1},
            "step": {"gw_inflow": 1, "pumping": 1, "pumping_yo": 1},
        }
    },
)
def gw_budget():
    return _integ_gw_budget()


_integ_gw_budget = Integ(
    lambda: gw_inflow() - pumping() - pumping_yo(),
    lambda: initial_gw_budget(),
    "_integ_gw_budget",
)


@component.add(
    name="GW Inflow",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"constant_groundwater_inflow": 1},
)
def gw_inflow():
    return constant_groundwater_inflow()


@component.add(
    name="GW Threshold", units="m3", comp_type="Constant", comp_subtype="Normal"
)
def gw_threshold():
    return 200


@component.add(
    name="Indicated Water Cost",
    units="$/m3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "max_water_cost": 1,
        "water_cost_sensitivity": 1,
        "water_cost_inflection": 1,
        "normal_groundwater": 1,
        "water_cost_growth_rate": 1,
        "water_cost_slope": 1,
    },
)
def indicated_water_cost():
    return max_water_cost() / (
        1
        + water_cost_slope()
        * np.exp(
            water_cost_growth_rate() * (normal_groundwater() - water_cost_inflection())
        )
    ) ** (1 / water_cost_sensitivity())


@component.add(
    name="Initial GW Budget", units="m3", comp_type="Constant", comp_subtype="Normal"
)
def initial_gw_budget():
    return 100


@component.add(
    name="Initial Orchards",
    units="Hectares",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_orchards():
    return 100


@component.add(
    name="Initial Profit", units="$", comp_type="Constant", comp_subtype="Normal"
)
def initial_profit():
    return 10000


@component.add(
    name="Water Cost Sensitivity",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def water_cost_sensitivity():
    return 0.5


@component.add(
    name="Initial Young Orchards",
    units="Hectares",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"treatment_delay": 1},
)
def initial_young_orchards():
    return if_then_else(treatment_delay() == 1, lambda: 1.66667, lambda: 6.66667)


@component.add(
    name="Max Water Cost", units="$/m3", comp_type="Constant", comp_subtype="Normal"
)
def max_water_cost():
    return 3000


@component.add(
    name="Normal Groundwater",
    units="1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"groundwater": 1, "gw_threshold": 1},
)
def normal_groundwater():
    return groundwater() / gw_threshold()


@component.add(
    name="Normal Orchard Unit Fixed Cost",
    units="$/Hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def normal_orchard_unit_fixed_cost():
    return 40


@component.add(
    name="Normal Orchard Unit Variable Cost",
    units="$/Hectare/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def normal_orchard_unit_variable_cost():
    return 20


@component.add(
    name="Obsolescence Rate",
    units="Hectares/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchards": 1, "average_lifetime": 1},
)
def obsolescence_rate():
    return orchards() / average_lifetime()


@component.add(
    name="Orchard Cost",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchard_fixed_cost": 1, "orchard_variable_cost": 1},
)
def orchard_cost():
    return orchard_fixed_cost() + orchard_variable_cost()


@component.add(
    name="Orchard Fixed Cost",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchard_growth": 1, "orchard_unit_fixed_cost": 1},
)
def orchard_fixed_cost():
    return orchard_growth() * orchard_unit_fixed_cost()


@component.add(
    name="Orchard Unit Fixed Cost",
    units="$/Hectare",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"normal_orchard_unit_fixed_cost": 1},
)
def orchard_unit_fixed_cost():
    return normal_orchard_unit_fixed_cost()


@component.add(
    name="Orchard Unit Selling Price",
    units="$/Hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def orchard_unit_selling_price():
    return 30


@component.add(
    name="Orchard Unit Variable Cost",
    units="$/(Year*Hectare)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"normal_orchard_unit_variable_cost": 1},
)
def orchard_unit_variable_cost():
    return normal_orchard_unit_variable_cost()


@component.add(
    name="Orchard Variable Cost",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"orchards": 1, "orchard_unit_variable_cost": 1},
)
def orchard_variable_cost():
    return orchards() * orchard_unit_variable_cost()


@component.add(
    name="Orchards",
    units="Hectares",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_orchards": 1},
    other_deps={
        "_integ_orchards": {
            "initial": {"initial_orchards": 1},
            "step": {"y3too": 1, "discard_rate": 1, "obsolescence_rate": 1},
        }
    },
)
def orchards():
    return _integ_orchards()


_integ_orchards = Integ(
    lambda: y3too() - discard_rate() - obsolescence_rate(),
    lambda: initial_orchards(),
    "_integ_orchards",
)


@component.add(
    name="Price", units="$/Tonne", comp_type="Constant", comp_subtype="Normal"
)
def price():
    return 100


@component.add(
    name="Production",
    units="Tonnes/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "reference_production": 1,
        "orchards": 1,
        "reference_orchards": 1,
        "elasticity_of_orchards": 1,
        "pumping": 1,
        "reference_water": 1,
        "elasticity_of_water": 1,
    },
)
def production():
    return (
        reference_production()
        * (orchards() / reference_orchards()) ** elasticity_of_orchards()
        * (pumping() / reference_water()) ** elasticity_of_water()
    )


@component.add(
    name="Profit",
    units="$",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_profit": 1},
    other_deps={
        "_integ_profit": {"initial": {"initial_profit": 1}, "step": {"profit_rate": 1}}
    },
)
def profit():
    return _integ_profit()


_integ_profit = Integ(lambda: profit_rate(), lambda: initial_profit(), "_integ_profit")


@component.add(
    name="Profit Rate",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"revenue": 1, "cost": 1},
)
def profit_rate():
    return revenue() - cost()


@component.add(
    name="Reference Orchards",
    units="Hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reference_orchards():
    return 1


@component.add(
    name="Reference Production",
    units="Tonnes/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reference_production():
    return 1


@component.add(
    name="Reference Water", units="m3/Year", comp_type="Constant", comp_subtype="Normal"
)
def reference_water():
    return 1


@component.add(
    name="Young Orchards",
    units="Hectares",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"young_orchards_1": 1, "young_orchards_2": 1, "young_orchards_3": 1},
)
def young_orchards():
    return young_orchards_1() + young_orchards_2() + young_orchards_3()


@component.add(
    name="Young Orchards 1",
    units="Hectares",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_young_orchards_1": 1},
    other_deps={
        "_integ_young_orchards_1": {
            "initial": {"initial_young_orchards": 1},
            "step": {"orchard_growth": 1, "y1toy2": 1},
        }
    },
)
def young_orchards_1():
    return _integ_young_orchards_1()


_integ_young_orchards_1 = Integ(
    lambda: orchard_growth() - y1toy2(),
    lambda: initial_young_orchards(),
    "_integ_young_orchards_1",
)


@component.add(
    name="Young Orchards 2",
    units="Hectares",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_young_orchards_2": 1},
    other_deps={
        "_integ_young_orchards_2": {
            "initial": {"initial_young_orchards": 1},
            "step": {"y1toy2": 1, "y2toy3": 1},
        }
    },
)
def young_orchards_2():
    return _integ_young_orchards_2()


_integ_young_orchards_2 = Integ(
    lambda: y1toy2() - y2toy3(),
    lambda: initial_young_orchards(),
    "_integ_young_orchards_2",
)


@component.add(
    name="Time to Change Water Cost",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_to_change_water_cost():
    return 1


@component.add(
    name="Total Inflow",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"gw_inflow": 1},
)
def total_inflow():
    return gw_inflow()


@component.add(
    name="Total Pumping",
    units="m3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"pumping": 1, "pumping_yo": 1},
)
def total_pumping():
    return pumping() + pumping_yo()


@component.add(
    name="Treatment Delay",
    units="Year",
    limits=(1.0, 4.0, 4.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def treatment_delay():
    return 4


@component.add(
    name="Water Cost",
    units="$/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"pumping": 1, "pumping_yo": 1, "avg_water_cost": 1},
)
def water_cost():
    return (pumping() + pumping_yo()) * avg_water_cost()


@component.add(
    name="Water Cost Growth Rate",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def water_cost_growth_rate():
    return 3


@component.add(
    name="Water Cost Inflection",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def water_cost_inflection():
    return 0.75


@component.add(
    name="Y1ToY2",
    units="Hectares/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"young_orchards_1": 1, "growth_delay": 1},
)
def y1toy2():
    return young_orchards_1() / growth_delay()


@component.add(
    name="Water Cost Slope", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def water_cost_slope():
    return 1


@component.add(
    name="Water Required",
    units="m3/Hectare/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def water_required():
    return 0.1


@component.add(
    name="Water Required YO",
    units="m3/Hectare/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def water_required_yo():
    return 0.05


@component.add(
    name="Y3ToO",
    units="Hectares/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"young_orchards_3": 1, "growth_delay": 1},
)
def y3too():
    return young_orchards_3() / growth_delay()


@component.add(
    name="Y2ToY3",
    units="Hectares/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"young_orchards_2": 1, "growth_delay": 1},
)
def y2toy3():
    return young_orchards_2() / growth_delay()


@component.add(
    name="Young Orchards 3",
    units="Hectares",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_young_orchards_3": 1},
    other_deps={
        "_integ_young_orchards_3": {
            "initial": {"initial_young_orchards": 1},
            "step": {"y2toy3": 1, "y3too": 1},
        }
    },
)
def young_orchards_3():
    return _integ_young_orchards_3()


_integ_young_orchards_3 = Integ(
    lambda: y2toy3() - y3too(),
    lambda: initial_young_orchards(),
    "_integ_young_orchards_3",
)
