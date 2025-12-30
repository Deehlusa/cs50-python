# import library python
import datetime
import random
# variáveis usadas (now, now_format, name_user, age, id_log, agelog)
now = datetime.datetime.now()
now_format = now.strftime("%d/%m/%Y %H:%M:%S")
name_user = input("What's your name?")
# condicional (while true, try, if, except)
while True:
    age = input("How old are you? ")

    try:
        age = int(age)
        if (age <= 0) or (age >= 120):
            print("Insert a valid age (1 to 119).")
            continue
        break
    
    except ValueError:
        print("Please enter a valid number format.")


id_log = random.randrange(1, 9999) # variavel id_log gera o número
id_log = str(id_log).zfill(4) # garante que os números gerados serão sempre 4 digitos
# terminal interage e mostra resultados através do print f
print(f"ID{id_log}")
print(f"You are {age} years old")
print(f"Your name: {name_user}.")
print(f"--- LOG DE SISTEMA: {now_format} ---")
# file chamado age_log.txt no formado "a" que vai sempre acrescentando novas informações ao file de texto
with open("age_log.txt", "a", encoding="utf-8") as agelog:
    agelog.write (f"[{id_log}]:\n")
    agelog.write(f"Age: {age} \n Name of User: {name_user}\n Date: {now_format}\n")
    agelog.write(f"-------------------------\n")