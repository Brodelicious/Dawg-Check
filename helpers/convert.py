def convert_american(odds):
    if (odds[0:1] == '+' or '-') and (odds[-2:-1] != "%"):
        sign = odds[0:1]
        number = odds[1:len(odds)]
        if sign == '-':
            return str(int(number) / (int(number) + 100) * 100) + '%'
        if sign == '+':
            return str(100 / (int(number) + 100)) + '%'

    if (odds[-1:-2] == "%") and (odds[0:1] != '+' or '-'):
        number = odds[0:len(odds-1)]
        return

    else:
        print("invalid input")
        return
