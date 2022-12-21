def export(df, name):
    yn = input("\nDo you want to save this data?\n")
    if yn == "yes" or yn == "y" or yn == "Yes" or yn == "Y" or yn == 'yuh':
        df.to_csv('data/CSVs/' + name + '.csv', index = False)
        print("Data saved to file \"" + name + ".csv\"")
        return
    if yn == "no" or yn == "n" or yn == "No" or yn == "N":
        return
    else:
        print("Huh?\n")
        export(df, name)
