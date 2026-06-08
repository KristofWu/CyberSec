import random

def game():
    random_number = random.randint(1, 10)
    guesses = 0

    while True:
        guess = int(input("Guess a number between 1 and 10: "))
        guesses += 1
        if guess < random_number:
            print("Too low! Try again.")
        elif guess > random_number:
            print("Too high! Try again.")
        else:
            print("Congratulations! You guessed the number!")
            print(f"You have made {guesses} guesses.")
            return guesses

score = []
while True: 
    account = game()
    score.append(account)
    play_game = input("Do you want to play the guessing game? (yes/no) ")

    if play_game.lower() == "yes":
        game()
    elif play_game.lower() == "no": 
        print("Thanks, see you!")
        print(f"Your score: {score}.")
        if len(score) > 0:
            print(f"Your best score is: {min(score)} guesses.")
        if min(score) == 1:
            print("Wow, you are a genius!")
        if max(score) > 5:
            print("You need to practice more!")
        if sum(score) / len(score) < 3:
            print("Great job! You are improving!")
        exit()



    