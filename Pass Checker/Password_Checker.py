

import string
import pandas as pd



score = []
pwds = []
strength = []


while True:
    pwd = input("Enter your password: ")
    points_counter = 0
    if len(pwd) >= 8:    
        points_counter += 1
    if any(char.isupper() for char in pwd):
        points_counter += 1
    if any(char.islower() for char in pwd):
        points_counter += 1
    if any(char.isdigit() for char in pwd):
        points_counter += 1
    if any(char in string.punctuation for char in pwd):
        points_counter += 1
    if points_counter == 5:
        print("Your password is strong!")  
    elif points_counter < 5:
        print("Your password is weak, try again!")   
    print(f"Your password has {points_counter} out of 5 points.")
    
    score.append(points_counter)
    pwds.append(pwd)
    strength.append("5 - strong" if points_counter == 5 else "1-4 weak")
    print(f"Your score: {score}.")
    print(f"Your passwords: {pwds}.")
    print(f"Your passwords strength: {strength}.")

    answer = input("Do you want to check another password? (yes/no) ")
    if answer.lower() == "yes":
        continue
    elif answer.lower() == "no":
        print("Thanks, see you!")
        break

########STATYSTYKI

print(f"You have checked {len(score)} password(s).")
if max(score) == 5 and min(score) < 5:
    print("You have checked ", score.count(1) + score.count(2) + score.count(3) + score.count(4), " weak password(s) and ", score.count(5), " strong password(s).")
elif max(score) == 5:
    print(" Cool, ", score.count(5), " strong password(s) have been checked.")
elif min(score) < 5:
    print("You have checked ", score.count(1) + score.count(2) + score.count(3) + score.count(4), "  weak password(s).")
print(score.count(5) / len(score) * 100, "%", " of the passwords are strong.")

for i in range(len(pwds)):
    print(f"Password: {pwds[i]}, Strength: {strength[i]}, Score: {score[i]}")

df = pd.DataFrame({
    "Passwords": pwds,
    "Strength": strength,
    "Score": score
})

print(df)

    
    


