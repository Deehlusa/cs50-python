"""
Module: string_inspector.py
Objective: Perform a full diagnostic on user input.
"""

n = input("Digite alguma coisa: ")

# Realizamos os testes individualmente para não anular o resultado
is_alpha   = n.isalpha()
is_digit   = n.isdigit()
is_lower   = n.islower()
is_upper   = n.isupper()
is_alnum   = n.isalnum()
is_space   = n.isspace()

print("-" * 30)
print(f"VALOR ANALISADO: '{n}'")
print(f"TIPO: {type(n)}")
print("-" * 30)

# Relatório de Inspeção (Onde vês a verdade de cada sensor)
print(f"É apenas letras?       {is_alpha}")
print(f"É apenas números?      {is_digit}")
print(f"Está tudo em minúsculo? {is_lower}")
print(f"Está tudo em maiúsculo? {is_upper}")
print(f"É alfanumérico?        {is_alnum}")
print(f"É apenas espaço?       {is_space}")