import psutil
import pyautogui as pag
import pandas as pd
import numpy as np

from os import path
from os import mkdir
from time import sleep
from subprocess import Popen

import Automatisering_RS2.source.filbehandling.make_objects as mo
import Automatisering_RS2.source.Auto_handlinger_RS2 as Auto

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)

# hensikten med denne scripten:
# opprette nye filer, med filnavn gitt av navnekonvensjonen
# ha en løkke som går i gjennom hver fil og klargjør for analyse
# eventuelt lukke alt til slutt

screenWidth, screenHeight = pag.size()  # the size of main monitor
command = ''

rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes, angel_attributes, \
y_attributes, x_attributes = 80, 1, 1, 500, [3, 5.5, 0.5], 22.5, 0, [5, 8, 1]

ant_parametere_interpret = 2
parameter_navn_interpret = ['sigma 1:', 'total deformasjon:', 'end']
while True:
    try:
        command = input('Kjøre script? j for ja: ')
        if command == 'j':
            break
        elif command == 'n':
            break
        else:
            print('j for ja din nisse!')
    except NameError:
        print('implementert verdi ukjent')
        continue

if command == 'j':
    # hente koordinater fra mus
    sti_koordinater_mus = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie" \
                          r"\excel\Pycharm_automatisering\liste_datamus_koordinater.csv "
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']

    # lage stier til filer og kopiere kildefil, eventuelt slette allerede eksisterende mapper:

    # sti_kildefil:
    # inneholder stien til kildefilen.
    sti_kildefil_rs2, sti_kildefil_csv = mo.get_file_paths_batch()

    # sti_til_mappe_for_lagring_av_stier:
    # er stien til der hvor alle kopier av kildefilene skal lagres i et mappesystem.
    sti_til_mappe_for_arbeidsfiler = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                                     r"\parameterstudie\Mine modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler "
    sti_til_mapper_endelige_filer = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                                     r"\parameterstudie\Mine modeller\RS2\tverrsnitt_sirkulær\sluttprodukt "
    if not path.exists(mo.alternate_slash([sti_til_mappe_for_arbeidsfiler])[0]):
        mkdir(mo.alternate_slash([sti_til_mappe_for_arbeidsfiler])[0])
    if not path.exists(mo.alternate_slash([sti_til_mapper_endelige_filer])[0]):
        mkdir(mo.alternate_slash([sti_til_mapper_endelige_filer])[0])

    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # er stien til .csv-fil der stier til kopier fra forrige gjennomkjøring er lagret.
    # Denne brukes hvis man ønsker å slette forrige forsøk.
    sti_csv_gamle_rs2stier = r'C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone' \
                             r'\parameterstudie\excel\Pycharm_automatisering\liste_stier_rs2filer.csv '
    sti_csv_gamle_csvStier = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                             r"\parameterstudie\excel\modellering_svakhetssone_resultater" \
                             r"\sti_csv_gamle_csvStier.csv "
    # df_gamle_rs2filer/csvfiler:
    # er en dataframe som inneholder stiene lest fra sti_csv_gamle_rs2stier
    df_gamle_stier_rs2filer = pd.read_csv(sti_csv_gamle_rs2stier, sep=';')
    df_gamle_stier_csvfiler = pd.read_csv(sti_csv_gamle_csvStier, sep=';')
    # Tomme elementer får verdien None.
    df_gamle_stier_rs2filer = df_gamle_stier_rs2filer.fillna(np.nan).replace([np.nan], [None])
    df_gamle_stier_csvfiler = df_gamle_stier_csvfiler.fillna(np.nan).replace([np.nan], [None])

    # mappenavn_til_rs2/csv:
    # inneholder navnene til kolonnene i df_gamle/nye_rs2/csvfiler og df_stier_rs2/csvfiler
    mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mapper_endelige_filer)
    # df_stier_rs2filer vil enten inneholde stiene til de gamle eller de nye stiene til rs2filene
    # avhengig av ønske.
    df_stier_rs2filer = df_gamle_stier_rs2filer.copy()
    df_stier_csvfiler = df_gamle_stier_csvfiler.copy()
    while True:
        try:
            command = input('Vil du lage nye rs2-filer? j for ja og n for nei: ')
            if command == 'j':
                # I create_folders:
                # vil mapper fra forrige prosjekt eventuelt bli slettet og mappene
                # til det nye prosjekt blir laget hvis dette er tilfelle
                mo.delete_and_create_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)
                mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mapper_endelige_filer)
                # copy_and_store:
                # lager alle kopiene av kildefilene og lagrer filene i rett mappe.
                # Dette gjøres ved å bruke mappenavn og filnavn som markør.
                df_nye_stier_rs2filer, df_nye_stier_csvfiler = mo.copy_and_store0(sti_kildefil_rs2,
                                                                                  sti_til_mappe_for_arbeidsfiler,
                                                                                  sti_til_mapper_endelige_filer, sti_kildefil_csv)
                # to_csv:
                # Her blir alle stiene til de nylagete rs2-filene lagret.
                df_nye_stier_rs2filer.to_csv(mo.alternate_slash([sti_csv_gamle_rs2stier])[0], sep=';')
                df_nye_stier_csvfiler.to_csv(mo.alternate_slash([sti_csv_gamle_csvStier])[0], sep=';')
                df_stier_rs2filer = df_nye_stier_rs2filer.copy()
                df_stier_csvfiler = df_nye_stier_csvfiler.copy()
                break
            elif command == 'n':
                break
            else:
                print('j for ja din nisse!')
        except NameError:
            print('implementert verdi ukjent')
            continue

    # df_endrede_attributter_rs2filer er en df som inneholder alle de endringer som hver fil skal igjennom.
    # Den har samme struktur som df_stier_rs2filer, men hver celle inneholder en pandas-'Series' der
    # indexene er gitt av hvilken type endring fila skal i gjennom (referert som en bokstav, se
    # r"C:\Users\eirand\OneDrive - Statens vegvesen\Dokumenter\modellering_svakhetssone\parameterstudie\excel\
    # Pycharm_automatisering\parameter_verdier_filnavn.csv " ) og kolonnen er gitt av de tilhørende verdiene som
    # beskriver hvor stor endringen er.
    df_endrede_attributter_rs2filer = mo.get_changing_attributes(df_stier_rs2filer,
                                                                 mappenavn_til_rs2)
    time = [0, 0.7, 1, 2, 5]  # tidsintervall, blir viktig for å sørge for at et steg er ferdig før neste begynner.

    # blir en for-løkke her!
    path_RS2 = "C:/Program Files/Rocscience/RS2/RS2.exe"
    # her lages geometriene til rs2-modellene
    i = 0
    indices_to_check = []
    list_differences = mo.make_container_diff(mappenavn_til_rs2)
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            print(path_fil_rs2)
            print(path_fil_csv)
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                streng_endringer = df_endrede_attributter_rs2filer[navn_rs2][j]
                indices = Auto.alter_model(path_fil_rs2, df_endrede_attributter_rs2filer, mappenavn_til_rs2, i, j)
                indices_to_check.append(indices)
        i += 1
    # # her lages diskretisering og mesh til alle modellene
    # for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
    #     for j in range(df_stier_rs2filer.shape[0]):
    #         path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
    #         path_fil_csv = df_stier_csvfiler[navn_csv][j]
    #         if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
    #             Popen([path_RS2, path_fil_rs2])
    #             sleep(7)
    #             # df_koordinater_mus = mo.transform_coordinates_mouse(sti_koordinater_mus, navn_kol_df_koord_mus, q)
    #             # pyautogui operasjoner begynner her
    #             pag.leftClick(927, 490, interval=time[1])
    #             pag.hotkey('alt', 'f4', interval=time[1])
    #             # lage diskretisering og mesh
    #             pag.hotkey('ctrl', 'm', interval=time[1])
    #             pag.hotkey('ctrl', 's', interval=time[1])
    #             pag.hotkey('alt', 'f4', interval=time[1])
    # # while True:
    # #     try:
    # #         command = input('fortsette script? j for ja: ')
    # #         if command == 'j':
    # #             break
    # #         elif command == 'n':
    # #             break
    # #         else:
    # #             print('j for ja din nisse!')
    # #     except NameError:
    # #         print('implementert verdi ukjent')
    # #         continue
    #
    # # her kjøres alle kalkulasjonene, med en dynamisk while-løkke slik at når alle kalkulasjonene er ferdig, så fortsetter scriptet
    # path_RS2_Compute = r"C:\Program Files\Rocscience\RS2\feawin.exe "
    # Popen([path_RS2_Compute])
    # sleep(5)
    # Auto.handlinger_kalkulasjon()
    # # lukke RS2 Compute
    # pag.hotkey('alt', 'f4', interval=time[2])
    #
    #
    # # åpner interpret, der alle resultater som skal benyttes hentes ut og lagres i csv-format
    # path_RS2_interpret = r"C:\Program Files\Rocscience\RS2\Interpret.exe "
    # i = 0
    # k = 0
    # for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
    #     for j in range(df_stier_rs2filer.shape[0]):
    #         path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
    #         path_fil_csv = df_stier_csvfiler[navn_csv][j]
    #         if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
    #             Popen([path_RS2_interpret, path_fil_rs2])
    #             sleep(7)
    #             i = Auto.store_results_csv_prep(df_koordinater_mus, navn_kol_df_koord_mus, i)
    #             pag.hotkey('f6', interval=time[2])
    #             for k in range(ant_parametere_interpret):
    #                 navn_parameter = parameter_navn_interpret[k]
    #                 i = Auto.store_results_in_csv(df_koordinater_mus, navn_kol_df_koord_mus, path_fil_csv,
    #                                               navn_parameter, i)
    #             #markere slutten på fila
    #             sr = pd.DataFrame(['end'])
    #             sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
    #             # lukke interpret
    #             pag.hotkey('alt', 'f4', interval=time[3])
    #             pag.press('enter', interval=time[2])
    #             # # lukke programmet
    #             # pag.hotkey('ctrl', 's', interval=time[1])
    #             # pag.hotkey('alt', 'f4', interval=time[1])
    #             i = 0
    #     k += 1
    #
    # # her kalkuleres differensene til de mest sentrale punktene som skal presenteres ved bruk av matplotlib
    # k = 0
    # for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
    #     for j in range(df_stier_rs2filer.shape[0]):
    #         path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
    #         path_fil_csv = df_stier_csvfiler[navn_csv][j]
    #         if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
    #             indices = indices_to_check[j]
    #             parameter_navn_interpret0 = mo.prep_parameter_navn(parameter_navn_interpret)
    #             to_plot = mo.get_parameter_to_plot(path_fil_csv, parameter_navn_interpret0)
    #             differences = mo.get_difference(to_plot, indices)
    #             if differences is not None:
    #                 list_differences[k].append(differences)
    #             # mo.plot_data(to_plot, parameter_navn_interpret)
    #     paths_fil_rs2 = df_stier_rs2filer[navn_rs2]
    #     mo.create_difference_csv(navn_csv, list_differences[k], parameter_navn_interpret, paths_fil_rs2,
    #                              sti_til_mappe_for_arbeidsfiler)
    #     k += 1
