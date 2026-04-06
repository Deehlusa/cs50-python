print ("===== MULTIPLICATION TABLE =====")
number = int(input("Enter the number you want to multiply: "))

for x in range(1, 11, 2):                                                                                                  
    result = number * x
    print ("===== RESULT =====")
    print(f"{number} x {x} = {result}")  