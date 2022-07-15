import pyautogui as pag
import pandas as pd

"""
This script tracks mouse coordinates, adds metadata to the coordinate, and stores it to a csv-file

"""


def mouse_tracker(path, bool_shall_reedit_mouse_coordinates):
    navn_kolonne = ['Handling', 'x', 'y']
    command = 'n'  # spore musas koordinater
    while bool_shall_reedit_mouse_coordinates:
        try:
            command = input("Vil du spore musas koordinater? j for ja og n for nei: ")
            if command == 'j':
                while True:
                    try:
                        command = input('Plasser mus over ønsket felt og press j: ')
                        if command == 'j':
                            break
                        else:
                            print('j for ja og n for nei, prøv igjen!')
                    except NameError:
                        print("Oppstod en feil!")
                        continue
                break
            elif command == 'n':
                break
            else:
                print('j for ja og n for nei, prøv igjen!')
        except NameError:
            print("Oppstod en feil!")
            continue

    if command == 'n':
        print('Ingen posisjon ble lagret!')
    else:
        teller = 0
        liste = [[], [], [], []]
        while command == 'j':

            x, y = pag.position()
            liste[0].append(input('Gi beskrivelse av handling: '))
            liste[1].append(x)
            liste[2].append(y)

            while True:
                try:
                    command2 = input('Ønsker du å slette lagret punkt? j for ja og n for nei: ')
                    if command2 == 'j':
                        del liste[0][-1]
                        del liste[1][-1]
                        del liste[2][-1]
                        break
                    elif command2 == 'n':
                        teller += 1
                        break
                    else:
                        print('j for ja og n for nei fjompenisse!')
                except NameError:
                    print('Det er et eller anna som har gått gæli!')

            while True:
                try:
                    command = input('Plasser mus over ønsket posisjon og press j for å lagre, eller n for å avslutte: ')
                    if command == 'j':
                        break
                    elif command == 'n':
                        break
                    else:
                        print('j for ja og n for nei, prøv igjen!')
                except NameError:
                    print("Oppstod en feil!")
                    continue

        data = {navn_kolonne[0]: liste[0], navn_kolonne[1]: liste[1], navn_kolonne[2]: liste[2]}
        df = pd.DataFrame(data)
        df.to_csv(path, mode='a', sep=';', index=False, header=False)
    return


