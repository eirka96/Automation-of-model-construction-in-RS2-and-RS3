import pyautogui as pag
import pandas as pd
import numpy as np

from subprocess import Popen
from time import sleep
from os import path
from os import mkdir

import source.filbehandling.make_objects as mo
import source.Automatisering.Auto_handlinger_RS2 as Auto


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# hensikten med denne scripten:
# opprette nye filer, med filnavn gitt av navnekonvensjonen
# ha en løkke som går i gjennom hver fil og klargjør for analyse
# eventuelt lukke alt til slutt

command = ''

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
    sti_koordinater_mus = r"C:\Users\Eirik\OneDrive\Documents\10. Prosjekt og masteroppgave\modellering_svakhetssone\parameterstudie" \
                          r"\excel\Pycharm_automatisering\liste_datamus_koordinater.csv "
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']
    # df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')


    # lage stier til filer og kopiere kildefil, eventuelt slette allerede eksisterende mapper:

    # sti_kildefil:
    # inneholder stien til kildefilen.
    sti_kildefil_rs2 = r"C:\Users\Eirik\OneDrive\Documents\10. Prosjekt og masteroppgave\modellering_svakhetssone\parameterstudie\Mine " \
                       r"modeller\RS2\tverrsnitt_sirkulær\sirkulær_mal\mal_S_bm80_ss1_k1_od500" \
                       r"\S_bm80_ss1_k1_od500_v0_m2_mal.fez "
    # sti_til_mappe_for_lagring_av_stier:
    # er stien til der hvor alle kopier av kildefilene skal lagres i et praktisk
    # mappesystem.
    sti_til_mappe_for_arbeidsfiler = r"C:\Users\Eirik\OneDrive\Documents\10. Prosjekt og " \
                                     r"masteroppgave\modellering_svakhetssone\parameterstudie\Mine " \
                                     r"modeller\RS2\tverrsnitt_sirkulær "
    if not path.exists(mo.alternate_slash([sti_til_mappe_for_arbeidsfiler])[0]):
        mkdir(mo.alternate_slash([sti_til_mappe_for_arbeidsfiler])[0])
    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # er stien til .csv-fil der stier til kopier fra forrige gjennomkjøring er lagret.
    # Denne brukes hvis man ønsker å slette forrige forsøk.
    sti_csv_gamle_rs2stier = r'C:\Users\Eirik\OneDrive\Documents\10. Prosjekt og masteroppgave\modellering_svakhetssone' \
                             r'\parameterstudie\excel\Pycharm_automatisering\liste_stier_rs2filer.csv '
    sti_csv_gamle_csvStier = r"C:\Users\Eirik\OneDrive\Documents\10. Prosjekt og masteroppgave\modellering_svakhetssone" \
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
    mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mappe_for_arbeidsfiler)
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
                mo.delete_and_create_folders(sti_til_mappe_for_arbeidsfiler)
                mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mappe_for_arbeidsfiler)
                # copy_and_store:
                # lager alle kopiene av kildefilene og lagrer filene i rett mappe.
                # Dette gjøres ved å bruke mappenavn og filnavn som markør.
                df_nye_stier_rs2filer, df_nye_stier_csvfiler = mo.copy_and_store(sti_kildefil_rs2,
                                                                                 sti_til_mappe_for_arbeidsfiler)
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
    df_endrede_attributter_rs2filer = mo.get_changing_attributes(sti_til_mappe_for_arbeidsfiler, df_stier_rs2filer,
                                                                 mappenavn_til_rs2)
    time = [0, 0.7, 1, 2, 5]  # tidsintervall, blir viktig for å sørge for at et steg er ferdig før neste begynner.
    # blir nøstet for-løkke her!
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            q = -10
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                path_RS2 = "C:/Program Files/Rocscience/RS2/RS2.exe"
                Popen([path_RS2, path_fil_rs2])
                sleep(10)
                df_koordinater_mus = mo.transform_coordinates_mouse(sti_koordinater_mus, navn_kol_df_koord_mus, q)
                # pyautogui operasjoner begynner her
                i = Auto.klargjore_rs2(df_koordinater_mus, navn_kol_df_koord_mus)
                sleep(2)
                i = Auto.rotere_svakhetssone(df_endrede_attributter_rs2filer, navn_rs2, j, df_koordinater_mus, navn_kol_df_koord_mus, i)
                sleep(2)
                i = Auto.forflytning_svakhetssone(df_endrede_attributter_rs2filer, navn_rs2, j, df_koordinater_mus, navn_kol_df_koord_mus, i)
                sleep(1)
                i = Auto.skalering_svakhetssone(df_koordinater_mus, navn_kol_df_koord_mus, i)
                sleep(3)
                i = Auto.utgraving(df_koordinater_mus, navn_kol_df_koord_mus, i)
                sleep(2)

                # lage diskretisering og mesh
                pag.hotkey('ctrl', 'm', interval=time[1])
                sleep(1)
                # kalkulere
                pag.hotkey('ctrl', 's', interval=time[2])
                pag.hotkey('ctrl', 't', interval=time[1])
                sleep(10)

                # åpne interpret
                pag.hotkey('ctrl', 'shift', 'i', interval=time[4])
                sleep(15)
                # hente ut resultater og lagre i csv
                Auto.interpret_resultat_til_clipboard(time)
                data = pd.read_clipboard()  # henter ut resultat fra interpret RS2, se full beskrivelse i
                # Logg - Mastergradsoppgave_Modellering, 10.08.2021
                data.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=None, index=None) # data lagres i respektiv csv
                # lukke interpret
                pag.hotkey('alt', 'f4', interval=time[3])

                # lukke programmet
                pag.hotkey('ctrl', 's', interval=time[2])
                pag.hotkey('alt', 'f4', interval=time[1])
                q = -10
