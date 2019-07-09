from check_change_module import *

check = ['2 large pepperoni pizzas', '3 sugar free sodas']
test_new_orders = [
    'Make one of the pizzas small',
    'Make two of the drinks a regular',
    'Make 3 sodas regular',
    'Change a soda for wine',
    'Change the pizzas for pastas',
    'Change the sodas with cocktails'
]

valid_new_checks = [
    ['1 large pepperoni pizzas', '3 sugar free sodas', '1 small pizzas'],
    ['2 large pepperoni pizzas', '1 sugar free sodas', '2 regular drinks'],
    ['2 large pepperoni pizzas', '3 regular sodas'],
    ['2 large pepperoni pizzas', '2 sugar free sodas', '1  wine'],
    ['3 sugar free sodas', '2  pastas'],
    ['2 large pepperoni pizzas', '3  cocktails']
]

for key, new_order in enumerate(test_new_orders):
    new_check = change_check(check, new_order)
    assert new_check == valid_new_checks[key], f"Error in key {key}. The generated new check is not valid: {new_check}"