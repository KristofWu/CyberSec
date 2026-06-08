print("Wlecome!")

name=input("What is your name? ")
print("Hi " + name + "!")

if name == "Ben":
  mad_status=(input("Are you mad?? "))
  if mad_status == "yes":
    print("Get out!")
    exit()
  else: 
    print("Welcome")
elif name == "Bob":
  magic_status=(input("Are you magic? "))
  if magic_status == "yes":
    print("Get out!")
    exit()
  if magic_status == "not really":
    print("you have a 50% dicount")
  else:
   print("Welcome")  
else:
  print("You are more than welcome")