def track_menu():

    pista = 0
    print("Which track do you want to use?")
    print("1- Circular Track")
    print("2- Oval Track")
    print("3- First Track")

    while pista > 4 or pista < 1 or isinstance(pista, str):
        pista = int(input("desired track: "))


    return pista
    
