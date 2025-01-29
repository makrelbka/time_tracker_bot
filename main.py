# import aiogram 
import time

def print_stat(arr):
    arr = sorted(arr.items(), key=lambda item: item[1], reverse=True)
    print("stat:")
    for i in arr:
        print(i[0]," : ","{:.2f}".format(i[1]/60))

arr = {}
current = []
while True:
    a = input()
    
    if current != []:
        if current[0] in arr:
            arr[current[0]] += time.time() - current[1]
        else:
            arr[current[0]] = time.time() - current[1]
    current = [a, time.time()]
    if a == "stop":
        print_stat(arr)

        








