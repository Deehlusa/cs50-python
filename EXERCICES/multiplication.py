"This program generates a multiplication table for a given number, multiplying it by odd numbers from 1 to 10.
Logic:
    1. Input handling with explicit type casting (int).
    2. Looping through a range of odd numbers (1 to 10).
    3. Performing multiplication and displaying results in a structured format.
Author: André Rodrigues (QA Automation Student)
Example:
    Input: 5
    Output:
    ===== MULTIPLICATION TABLE ====="

print ("===== MULTIPLICATION TABLE =====")
number = int(input("Enter the number you want to multiply: "))

for x in range(1, 11, 2):                                                                                                  
    result = number * x
    print ("===== RESULT =====")
    print(f"{number} x {x} = {result}")  