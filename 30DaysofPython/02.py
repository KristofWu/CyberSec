

first_name = "Ania"
last_name = "Cool"
full_name = "Ania Cool"
country = "Poland"
City = "Stolec"
age = 20
year = 2000
is_married = False
is_true = True
is_light_on = True
personal_info = {
    "Czy lubię programować?": "Tak",
    "Czy lubię kawę?": "Tak",
    "Czy lubię herbatę?": "Tak",
    "Czy lubię wódkę?": "Nie",
}

print(type(first_name))
print(type(last_name))
print(type(full_name))
print(type(country))
print(type(City))
print(type(age))
print(type(year))
print(type(is_married))
print(type(is_true))
print(type(is_light_on))
print(type(personal_info))

print(len(first_name))
print(len(last_name))

variable_one = 5
variable_two = 4
total = variable_one + variable_two
diff = variable_one - variable_two
product = variable_one * variable_two
division = variable_one / variable_two
mod = variable_one % variable_two
exp = variable_one ** variable_two
floor_division = variable_one // variable_two
print("Var1: ", variable_one, "Var2: ", variable_two)
print("Total: ", total)
print("Difference: ", diff)
print("Product: ", product)
print("Division: ", division)
print("Modulus: ", mod)
print("Exponent: ", exp)
print("Floor Division: ", floor_division)  

rad = 30
area_of_circle = 3.14 * rad ** 2
print("Area of circle with radius: ", rad, " is: ", area_of_circle)
circum_of_circle = 2 * 3.14 * rad
print("Circumference of circle with radius: ", rad, " is: ", circum_of_circle)

input = float(input("Enter the radius of the circle: "))
area_of_user_circle = 3.14 * input ** 2
print("Area of circle with radius: ", input, " is: ", area_of_user_circle)
circum_of_user_circle = 2 * 3.14 * input
print("Circumference of circle with radius: ", input, " is: ", circum_of_user_circle)


