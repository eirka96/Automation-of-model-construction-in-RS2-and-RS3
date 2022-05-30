import pandas as pd
import Automatisering_RS2.source.filbehandling.make_objects as mo
from Automatisering_RS2.source.alter_geometry import geometry_operations as go
import plan_experiment as pe
import experiment_actions as ea
import Automatisering_RS2.source.sporing_mus.mouse_tracker as mt
import time
from datetime import timedelta

"""

hensikten med denne scripten:
opprette nye filer, med filnavn gitt av navnekonvensjonen
ha en løkke som går i gjennom hver fil og klargjør for analyse
eventuelt lukke alt til slutt

"""
time_start = time.time()
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
    tolerance = 0.001
    maxiter = 10000
    list_change_fieldstress = [300, 500, 800, 1200]
    ant_parametere_interpret = 2
    parameter_navn_interpret = ['sigma 1:', 'total deformasjon:', 'end']
    parameters_varied = ['od', 'v', 'x']
    fysiske_enheter = ['[MPa]', '[m]']
    # definerer parameterenes størrelser
    rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes, angel_attributes, \
        y_attributes, x_attributes = 80, 1, 1, [100, 200, 300, 500, 800, 1200], \
                                     4, [45, 52.5, 60, 67.5, 75, 82.5, 90], 0, \
                                     [0, 0, 0.25, 0.5, 0.75, 1, 2, 3, 4, 4.5, 5, 5.5, 5.75, 6, 7, 8, 9, 10, 11, 13, 15,
                                      20]
    true_lengths = [x + mektighet_attributes/2 for i, x in enumerate(x_attributes) if i > 0]
    # NB!!!!!! x_attributes er her missvisende, men er valgt å forbli slik pga liten tid. Det er funnet ut at det
    # er mer hensiktsmessig å nytte minste avstand fra sone til tunnelsenter. y blir altså ikke brukt og x er egt
    # denne nye normerte avstand, som i ea.set_model_csv_attributes_batch blir endret til rett x-verdi.
    ytre_grenser_utstrekning = [25, 100, 150, 150, 150, 150, 150]
    overdekninger = [25, 100, 200, 300, 500, 800, 1200]
    files_to_skip = [0]
    n_points_tunnel_boundary = 360
    # definerer en liste over alle attributter (attributes_list, samt en liste over de attributter som skal varieres
    # (list_of_lists_attributes). Brukes i plotte_funksjonene.
    attributes_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden, mektighet_attributes,
                       angel_attributes, y_attributes, x_attributes]
    list_of_lists_attributes, attribute_type = mo.return_lists(attributes_list)

    color_map = {
        'od': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'fuchsia'],
        'v': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'fuchsia'],
        'm': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'fuchsia'],
        'x': ['black', 'gray', 'lightcoral', 'red', 'orange', 'yellow', 'xkcd:yellowish', 'green',
              'xkcd:lime', 'blue', 'cyan', 'purple', 'fuchsia', 'xkcd:lavender', 'xkcd:bronze']
    }
    list_colormaps = []
    list_colormaps += 7 * [color_map]
    list_which_material = [[[[15, 15], [15, 15], [16, 16], [16, 0]], [[15, 15], [15, 15], [16, 16], [15, 0]]],
                           [[15, 15], [15, 15], [15, 0], [16, 0], [16, 16]],
                           [[15, 15], [15, 15], [15, 0], [15, 0], [16, 16], [16, 16], [16, 0]]]

    valnavn_2lines = ['file_name', 'true_lengths', 'od', 'v', 'x', 'quad_high - sigma1, low',
                      'quad_high - sigma1, high', 'quad_high - sigma 1, inbetween',
                      'quad_high - totaldeformasjon, low', 'quad_high - totaldeformasjon, high',
                      'quad_high - totaldeformasjon, inbetween',
                      'quad_low - sigma1, low', 'quad_low - sigma1, high', 'quad_low - sigma 1, inbetween',
                      'quad_low - totaldeformasjon, low', 'quad_low - totaldeformasjon, high',
                      'quad_low - totaldeformasjon, inbetween']
    valnavn = ['file_name', 'od', 'v', 'x', 'sigma 1, max', 'totaldeformasjon, max',
               'quad_high - sigma 1, inbetween', 'quad_high - totaldeformasjon, inbetween',
               'quad_low - sigma 1, inbetween', 'quad_low - totaldeformasjon, inbetween']
    list_valnavn_2lines = []
    list_valnavn = []
    list_valnavn_2lines += 7 * [valnavn_2lines]
    list_valnavn += 7 * [valnavn]
    liste_stier_PycharmProjects_automatisering = pd.read_csv(r'C:\temp\thesis\eksperimenter\mektighet_1'
                                                             r'\base_modeler\Pycharm_automatisering'
                                                             r'\liste_stier_PycharmProjects_automatisering.txt',
                                                             sep=';')
    main_stringobjects = pd.read_csv(liste_stier_PycharmProjects_automatisering['object'][0], sep=';')

    list_0lines_inside, list_1line_inside, list_2lines_inside, list_iternumber_0, list_iternumber_1, \
        list_iternumber_2, list_excluded_files_2linescalc, list_points_to_check, ll_inner_points = \
        [], [], [], [], [], [], [], [], []

    """ Her er det mulig å gjøre endringer på koordinatene lagret i liste_datamus_koordinater"""
    # mt.mouse_tracker(liste_stier_PycharmProjects_automatisering['object'][1])
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
    path_csv_parameter_verdier_fil = main_stringobjects['object'][0]
    path_csv_parameter_verdier_mappe = main_stringobjects['object'][1]
    paths_shell_rs2 = main_stringobjects['object'][2]
    paths_shell_csv = main_stringobjects['object'][3]
    # set_model_csv_attributes_batch så blir filnavnene skapt på bakgrunn av parameterverdiene lagret i en stor batch.
    # Denne setter føringen for hele scriptets struktur, som er avhengig av at alle filnavnene er plassert på samme sted
    number_of_files = pe.set_model_csv_attributes_batch(path_csv_parameter_verdier_fil, rock_mass_material,
                                                        weakness_zone_material, stress_ratio, overburden,
                                                        mektighet_attributes, angel_attributes, y_attributes,
                                                        x_attributes)
    # set_model_csv_attributes er mindre sentral, men kan benyttes for å systematisere de ulike filer med hensyn på
    # overdekning i et senere stadium for mer oversiktelig lagring av resultater.
    # paths_csv = pe.make_csv_paths(overdekninger, paths_shell_csv)
    # pe.delete_content_csv(paths_csv)
    # pe.set_model_csv_attributes(paths_csv, rock_mass_material, weakness_zone_material, stress_ratio, overburden,
    #                             mektighet_attributes, angel_attributes, y_attributes, x_attributes)

    """
    I dette segmentet blir andre viktige variable definert. Stier for ulike programmer som skal benyttes, allerede
    eksisterende data blir hentet fra ulike filplasseringer og plassert som regel i en dataframe, struktur
    for ulike dataframes defineres.
     """

    # stier, programmer som kalles på:
    path_rs2 = main_stringobjects['object'][4]
    path_rs2_compute = main_stringobjects['object'][5]
    path_rs2_interpret = main_stringobjects['object'][6]

    # hente koordinater fra mus
    sti_koordinater_mus = main_stringobjects['object'][7]
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']

    # lage stier til filer og kopiere kildefil, eventuelt slette allerede eksisterende mapper:

    # sti_kildefil:
    # inneholder stien til kildefilen.
    sti_kildefil_rs2, sti_kildefil_csv = mo.get_file_paths_batch(paths_shell_rs2, path_csv_parameter_verdier_fil)

    # sti_til_mappe_for_lagring_av_stier:
    # er stien til der hvor alle kopier av kildefilene skal lagres i et mappesystem.
    sti_til_mappe_for_arbeidsfiler = main_stringobjects['object'][8]
    sti_til_mapper_endelige_filer = main_stringobjects['object'][9]
    # create_work_and_storage_folders
    mo.create_work_and_storage_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)

    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # er stien til .csv-fil der stier til kopier fra forrige gjennomkjøring er lagret.
    # Denne brukes hvis man ønsker å slette forrige forsøk.
    sti_csv_gamle_rs2stier = main_stringobjects['object'][10]
    sti_csv_gamle_csvstier = main_stringobjects['object'][11]
    sti_list_variables_2lines_calculations = [main_stringobjects['object'][12], main_stringobjects['object'][13],
                                              main_stringobjects['object'][14], main_stringobjects['object'][15],
                                              main_stringobjects['object'][16], main_stringobjects['object'][17],
                                              main_stringobjects['object'][18], main_stringobjects['object'][19],
                                              main_stringobjects['object'][20]]
    sti_tolerance_too_high = main_stringobjects['object'][21]
    sti_values_toplot_2lines = main_stringobjects['object'][22]
    sti_values_toplot = main_stringobjects['object'][23]
    # get_old_paths_df henter stier fra alleredeeksisterende eksperiment og lagrer disse i dataframe-format
    df_stier_rs2filer, df_stier_csvfiler = mo.get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)
    # mappenavn_til_rs2/csv:
    # inneholder navnene til kolonnene i df_stier_rs2/csvfiler
    mappenavn_til_rs2, mappenavn_til_csv = mo.get_name_folders(sti_til_mapper_endelige_filer)
    df_filnavn_rs2, df_filnavn_csv = mo.make_file_name(path_csv_parameter_verdier_fil)

    # her stilles spm om det vil startes et nytt eksperiment, hvis ja så blir det dannet nye filer og de gamle forkastes
    change = mo.get_new_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2,
                                 sti_kildefil_csv, sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier,
                                 path_csv_parameter_verdier_mappe, ytre_grenser_utstrekning)
    if change[0]:
        df_stier_rs2filer, df_stier_csvfiler = change[1], change[2]

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
    time0 = [0, 0.7, 1, 2, 5]
    """her lages geometriene til rs2-modellene, evt så hentes de sentrale punktene ut"""
    list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
        ea.execute_model_alteration0(ytre_grenser_utstrekning, n_points_tunnel_boundary, overdekninger,
                                     list_change_fieldstress,
                                     mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
                                     df_stier_csvfiler, df_endrede_attributter_rs2filer, list_which_material,
                                     list_0lines_inside, list_1line_inside, list_2lines_inside,
                                     list_excluded_files_2linescalc, list_points_to_check,
                                     sti_list_variables_2lines_calculations, list_iternumber_0, list_iternumber_1,
                                     list_iternumber_2, ll_inner_points)
    # list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
    #     go.get_parameters_2lines_inside(sti_list_variables_2lines_calculations)
    list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc, list_points_to_check, \
        list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points = \
        list_of_df_2lines_info[0], list_of_df_2lines_info[1], list_of_df_2lines_info[2], list_of_df_2lines_info[3], \
        list_of_df_2lines_info[4], list_of_df_2lines_info[5], list_of_df_2lines_info[6], list_of_df_2lines_info[7], \
        list_of_df_2lines_info[8]

    """her lages diskretisering og mesh til alle modellene"""
    ea.create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time0,
                   files_to_skip)

    """
    her kjøres alle kalkulasjonene, med en dynamisk while-løkke slik at når alle kalkulasjonene er ferdig, 
    så fortsetter scriptet. Det er viktig å sørge for at rs2_compute allerede finner den mappen som filene ligger i.
    """
    ea.calculate(path_rs2_compute, time0, df_filnavn_rs2, sti_til_mappe_for_arbeidsfiler, sti_tolerance_too_high,
                 tolerance, number_of_files)
    # mo.get_files_unsuc_tolerance(sti_til_mappe_for_arbeidsfiler, df_filnavn_rs2, sti_tolerance_too_high, tolerance)
    """åpner interpret, der alle resultater som skal benyttes hentes ut og lagres i csv-format"""
    ea.store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
                  df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time0,
                  list_excluded_files_2linescalc, ll_inner_points)

    """her kalkuleres differensene til de mest sentrale punktene som skal presenteres ved bruk av excel"""
    list_paths_values_2lines, list_paths_values = ea.execute_data_processing(parameter_navn_interpret,
                                                                             mappenavn_til_rs2, mappenavn_til_csv,
                                                                             df_stier_csvfiler, list_points_to_check,
                                                                             sti_til_mapper_endelige_filer,
                                                                             list_excluded_files_2linescalc,
                                                                             list_valnavn_2lines, list_2lines_inside,
                                                                             sti_values_toplot_2lines,
                                                                             list_valnavn, sti_values_toplot,
                                                                             list_0lines_inside, list_1line_inside,
                                                                             parameters_varied)
time_end = time.time()
time_diff_in_seconds = time_end-time_start
time_diff_in_hours_min_sec = timedelta(seconds=time_diff_in_seconds)
print("Tid brukt for kjøring av script:     {}. (#hours#:#minutes#:#seconds#)".format(time_diff_in_hours_min_sec))
