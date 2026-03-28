# Captura e normalização (Mantendo como String para aceitar texto e números)
answer = input("What is the Answer to the Great Question of Life, the Universe, and Everything? ").strip().lower()

# Verificação de múltiplas condições
if answer == "42" or answer == "forty-two" or answer == "forty two":
    print("Yes")
else:
    print("No")

