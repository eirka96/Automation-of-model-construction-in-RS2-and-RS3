import pyautogui as pag
import pandas as pd

from time import sleep
from subprocess import Popen

from Automatisering_RS2 import module_main_functions as mmf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


"""
The four functions beneath is used to store the excavation query line values fetched from a specific file
"""
"""
This function should be used the first time the storing process is initiated. 

It sets the stage to the excavation stage.
"""


def store_results_csv_prep_init(df_koordinates_mouse, name_col_df, i=1, time=None):
    if time is None:
        time = mmf.get_time_increments()
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
              interval=time[1])  # velg excavation stage
    i += 1
    pag.hotkey('f6', interval=time[1])
    # pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #                interval=time[1])  # change type
    i += 1
    # pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #                interval=time[1])  # choose tot sigma
    i += 1
    # pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #           interval=time[1])  # choose sig1
    i += 1
    pag.hotkey('ctrl', 'e', interval=time[1])  # generates excavation query line
    return i


"""
Same as function over, but:

This function should be used if there happened some complications during the calculation process and the operation
must be repeated. This function sets the interpreter into showing stress which is the first parameter to be stored. If
this was not done, the interpreter is saved to show total deformation.
"""


def store_results_csv_prep(df_koordinates_mouse, name_col_df, i=1, time=None):
    if time is None:
        time = mmf.get_time_increments()
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
              interval=time[1])  # choose stage 2
    i += 1
    pag.hotkey('f6', interval=time[1])
    pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1])  # change type
    i += 1
    pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1])  # choose tot sigma
    i += 1
    pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                   interval=time[1])  # choose sig1
    i += 1
    pag.hotkey('ctrl', 'e', interval=time[1])  # generates excavation query line
    return i


"""
saves the content of excavation line to clipboard, later to be saved in csv-file
"""


def interpret_resultat_til_clipboard(time=None):
    if time is None:
        time = mmf.get_time_increments()
    pag.press('f6', interval=time[2])
    pag.click(754, 527, interval=time[1], button='right')
    pag.click(846, 666, interval=time[1])
    return


"""
the function stores the content given in a excavation query of a model in a specific csv file
"""


def store_results_in_csv(df_koordinates_mouse, name_col_df, path_fil_csv, navn_parameter, i=1, time=None):
    if time is None:
        time = mmf.get_time_increments()
    if i == 4:
        sr = pd.DataFrame([navn_parameter])
        sr.to_csv(path_or_buf=path_fil_csv, mode='w', sep=';', header=False, index=False)
        pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                       interval=time[1])  # choose boundary 1st time, right click
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1])  # velg copy data
        i += 1
        data = pd.read_clipboard()  # fetch content stored in clipboard, see full description in
        # Logg - Mastergradsoppgave_Modellering, 10.08.2021
        data.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=True)  # data stored in a given csv
    else:
        sr = pd.DataFrame([navn_parameter])
        sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # change parameter
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # choose deformation
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # choose total deformation
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='right')  # choose boundary 2nd time, rightclick
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # choose copy data
        i += 1
        data = pd.read_clipboard()  # fetch content stored in clipboard, see full description in
        # Logg - Mastergradsoppgave_Modellering, 10.08.2021
        data.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=None, index=True)  # data stored in a given csv
    return i


"""
store_data sequences through each model
"""


def store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
               df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time,
               ll_inner_points, bool_is_first_time_execute_data_store, bool_shall_execute_storedata, files_to_skip,
               storage_calculation_times):
    """

    @param mappenavn_til_rs2:
    @param mappenavn_til_csv:
    @param df_stier_rs2filer:
    @param df_stier_csvfiler:
    @param path_rs2_interpret:
    @param df_koordinater_mus:
    @param navn_kol_df_koord_mus:
    @param ant_parametere_interpret:
    @param parameter_navn_interpret:
    @param time:
    @param ll_inner_points:
    @param bool_is_first_time_execute_data_store:
    @param bool_shall_execute_storedata:
    @param files_to_skip:
    @param storage_calculation_times:
    @return:
    """
    if bool_shall_execute_storedata is False:
        return
    time_operation = time.time()
    category = 'store_data'

    i = 1
    for k, (navn_rs2, navn_csv, (colname_innerpoints, l_inner_points)) in enumerate(zip(
            mappenavn_til_rs2, mappenavn_til_csv, ll_inner_points.iteritems())):
        if k in files_to_skip:
            continue
        for j, innerpoints in enumerate(l_inner_points):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2_interpret, path_fil_rs2])
                sleep(5)
                # if there is a window open in addition to rs2 interpret, this removes it
                pag.press('tab', interval=time[1])
                pag.press('enter', interval=time[2])
                if bool_is_first_time_execute_data_store is True:
                    i = store_results_csv_prep_init(df_koordinater_mus, navn_kol_df_koord_mus, i)
                else:
                    i = store_results_csv_prep(df_koordinater_mus, navn_kol_df_koord_mus, i)
                for q in range(ant_parametere_interpret):
                    navn_parameter = parameter_navn_interpret[q]
                    i = store_results_in_csv(df_koordinater_mus, navn_kol_df_koord_mus, path_fil_csv,
                                             navn_parameter, i)
                # markere slutten på fila
                sr = pd.DataFrame(['end'])
                sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
                # lukke interpret
                pag.hotkey('ctrl', 's', interval=time[1])
                pag.hotkey('alt', 'f4', interval=time[1])
                i = 1
    mmf.calculate_computation_time(time_operation, category, storage_calculation_times)
    return
