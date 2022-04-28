import psutil
import pyautogui as pag
import pandas as pd
import numpy as np

from os import path
from os import mkdir
from time import sleep
from subprocess import Popen
import Automatisering_RS2.source.Auto_handlinger_RS2 as Auto
import Automatisering_RS2.source.filbehandling.make_objects as mo


def pause_script():
    while True:
        try:
            command = input('fortsette script? j for ja: ')
            if command == 'j':
                break
            elif command == 'n':
                break
            else:
                print('j for ja din nisse!')
        except NameError:
            print('implementert verdi ukjent')
            continue
    return


def execute_model_alteration(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler,
                             df_endrede_attributter_rs2filer):
    i = 0
    points_to_check = []
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            print(path_fil_rs2)
            print(path_fil_csv)
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                streng_endringer = df_endrede_attributter_rs2filer[navn_rs2][j]
                points = Auto.alter_model(path_fil_rs2, df_endrede_attributter_rs2filer, mappenavn_til_rs2, i, j)
                points_to_check.append(points)
        i += 1
    return points_to_check


def create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time):
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2, path_fil_rs2])
                sleep(7)
                # df_koordinater_mus = mo.transform_coordinates_mouse(sti_koordinater_mus, navn_kol_df_koord_mus, q)
                # pyautogui operasjoner begynner her
                pag.leftClick(927, 490, interval=time[2])
                pag.hotkey('alt', 'f4', interval=time[2])
                # lage diskretisering og mesh
                pag.hotkey('ctrl', 'm', interval=time[2])
                pag.hotkey('ctrl', 's', interval=time[2])
                pag.hotkey('alt', 'f4', interval=time[2])
    return


def calculate(path_rs2_compute, time):
    Popen([path_rs2_compute])
    sleep(5)
    Auto.handlinger_kalkulasjon()
    # lukke RS2 Compute
    pag.hotkey('alt', 'f4', interval=time[2])
    return


def store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
               df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time):
    i = 0
    k = 0
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2_interpret, path_fil_rs2])
                sleep(10)
                i = Auto.store_results_csv_prep(df_koordinater_mus, navn_kol_df_koord_mus, i)
                pag.hotkey('f6', interval=time[1])
                for k in range(ant_parametere_interpret):
                    navn_parameter = parameter_navn_interpret[k]
                    i = Auto.store_results_in_csv(df_koordinater_mus, navn_kol_df_koord_mus, path_fil_csv,
                                                  navn_parameter, i)
                # markere slutten på fila
                sr = pd.DataFrame(['end'])
                sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
                # lukke interpret
                pag.hotkey('alt', 'f4', interval=time[1])
                pag.press('enter', interval=time[1])
                # # lukke programmet
                # pag.hotkey('ctrl', 's', interval=time[1])
                # pag.hotkey('alt', 'f4', interval=time[1])
                i = 0
        k += 1


def execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
                            df_stier_csvfiler, points_to_check, sti_til_mappe_for_arbeidsfiler,
                            sti_til_mapper_endelige_filer):
    k = 0
    list_differences = mo.make_container_diff(mappenavn_til_rs2)
    list_values = mo.make_container_diff(mappenavn_til_rs2)
    parameter_navn_interpret0 = mo.prep_parameter_navn(parameter_navn_interpret)
    list_paths_differences = []
    list_diff_navn = []
    list_paths_values = []
    list_val_navn = []
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        # element_files_corrupted er definert mtp en treshold for filstørrelse, da de filer hvor feilklikking inntreffer
        # viser ca 1/3 mindre størrelse.
        elements_files_corrupted = mo.get_elements_corrupted_files(df_stier_csvfiler[navn_csv])
        list_paths_differences.append([])
        list_diff_navn.append([])
        if elements_files_corrupted is not None:
            check = elements_files_corrupted.copy()
        else:
            check = [None]
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                if j == check[0]:
                    if len(check) > 1:
                        check.pop(0)
                    continue
                elif j == 135 or j == 149:
                    continue
                points = points_to_check[k][j]
                query_values = mo.get_Query_values(path_fil_csv, parameter_navn_interpret0)
                to_plot = mo.get_values_to_plot(query_values)
                query_positions = mo.get_query_positions(query_values)
                print('PIKK')
                print(j)
                differences = mo.get_difference(to_plot, points, query_positions)
                quad_high = mo.get_values_quad(to_plot, points, query_positions, [0, 1])
                print(quad_high)
                quad_low = mo.get_values_quad(to_plot, points, query_positions, [2, 3])
                values_to_plot = [quad_high, quad_low]
                if differences is not None:
                    list_differences[k].append(differences)
                if all(value is not None for value in values_to_plot):
                    list_values[k].append(values_to_plot)
                # mo.plot_data(to_plot, parameter_navn_interpret)
        print('OOOGAAAHHHHH')
        print(list_values)
        paths_fil_csv = df_stier_csvfiler[navn_csv]
        paths_differences, diff_navn = mo.create_difference_csv(navn_csv, list_differences[k], parameter_navn_interpret,
                                                                paths_fil_csv, sti_til_mappe_for_arbeidsfiler,
                                                                elements_files_corrupted, 'differenser',
                                                                sti_til_mapper_endelige_filer)
        list_paths_differences[k] = paths_differences
        list_diff_navn[k] = diff_navn
        # paths_values, val_navn = mo.create_values_csv(navn_csv, list_values[k], parameter_navn_interpret,
        #                                               paths_fil_csv, sti_til_mappe_for_arbeidsfiler,
        #                                               elements_files_corrupted, 'values',
        #                                               sti_til_mapper_endelige_filer)
        # list_paths_values[k] = paths_values
        # list_val_navn[k] = val_navn
        print(paths_differences)
        # print(paths_values)
        k += 1
    return list_paths_differences, list_diff_navn, list_paths_values, list_val_navn


def execute_plots(list_paths_differences, list_diff_navn, list_paths_values, list_val_navn,
                  mappenavn_til_rs2, mappenavn_til_csv, parameter_navn_interpret, df_stier_csvfiler,
                  list_of_lists_attributes, attribute_type, fysiske_enheter):
    for navn_rs2, navn_csv, paths_differences, diff_navn, paths_values, val_navn in zip(
            mappenavn_til_rs2, mappenavn_til_csv, list_paths_differences, list_diff_navn, list_paths_values,
            list_val_navn):
        if paths_differences is None:
            continue
        parameter_navn_interpret0 = mo.prep_parameter_navn(parameter_navn_interpret)
        elements_files_corrupted = mo.get_elements_corrupted_files(df_stier_csvfiler[navn_csv])
        # mo.plot_differences(paths_differences, parameter_navn_interpret0, elements_files_corrupted, diff_navn,
        #                     fysiske_enheter)
        # indices_selection_true, indices_selection_augm = mo.get_indices_paths_selection(list_of_lists_attributes,
        #                                                                                 attribute_type,
        #                                                                                 df_stier_csvfiler[navn_csv],
        #                                                                                 elements_files_corrupted)
        list_category, list_indices = mo.get_category(list_of_lists_attributes, attribute_type,
                                                      df_stier_csvfiler[navn_csv], elements_files_corrupted)
        mo.plot_difference_selection(paths_differences, parameter_navn_interpret0, diff_navn, fysiske_enheter,
                                     list_category, list_indices, attribute_type)
        # mo.plot_difference_selection0(paths_differences, parameter_navn_interpret0, diff_navn, fysiske_enheter,
        #                               indices_selection_true, indices_selection_augm)
    return

