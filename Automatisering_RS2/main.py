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
    y_attributes, x_attributes = 80, 1, 1, 500, 3, 22.5, 0, [0, 2, 1]
    overdekninger = [25, 100, 200, 300, 500, 800, 1000]
    # definerer en liste over alle attributter (attributes_list, samt en liste over de attributter som skal varieres
    # (list_of_lists_attributes). Brukes i plotte_funksjonene.
    attributes_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes,
                       angel_attributes, y_attributes, x_attributes]
    list_of_lists_attributes, attribute_type = mo.return_lists(attributes_list)

    color_map = {
        'm': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'fuchsia'],
        'x': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'xkcd:yellowish', 'green',
              'xkcd:lime', 'blue', 'cyan', 'purple', 'fuchsia', 'xkcd:lavender', 'xkcd:bronze']
    }
    list_colormaps = []
    list_colormaps += 7 * [color_map]
    list_which_material = [[[[15, 15], [15, 15], [16, 16], [16, 0]], [[15, 15], [15, 15], [16, 16], [15, 0]]],
                           [[15, 15], [15, 15], [16, 0], [15, 0], [16, 16]],
                           [[15, 15], [15, 15], [15, 0], [15, 0], [16, 16], [16, 16], [16, 0]]]

    valnavn = ['file_name', 'quad_high - sigma1, low', 'quad_high - sigma1, high', 'quad_high - sigma 1, inbetween',
               'quad_high - totaldeformasjon, low', 'quad_high - totaldeformasjon, high',
               'quad_high - totaldeformasjon, inbetween',
               'quad_low - sigma1, low', 'quad_low - sigma1, high', 'quad_low - sigma 1, inbetween',
               'quad_low - totaldeformasjon, low', 'quad_low - totaldeformasjon, high',
               'quad_low - totaldeformasjon, inbetween']
    list_valnavn = []
    list_valnavn += 7 * [valnavn]
    main_stringobjects = pd.read_csv(r'C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave'
                                     r'\modellering_svakhetssone\parameterstudie\excel\Pycharm_automatisering'
                                     r'\liste_stringObjects_main_vivoBook.csv ', sep=';')
    # list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc, \
    # list_points_to_check = [], [], [], [], []
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
    path_csv_parameter_verdier = main_stringobjects['object'][0]
    paths_shell_rs2 = main_stringobjects['object'][1]
    paths_shell_csv = main_stringobjects['object'][2]
    # set_model_csv_attributes_batch så blir filnavnene skapt på bakgrunn av parameterverdiene lagret i en stor batch.
    # Denne setter føringen for hele scriptets struktur, som er avhengig av at alle filnavnene er plassert på samme sted
    pe.set_model_csv_attributes_batch(path_csv_parameter_verdier, rock_mass_material, weakness_zone_material,
                                      stress_ratio, overburden, mektighet_attributes, angel_attributes,
                                      y_attributes, x_attributes)
    # set_model_csv_attributes er mindre sentral, men kan benyttes for å systematisere de ulike filer med hensyn på
    # overdekning i et senere stadium for mer oversiktelig lagring av resultater.
    paths_csv = pe.make_csv_paths(overdekninger, paths_shell_csv)
    pe.delete_content_csv(paths_csv)
    pe.set_model_csv_attributes(paths_csv, rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                                mektighet_attributes, angel_attributes, y_attributes, x_attributes)

    """
    I dette segmentet blir andre viktige variable definert. Stier for ulike programmer som skal benyttes, allerede
    eksisterende data blir hentet fra ulike filplasseringer og plassert som regel i en dataframe, struktur
    for ulike dataframes defineres.
     """

    # stier, programmer som kalles på:
    path_rs2 = main_stringobjects['object'][3]
    path_rs2_compute = main_stringobjects['object'][4]
    path_rs2_interpret = main_stringobjects['object'][5]

    # hente koordinater fra mus
    sti_koordinater_mus = main_stringobjects['object'][6]
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']

    # lage stier til filer og kopiere kildefil, eventuelt slette allerede eksisterende mapper:

    # sti_kildefil:
    # inneholder stien til kildefilen.
    sti_kildefil_rs2, sti_kildefil_csv = mo.get_file_paths_batch(paths_shell_rs2, path_csv_parameter_verdier)

    # sti_til_mappe_for_lagring_av_stier:
    # er stien til der hvor alle kopier av kildefilene skal lagres i et mappesystem.
    sti_til_mappe_for_arbeidsfiler = main_stringobjects['object'][7]
    sti_til_mapper_endelige_filer = main_stringobjects['object'][8]
    # create_work_and_storage_folders
    mo.create_work_and_storage_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)

    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # er stien til .csv-fil der stier til kopier fra forrige gjennomkjøring er lagret.
    # Denne brukes hvis man ønsker å slette forrige forsøk.
    sti_csv_gamle_rs2stier = main_stringobjects['object'][9]
    sti_csv_gamle_csvstier = main_stringobjects['object'][10]
    sti_list_variables_2lines_calculations = [main_stringobjects['object'][11], main_stringobjects['object'][12],
                                              main_stringobjects['object'][13], main_stringobjects['object'][14],
                                              main_stringobjects['object'][15]]
    # get_old_paths_df henter stier fra alleredeeksisterende eksperiment og lagrer disse i dataframe-format
    df_stier_rs2filer, df_stier_csvfiler = mo.get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)
    # mappenavn_til_rs2/csv:
    # inneholder navnene til kolonnene i df_stier_rs2/csvfiler
    mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mapper_endelige_filer)

    # her stilles spm om det vil startes et nytt eksperiment, hvis ja så blir det dannet nye filer og de gamle forkastes
    # change = mo.get_new_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2,
    #                              sti_kildefil_csv, sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)
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
    # ea.execute_model_alteration(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
    #                             df_stier_csvfiler, df_endrede_attributter_rs2filer,
    #                             list_which_material, list_0lines_inside, list_1line_inside,
    #                             list_2lines_inside, list_excluded_files_2linescalc, list_points_to_check,
    #                             sti_list_variables_2lines_calculations)
    list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
        go.get_parameters_2lines_inside(sti_list_variables_2lines_calculations)
    list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc, list_points_to_check = \
        list_of_df_2lines_info[0], list_of_df_2lines_info[1], list_of_df_2lines_info[2], \
        list_of_df_2lines_info[3], list_of_df_2lines_info[4]
    print(list_of_df_2lines_info[4]['S_bm80_ss1_k1_od500/'][0])
    print(type(list_of_df_2lines_info[4]['S_bm80_ss1_k1_od500/'][0]))
    """her lages diskretisering og mesh til alle modellene"""
    # ea.create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time)

    """
    her kjøres alle kalkulasjonene, med en dynamisk while-løkke slik at når alle kalkulasjonene er ferdig, 
    så fortsetter scriptet. Det er viktig å sørge for at rs2_compute allerede finner den mappen som filene ligger i.
    """
    # ea.calculate(path_rs2_compute, time)

    """åpner interpret, der alle resultater som skal benyttes hentes ut og lagres i csv-format"""
    # ea.store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
    #               df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time)

    """her kalkuleres differensene til de mest sentrale punktene som skal presenteres ved bruk av matplotlib"""
    list_paths_differences, list_diff_navn, list_paths_values = \
        ea.execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv,
                                   df_stier_csvfiler, list_points_to_check, sti_til_mapper_endelige_filer,
                                   list_excluded_files_2linescalc, list_valnavn, list_2lines_inside)

    """her plottes det som skal plottes"""
    ea.execute_plots(list_paths_differences, list_diff_navn, list_paths_values, list_valnavn,
                     mappenavn_til_rs2, mappenavn_til_csv, parameter_navn_interpret, df_stier_csvfiler,
                     list_of_lists_attributes, attribute_type, fysiske_enheter, list_excluded_files_2linescalc,
                     list_colormaps, list_2lines_inside)
