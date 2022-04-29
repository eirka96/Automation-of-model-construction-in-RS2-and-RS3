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
from Automatisering_RS2.source.alter_geometry import geometry_operations as go
import plan_experiment as pe
import experiment_actions as ea

"""

hensikten med denne scripten:
opprette nye filer, med filnavn gitt av navnekonvensjonen
ha en løkke som går i gjennom hver fil og klargjør for analyse
eventuelt lukke alt til slutt

"""

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
    """
    First, some rules for printing of dataframes in the pandas library is defined, to make the workflow with them 
    easier.
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', -1)
    """
    Hvis det er nødvendig å finne monitorens størrelse, så uncomment det under.
    """
    # screenWidth, screenHeight = pag.size()  # the size of main monitor
    # print("the size of the main monitor is [" + str(screenWidth) + ", " + str(screenHeight" + "].")
    """
    the plan_experiment module (shortened: pe) sets the attributes that will be varied in the experiment. All parameters
    is set in the variables bellow and is later read when the geometry and material is defined.
    """
    # definerer hvilke attributter som endres
    ant_parametere_interpret = 2
    parameter_navn_interpret = ['sigma 1:', 'total deformasjon:', 'end']
    fysiske_enheter = ['[MPa]', '[m]']
    # definerer parameterenes størrelser
    rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes, angel_attributes, \
    y_attributes, x_attributes = 80, 1, 1, 500, [0.5, 5.5, 0.5], 22.5, 0, [-7, 8, 1]
    # definerer en liste over alle attributter (attributes_list, samt en liste over de attributter som skal varieres
    # (list_of_lists_attributes). Brukes i plotte_funksjonene.
    attributes_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes,
                       angel_attributes, y_attributes, x_attributes]
    list_of_lists_attributes, attribute_type = mo.return_lists(attributes_list)
    # path til csv for lagring av konstrerte filnavn som er tuftet på parameterverdiene over og har struktur:
    # S_bm80_ss1_k1_od500_m4_v22.5_x0_y0.
    # S: sirkulær kontur,
    # bm er bergmassekvaliteten i omkringliggende berg,
    # ss er materialkvaliteten på sone,
    # k er forholdet mellom vertikal og horisontalspenning der spenningen er homogen i horisontalplanet,
    # od er overdekningen,
    # m er mektigheten,
    # v er vinkelen til sonen,
    # x er den horisontale forflytning av sonen,
    # y er den vertikale forflytning av sonen.
    # Denne strukturen er sentral for hvordan scriptet kan forstå hvilke endringer som skal gjøres og letter dessuten
    # arbeidet med å identifisere en spesifikk modell.
    path_csv_parameter_verdier = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave" \
                                 r"\modellering_svakhetssone\parameterstudie\excel\Pycharm_automatisering" \
                                 r"\parameter_verdier_filnavn.csv "
    # set_model_csv_attributes_batch så blir filnavnene skapt på bakgrunn av parameterverdiene lagret i en stor batch.
    # Denne setter føringen for hele scriptets struktur, som er avhengig av at alle filnavnene er plassert på samme sted
    pe.set_model_csv_attributes_batch(path_csv_parameter_verdier, rock_mass_material, weakness_zone_material,
                                      stress_ratio, overburden, mektighet_attributes, angel_attributes,
                                      y_attributes, x_attributes)
    # set_model_csv_attributes er mindre sentral, men kan benyttes for å systematisere de ulike filer med hensyn på
    # overdekning i et senere stadium for mer oversiktelig lagring av resultater.
    paths_csv = pe.make_csv_paths([25, 100, 200, 300, 500, 800, 1000])
    pe.delete_content_csv(paths_csv)
    pe.set_model_csv_attributes(paths_csv, rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                                mektighet_attributes, angel_attributes, y_attributes, x_attributes)

    """
    I dette segmentet blir andre viktige variable definert. Stier for ulike programmer som skal benyttes, allerede
    eksisterende data blir hentet fra ulike filplasseringer og plassert som regel i en dataframe, struktur
    for ulike dataframes defineres.
     """

    # stier, programmer som kalles på:
    path_rs2 = "C:/Program Files/Rocscience/RS2/RS2.exe"
    path_rs2_compute = r"C:\Program Files\Rocscience\RS2\feawin.exe "
    path_rs2_interpret = r"C:\Program Files\Rocscience\RS2\Interpret.exe "

    # hente koordinater fra mus
    sti_koordinater_mus = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                          r"\parameterstudie\excel\Pycharm_automatisering\liste_datamus_koordinater.csv "
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']

    # lage stier til filer og kopiere kildefil, eventuelt slette allerede eksisterende mapper:

    # sti_kildefil:
    # inneholder stien til kildefilen.
    paths_shale_rs2 = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                      r"\parameterstudie\Mine modeller\RS2\tverrsnitt_sirkulær\sirkulær_mal\mal_S_bm80_ss1_k1_od{}" \
                      r"\S_bm80_ss1_k1_od{}_v0_m2_mal\S_bm80_ss1_k1_od{}_v0_m2_mal.fea "
    sti_kildefil_rs2, sti_kildefil_csv = mo.get_file_paths_batch(paths_shale_rs2, path_csv_parameter_verdier)

    # sti_til_mappe_for_lagring_av_stier:
    # er stien til der hvor alle kopier av kildefilene skal lagres i et mappesystem.
    sti_til_mappe_for_arbeidsfiler = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave" \
                                     r"\modellering_svakhetssone\parameterstudie\Mine modeller\RS2" \
                                     r"\tverrsnitt_sirkulær\arbeidsfiler "
    sti_til_mapper_endelige_filer = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave" \
                                    r"\modellering_svakhetssone\parameterstudie\Mine modeller\RS2" \
                                    r"\tverrsnitt_sirkulær\sluttprodukt "
    # create_work_and_storage_folders
    mo.create_work_and_storage_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)

    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # er stien til .csv-fil der stier til kopier fra forrige gjennomkjøring er lagret.
    # Denne brukes hvis man ønsker å slette forrige forsøk.
    sti_csv_gamle_rs2stier = r'C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone' \
                             r'\parameterstudie\excel\Pycharm_automatisering\liste_stier_rs2filer.csv '
    sti_csv_gamle_csvstier = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                             r"\parameterstudie\excel\modellering_svakhetssone_resultater" \
                             r"\sti_csv_gamle_csvStier.csv "
    # get_old_paths_df henter stier fra alleredeeksisterende eksperiment og lagrer disse i dataframe-format
    df_stier_rs2filer, df_stier_csvfiler = mo.get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)
    # mappenavn_til_rs2/csv:
    # inneholder navnene til kolonnene i df_stier_rs2/csvfiler
    mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mapper_endelige_filer)

    # her stilles spm om det vil startes et nytt eksperiment, hvis ja så blir det dannet nye filer og de gamle forkastes
    change = mo.get_new_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2,
                                 sti_kildefil_csv, sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)
    # if change[0]:
    #     df_stier_rs2filer, df_stier_csvfiler = change[1], change[2]

    # df_endrede_attributter_rs2filer er en df som inneholder alle de endringer som hver fil skal igjennom.
    # Den har samme struktur som df_stier_rs2filer, men hver celle inneholder en pandas-'Series' der
    # indexene er gitt av hvilken type endring fila skal i gjennom (referert som en bokstav, se
    # r"C:\Users\eirand\OneDrive - Statens vegvesen\Dokumenter\modellering_svakhetssone\parameterstudie\excel\
    # Pycharm_automatisering\parameter_verdier_filnavn.csv " ) og kolonnen er gitt av de tilhørende verdiene som
    # beskriver hvor stor endringen er.
    df_endrede_attributter_rs2filer = mo.get_changing_attributes(df_stier_rs2filer, mappenavn_til_rs2)
    # time, benyttes under autogui-prosessene for å definere hvor lang tid pcen har for å utføre en komando.
    # Blir viktig for å sørge for at et steg er ferdig før neste begynner. Hvis det skjer så crasher srciptet. Valg av
    # intervall blir funnet på bakgrunn av testing.
    time = [0, 0.7, 1, 2, 5]

    "her lages geometriene til rs2-modellene, evt så hentes de sentrale punktene ut"
    # points_to_check = ea.execute_model_alteration(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
    #                                               df_stier_csvfiler, df_endrede_attributter_rs2filer)
    points_to_check = go.get_parameters(df_stier_rs2filer, mappenavn_til_rs2, mappenavn_til_csv)

    """her lages diskretisering og mesh til alle modellene"""
    ea.create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time)

    """
    her kjøres alle kalkulasjonene, med en dynamisk while-løkke slik at når alle kalkulasjonene er ferdig, 
    så fortsetter scriptet. Det er viktig å sørge for at rs2_compute allerede finner den mappen som filene ligger i.
    """
    ea.calculate(path_rs2_compute, time)

    """åpner interpret, der alle resultater som skal benyttes hentes ut og lagres i csv-format"""
    ea.store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
                  df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time)
    #
    # """her kalkuleres differensene til de mest sentrale punktene som skal presenteres ved bruk av matplotlib"""
    # list_paths_differences, list_diff_navn, list_paths_values, list_val_navn = \
    #     ea.execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
    #                                df_stier_csvfiler, points_to_check, sti_til_mappe_for_arbeidsfiler,
    #                                sti_til_mapper_endelige_filer)
    #
    # """her plottes det som skal plottes"""
    # ea.execute_plots(list_paths_differences, list_diff_navn, list_paths_values, list_val_navn,
    #                  mappenavn_til_rs2, mappenavn_til_csv, parameter_navn_interpret, df_stier_csvfiler,
    #                  list_of_lists_attributes, attribute_type, fysiske_enheter)

