import pyautogui as pag
import pandas as pd

# Må sørge for at excel arke er klargjort på forhånd med følgende attributter:
# 1. exceldokumentet må ha navn likt variabel tekst
# 2. excelark må ha navn koordinater
# 3. kolonne A1, B1, C1 og D1 må ha navn hhv. gitt av navn_kolonne
# 4. Siden dataframes rader er gitt av vanlig indexering lagres denne ikke

# Må sørge for at det alltid gjøres et click i det vinduet man ønsker å gjøre operasjoner som er knyttet til
# hurtigtaster

tekst = r'C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\excel' \
        r'\Pycharm_automatisering\liste_datamus_koordinater.csv '
navn_kolonne = ['Handling', 'x', 'y']

command = ' '  # tømme
command1 = ''  # spore musas koordinater
command2 = ''  # slette koordinat som ble lagt inn ved feil

# while True:
#     try:
#         command = input('Vil du tømme alle lagrede koordinater tilhørende musa? j for ja og n for nei: ')
#         if command == 'j':
#             os.remove(tekst)  #slette eksistrende fil
#             wb = op.Workbook()  # lage workbook
#             ws = wb.active  # gi navn til excelark
#             ws.title = 'koordinater'
#             ws['A1'] = navn_kolonne[0]
#             ws['B1'] = navn_kolonne[1]
#             ws['C1'] = navn_kolonne[2]
#             wb.save(tekst)  # oppretter excel fil
#
#             break
#         elif command == 'n':
#             break
#         else:
#             print('Du må enten svare j (ja) eller n (nei) ditt nek!')
#     except NameError:
#         print("Uffda, har hare oppstått'n feil!")
#         continue


while True:
    try:
        command1 = input("Vil du spore musas koordinater? j for ja og n for nei: ")
        if command1 == 'j':
            while True:
                try:
                    command1 = input('Plasser mus over ønsket felt og press j: ')
                    if command1 == 'j':
                        break
                    else:
                        print('j for ja og n for nei, prøv igjen!')
                except NameError:
                    print("Oppstod en feil!")
                    continue
            break
        elif command1 == 'n':
            break
        else:
            print('j for ja og n for nei, prøv igjen!')
    except NameError:
        print("Oppstod en feil!")
        continue

if command1 == 'n':
    print('Ingen posisjon ble lagret!')

else:
    teller = 0
    liste = [[], [], [], []]
    while command1 == 'j':

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
        # if command2 == 'n':
        #     while True:
        #         try:
        #             p = input('Benyttes tastatur? 1 for ja og 0 for nei: ')
        #             if p == '1':
        #                 liste[3].append(p)
        #                 break
        #             elif p == '0':
        #                 liste[3].append(p)
        #                 break
        #             else:
        #                 print('1 for ja og 0 for nei!')
        #         except NameError:
        #             print("Oppstod en feil!")
        #             continue

        while True:
            try:
                command1 = input('Plasser mus over ønsket posisjon og press j for å lagre, eller n for å avslutte: ')
                if command1 == 'j':
                    break
                elif command1 == 'n':
                    break
                else:
                    print('j for ja og n for nei, prøv igjen!')
            except NameError:
                print("Oppstod en feil!")
                continue

    data = {navn_kolonne[0]: liste[0], navn_kolonne[1]: liste[1], navn_kolonne[2]: liste[2]}
    df = pd.DataFrame(data)
    # append_df_to_excel(tekst, df, sheet_name='koordinater', header=None, index=False)
    df.to_csv(tekst, mode='a', sep=';', index=False, header=False)
    # if command == 'j':
    #     df_col = pd.DataFrame({'col': navn_kolonne})
    #     append_df_to_excel(tekst, df_col, sheet_name='navn_kolonne', index=False)


# if input('måle posisjon nå?') == 'j':
#     x, y = pag.position()
#     print(x, y)


