  #Pedir ao utilizador para escrever um cumprimento (greeting). Depois, verificas o que ele#   
  #escreveu e devolves dinheiro:#

greeting = input("Say something: \n").lower()

if greeting.startswith("hello"): #se variavel greeting input do users for "hello" imprime 0
    print("0$")
elif greeting.startswith("h"): #se não for "hello" for "h" também imprime 0
    print("0$")
elif greeting.startswith("goodbye"): # se não for nenhuma das anteriores e gor "goodbye" imprime 20$
    print("20$")
else:      # se não for nenhuma das condições acima imprime 0 na mesma
    print("0$")                                  

