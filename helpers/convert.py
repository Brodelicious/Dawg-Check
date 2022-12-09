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

def convert_sports_reference_dates(date):
    date = date.replace(',','')
    date_vars = date.split(' ')
    if date_vars[1] == 'Jan':
        date_vars[1] = '2'
    elif date_vars[1] == 'Feb':
        date_vars[1] = '3'
    elif date_vars[1] == 'Mar':
        date_vars[1] = '4'
    elif date_vars[1] == 'Apr':
        date_vars[1] = '5'
    elif date_vars[1] == 'May':
        date_vars[1] = '6'
    elif date_vars[1] == 'Jun':
        date_vars[1] = '7'
    elif date_vars[1] == 'Jul':
        date_vars[1] = '8'
    elif date_vars[1] == 'Aug':
        date_vars[1] = '8'
    elif date_vars[1] == 'Sep':
        date_vars[1] = '9'
    elif date_vars[1] == 'Oct':
        date_vars[1] = '10'
    elif date_vars[1] == 'Nov':
        date_vars[1] = '11'
    elif date_vars[1] == 'Dec':
        date_vars[1] = '12'
    else:
        print("Month not recognized")
    date = date_vars[3] + '-' + date_vars[1] + '-' + date_vars[2]
    print(date)
    return date

