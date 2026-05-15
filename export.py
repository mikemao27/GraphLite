def main():
    coins = [25, 10, 5]
    cost = 50
    while cost > 0:
        print(f"Amount Due: {cost}")
        change = input("Insert Coin: ")
        change = int(change)
        if change in coins:
            cost -= change

    if cost < 0:
        cost = cost * (-1)
    print(f"Change Owed: {cost}")
    
main()