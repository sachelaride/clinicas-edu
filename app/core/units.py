from typing import Dict, Tuple, Optional

# Define base units for each dimension
BASE_UNITS: Dict[str, str] = {
    "mass": "kg",
    "volume": "L",
    "length": "m",
}

# Define conversion factors to the base unit for each dimension
# Factor is how many of the current unit make up one base unit
# e.g., 1 kg = 1 kg (factor 1)
#       1 g = 0.001 kg (factor 0.001)
#       1 mg = 0.000001 kg (factor 0.000001)
#       1 mcg = 0.000000001 kg (factor 0.000000001)
UNIT_CONVERSIONS: Dict[str, Dict[str, float]] = {
    "mass": {
        "Quilograma (kg)": 1.0,
        "Grama (g)": 0.001,
        "Miligrama (mg)": 0.000001,
        "Micrograma (mcg)": 0.000000001,
    },
    "volume": {
        "Litro (L)": 1.0,
        "Mililitro (mL)": 0.001,
        "Microlitro (µL)": 0.000001,
    },
    "length": {
        "Metro (m)": 1.0,
        "Centímetro (cm)": 0.01,
        "Milímetro (mm)": 0.001,
    },
}

def get_unit_dimension(unit: str) -> Optional[str]:
    """Returns the dimension (e.g., 'mass', 'volume') for a given unit."""
    for dimension, units in UNIT_CONVERSIONS.items():
        if unit in units:
            return dimension
    return None

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Converts a value from one unit to another within the same dimension."""
    from_dimension = get_unit_dimension(from_unit)
    to_dimension = get_unit_dimension(to_unit)

    if from_dimension is None or to_dimension is None:
        raise ValueError(f"Unknown unit: {from_unit} or {to_unit}")
    
    if from_dimension != to_dimension:
        raise ValueError(f"Cannot convert between different dimensions: {from_unit} ({from_dimension}) to {to_unit} ({to_dimension})")

    # Convert to base unit first
    value_in_base = value * UNIT_CONVERSIONS[from_dimension][from_unit]
    
    # Convert from base unit to target unit
    converted_value = value_in_base / UNIT_CONVERSIONS[to_dimension][to_unit]
    
    return converted_value

def get_base_unit_for_dimension(dimension: str) -> Optional[str]:
    """Returns the base unit for a given dimension."""
    return BASE_UNITS.get(dimension)

def get_conversion_factor(from_unit: str, to_base_unit: str) -> float:
    """Returns the conversion factor from a unit to its base unit."""
    dimension = get_unit_dimension(from_unit)
    if dimension is None or to_base_unit != BASE_UNITS[dimension]:
        raise ValueError(f"Invalid conversion: {from_unit} to {to_base_unit}")
    return UNIT_CONVERSIONS[dimension][from_unit]
