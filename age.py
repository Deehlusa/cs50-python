import datetime
import random


now = datetime.datetime.now()
now_format = now.strftime("%d/%m/%Y %H:%M:%S")

name_user = input("What's your name?")
while True:
    age = input("How old are you? ")
    try:
        age = int(age)
        break
    except ValueError:
        print("Please enter a valid number fomat.")

id_log = random.randrange(1, 9999) # variavel id_log gera o número
id_log = str(id_log).zfill(4) # garante que os números gerados serão sempre 4 digitos

print(f"ID{id_log}")
print(f"You are {age} years old")
print(f"Your name: {name_user}.")

print(f"--- LOG DE SISTEMA: {now_format} ---")
with open("age_log.txt", "a", encoding="utf-8") as agelog:
    agelog.write (f"[{id_log}]:\n")
    agelog.write(f"[Age: {age}] \n Name of User: {name_user}\n Date: {now_format}\n")
    