
import json

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        self.load()

    def add(self):
        service_add = input("Enter the name of the service: ")
        self.passwords[service_add] = input("Enter your password: ")

    def retrieve(self):
        service_name = input("Choose which service would you like to get the password to? ")
        if service_name in self.passwords:
            print(f"This is the password for the service: {service_name}: {self.passwords[service_name]}")      
        else:
            print("There is no password for the service")

    def show_all(self):
        for service, password in self.passwords.items():
            print(f"{service}: {password}")
        if not self.passwords:
            print("There are no passwords")

    def delete(self):
        service_del = input("Which password would you like to delete? ")
        if service_del in self.passwords:
            self.passwords.pop(service_del)
        else:
            print("There is no such service")
    
    def save(self):
        with open("passwords.json", "w") as file:
            json.dump(self.passwords, file)

    def load(self):
        try:
            with open("passwords.json", "r") as file:
                self.passwords = json.load(file)
        except FileNotFoundError:
            pass #init already prepared an empty dictionary or self.passwords = {}

manager = PasswordManager()

while True:
    print("\n===== Pass Manager =====")
    print("1. Add a new password")
    print("2. Retrieve your password")
    print("3. Show all services")
    print("4. Delete your password")
    print("5. Exit")

    choice = input("\nEnter your choice (1/2/3/4/5): ")

    if choice == '1':
        manager.add()
    elif choice == '2':
        manager.retrieve()
    elif choice == '3':
        manager.show_all()    
    elif choice == '4':
        manager.delete()
    elif choice == '5':
        manager.save()
        break
    else:
        print("Incorrect answer, please try again")