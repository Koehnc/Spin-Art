import random

def sim(numPeople):
    people = list(range(numPeople))
    picker = 0
    while len(people) > 0 and picker < numPeople:
        choice = random.choice(people)
        people.remove(choice)
        if choice == picker:
            return True
        picker += 1
    
    return False

numSims = 1000000
for j in range(0,20):
    counter = 0
    for i in range(numSims):
        if sim(j):
            counter += 1
    print("Num People: ", j, "chance: ", float(counter) / numSims)

print(float(counter) / numSims)
input("Press anything to close the tab...")

