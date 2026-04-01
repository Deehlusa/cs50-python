answer = input("What is the Answer to the Great Question of Life, the Universe, and Everything? ").strip().lower()

# Refactoring: Isolamento das condições aceites num array/list
if answer in ["42", "forty-two", "forty two"]:
    print("Yes")
else:
    print("No")