
import string

def encrypt_message():
    message = input("Enter message to be encrypted: ")
    key = int(input("This is a Caesar Cipher. Enter the key (number of positions to shift): "))
    outcome = ""

    for char in message:
        if char.isalpha():
            if char.isupper():
                position = ord(char) - ord('A')
                newposition = (position + key) % 26
                newcharacter = chr(newposition + ord('A'))
                outcome = outcome + newcharacter
            elif char.islower():
                position = ord(char) - ord('a')
                newposition = (position + key) % 26
                newcharacter = chr(newposition + ord('a'))
                outcome = outcome + newcharacter
        else:
            outcome = outcome + char

    print(outcome)

def decrypt_message():
    message = input("Enter message to be decrypted: ")
    key = int(input("This is a Caesar Cipher. Enter the key (number of positions to shift): "))
    outcome = ""

    for char in message:
        if char.isalpha():
            if char.isupper():
                position = ord(char) - ord('A')
                newposition = (position - key) % 26
                newcharacter = chr(newposition + ord('A'))
                outcome = outcome + newcharacter
            elif char.islower():
                position = ord(char) - ord('a')
                newposition = (position - key) % 26
                newcharacter = chr(newposition + ord('a'))
                outcome = outcome + newcharacter
        else:
            outcome = outcome + char

    print(outcome)

while True:
    print("===== CAESAR CIPHER MENU =====")
    print("1. Encrypt a message")
    print("2. Decrypt a message")
    print("3. Exit")

    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        encrypt_message()
    
    if choice == '2':
        decrypt_message()
    
    if choice == '3':
        break













