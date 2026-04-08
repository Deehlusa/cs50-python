""""
Module: sum.py
Description: Simple arithmetic script to perform addition between two integers.
Author: André Rodrigues (QA Automation Student)
Logic: 
    1. Input handling with explicit type casting (int).
    2. Arithmetic operation (addition).
    3. String interpolation using the .format() method.
"""
n1 = int(input("Digite um valor: "))
n2 = int(input("Digite outro valor: "))

result = n1 + n2

#print("A soma entre:", n1, "+", n2, "=" ,result)
# using method .format to exibition result
print(f"A soma entre {n1} + {n2} = {result}")


