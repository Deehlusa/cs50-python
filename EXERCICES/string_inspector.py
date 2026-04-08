"""
Module: string_inspector.py
Objective: Perform a full diagnostic on user input.
Author: André Rodrigues (QA Automation Student)
Logic:
    1. Input handling (string).
    2. Use of string methods to analyze the input.
    3. Output of results in a structured format. 
example:
    Input: "Hello World 123"
    Output:
    ------------------------------
    VALOR ANALISADO: 'Hello World 123'
    TIPO: <class 'str'>
    ------------------------------
    É apenas letras?       False
    É apenas números?      False
    Está tudo em minúsculo? False
    Está tudo em maiúsculo? False
    É alfanumérico?        False
    É apenas espaço?       False
    É imprimível?          True
    É alfanumérico ou espaço? False
    É um título?           True
    É decimal?             False
    É numérico?            False
    É um identificador válido? False
    É casefold?           False
    É ASCII?              True
    É decimal ou espaço?   False
    É numérico ou espaço?  False        
"""

n = input("Digite alguma coisa: ")

# Realizamos os testes individualmente para não anular o resultado
is_alpha   = n.isalpha() # Verificando se o valor é composto apenas por letras (True) ou não (False)
is_digit   = n.isdigit() # Verificando se o valor é composto apenas por dígitos (True) ou não (False)
is_lower   = n.islower() # Verificando se o valor está todo em minúsculo (True) ou não (False)
is_upper   = n.isupper() # Verificando se o valor está todo em maiúsculo (True) ou não (False)
is_alnum   = n.isalnum() # Verificando se o valor é alfanumérico (True) ou não (False)
is_space   = n.isspace() # Verificando se o valor é apenas espaço (True) ou não (False)
is_printable= n.isprintable() # Verificando se o valor é imprimível (True) ou não (False)
is_alnum_or_space = n.replace(" ", "").isalnum() # Verificando se o valor é alfanumérico ou espaço (True) ou não (False)
is_title   = n.istitle() # Verificando se o valor é um título (True) ou não (False)
is_decimal = n.isdecimal() # Verificando se o valor é decimal (True) ou não (False)
is_numeric = n.isnumeric() # Verificando se o valor é numérico (True) ou não (False)
is_identifier = n.isidentifier() # Verificando se o valor é um identificador válido (True) ou não (False)
is_ascii = n.isascii() # Verificando se o valor é ASCII (True) ou não (False)
is_decimal_or_space = n.replace(" ", "").isdecimal() # Verificando se o valor é decimal ou espaço (True) ou não (False)
is_numeric_or_space = n.replace(" ", "").isnumeric() # Verificando se o valor é numérico ou espaço (True) ou não (False)

print("-" * 30)
print(f"VALOR ANALISADO: '{n}'")
print(f"TIPO: {type(n)}")
print("-" * 30)

# Relatório de Inspeção (Onde vês a verdade de cada sensor)
print(f"É apenas letras?       {is_alpha}") # Verificando se o valor é composto apenas por letras (True) ou não (False)
print(f"É apenas números?      {is_digit}") # Verificando se o valor é composto apenas por dígitos (True) ou não (False)
print(f"Está tudo em minúsculo? {is_lower}") # Verificando se o valor está todo em minúsculo (True) ou não (False)
print(f"Está tudo em maiúsculo? {is_upper}") # Verificando se o valor está todo em maiúsculo (True) ou não (False)
print(f"É alfanumérico?        {is_alnum}") # Verificando se o valor é alfanumérico (True) ou não (False)
print(f"É apenas espaço?       {is_space}") # Verificando se o valor é apenas espaço (True) ou não (False)
print(f"É imprimível?          {is_printable}") # Verificando se o valor é imprimível (True) ou não (False)
print(f"É alfanumérico ou espaço? {is_alnum_or_space}") # Verificando se o valor é alfanumérico ou espaço (True) ou não (False)
print(f"É um título?           {is_title}") # Verificando se o valor é um título (True) ou não (False)
print(f"É decimal?             {is_decimal}") # Verificando se o valor é decimal (True) ou não (False)
print(f"É numérico?            {is_numeric}") # Verificando se o valor é numérico (True) ou não (False)
print(f"É um identificador válido? {is_identifier}") # Verificando se o valor é um identificador válido (True) ou não (False)
print(f"É ASCII?              {is_ascii}") # Verificando se o valor é ASCII (True) ou não (False)
print(f"É decimal ou espaço?   {is_decimal_or_space}") # Verificando se o valor é decimal ou espaço (True) ou não (False)
print(f"É numérico ou espaço?  {is_numeric_or_space}") # Verificando se o valor é numérico ou espaço (True) ou não (False)
print("-" * 30) 
print("Fim do diagnóstico.")