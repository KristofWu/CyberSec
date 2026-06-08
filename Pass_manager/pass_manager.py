
def add():
    service_add = input("Enter the name of the service: ")
    passwords[service_add] = input("Enter your password: ")

def retrieve():
    service_name = input("Choose which service would you like to get the password to? ")
    if service_name in passwords:
        print(f"This is the password for the service: {service_name}: {passwords[service_name]}")      
    else:
        print("There is no password for the service")

def show_all():
    for service, password in passwords.items():
        print(f"{service}: {password}")
    if not passwords:
        print("There are no passwords")

def delete():
    service_del = input("Which password would you like to delete? ")
    if service_del in passwords:
        passwords.pop(service_del)
    else:
        print("There is no such service")    

import json

try:
    with open("passwords.json", "r") as file:
        passwords = json.load(file)
except FileNotFoundError:
    passwords = {}



while True:
    print("\n===== Pass Manager =====")
    print("1. Add a new password")
    print("2. Retrieve your password")
    print("3. Show all services")
    print("4. Delete your password")
    print("5. Exit")

    choice = input("\nEnter your choice (1/2/3/4/5): ")

    if choice == '1':
        add()
    elif choice == '2':
        retrieve()
    elif choice == '3':
        show_all()    
    elif choice == '4':
        delete()
    elif choice == '5':
        with open("passwords.json", "w") as file:
            json.dump(passwords, file, indent=4)
        break
    else:
        print("Incorrect answer, please try again")




