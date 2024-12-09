from decimal import Decimal, getcontext

def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# Using Decimal to avoid any long floating points where they don't belong.
## For example, if a computation should come out to 58.0, it can become 57.99999999 using normal floats. Decimal avoids that.
def to_decimal(value, default=Decimal('0.0')):
    try:
        # Checking if the var is empty to avoid conversion errors.
        if value is None or value == '':
            return default
        return Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return default

# Formula to convert food weight and serving size form whatever unit the user used to grams.
def convert_to_grams(weight: Decimal, unit: str, ounces: Decimal = Decimal('0.0')) -> Decimal:
    # UPDATE: The function now uses a dictionary to pull the conversion rate.
    conversion_factors = {
        "kg": Decimal("1000"),
        "oz": Decimal("28.3495"),
        "lb": Decimal("453.592"),
        "mL": Decimal("1"),
        "mg": Decimal("0.001")
    }
    # For most units, we just return weight * the conversion factor passed on the function call.
    if unit in conversion_factors:
        return weight * conversion_factors[unit]
    # Lbs and oz is a slightly special case so we call those explicitly here.
    elif unit == "lb_oz":
        return (weight * conversion_factors["lb"]) + (ounces * conversion_factors["oz"])
    # This is triggered is the unit is "g" as that is not in conversion_factors. In that case, just return the weight.
    else:
        return weight

def format_weight(weight):
    weight_str = str(weight).rstrip('0').rstrip('.')
    return weight_str if '.' in weight_str else str(int(weight))

def format_macros(macro: Decimal) -> str:
    rounded_macro = str(round(macro, 2))
    if rounded_macro.endswith('.00'):
        return str(int(macro))
    else:
        return rounded_macro.rstrip('0').rstrip('.')