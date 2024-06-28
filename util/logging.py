def log(message: any, *args) -> None:
    if len(args) == 0:
        print(message)
    else:
        print(message, *args)

