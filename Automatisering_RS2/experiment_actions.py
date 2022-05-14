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


def execute_model_alteration(ytre_grenser_utstrekning, n_points_tunnel_boundary,
                             mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
                             df_stier_csvfiler, df_endrede_attributter_rs2filer, list_which_material, list_0lines_inside,
                             list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc,
                             list_points_to_check, sti_list_variables_2lines_calculations,
                             list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points):
    for i, (navn_rs2, navn_csv, utskrekning) in enumerate(zip(mappenavn_til_rs2, mappenavn_til_csv,
                                                              ytre_grenser_utstrekning)):
        list_0lines_inside.append([]), list_1line_inside.append([]), list_2lines_inside.append([]),
        list_excluded_files_2linescalc.append([]), list_points_to_check.append([]),
        list_iternumber_0.append([]), list_iternumber_1.append([]), list_iternumber_2.append([]),
        ll_inner_points.append([])
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            print(path_fil_rs2)
            # print(path_fil_csv)
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                streng_endringer = df_endrede_attributter_rs2filer[navn_rs2][j]
                Auto.alter_model(utskrekning, n_points_tunnel_boundary,
                                 path_fil_rs2, path_fil_csv, df_endrede_attributter_rs2filer,
                                 mappenavn_til_rs2, list_which_material, list_0lines_inside[i], list_1line_inside[i],
                                 list_2lines_inside[i], list_excluded_files_2linescalc[i],
                                 list_points_to_check[i], i, j, list_iternumber_0[i], list_iternumber_1[i],
                                 list_iternumber_2[i], ll_inner_points[i])
            else:
                ll_inner_points[i].append(None)
    list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
        mo.create_csv_2lines_info(list_0lines_inside, list_1line_inside, list_2lines_inside,
                                  list_excluded_files_2linescalc, list_points_to_check,
                                  sti_list_variables_2lines_calculations, mappenavn_til_rs2,
                                  list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points)
    return list_of_df_2lines_info, colnames_of_dfs_2lines_info


def create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time):
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2, path_fil_rs2])
                sleep(5)
                # df_koordinater_mus = mo.transform_coordinates_mouse(sti_koordinater_mus, navn_kol_df_koord_mus, q)
                # pyautogui operasjoner begynner her
                pag.leftClick(927, 490, interval=time[1])
                # pag.hotkey('alt', 'f4', interval=time[2])
                # lage diskretisering og mesh
                pag.hotkey('ctrl', 'm', interval=time[1])
                pag.hotkey('ctrl', 's', interval=time[1])
                pag.hotkey('alt', 'f4', interval=time[1])
    return


def calculate(path_rs2_compute, time, df_filnavn_rs2, sti_til_mappe_for_arbeidsfiler, path_store_unsuc_tol_models,
              tolerance):
    Popen([path_rs2_compute])
    sleep(5)
    Auto.handlinger_kalkulasjon()
    # lukke RS2 Compute
    pag.hotkey('alt', 'f4', interval=time[2])
    mo.get_files_unsuc_tolerance(sti_til_mappe_for_arbeidsfiler, df_filnavn_rs2, path_store_unsuc_tol_models, tolerance)
    return


def store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
               df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret, parameter_navn_interpret, time,
               list_excluded_files_2linescalc, ll_inner_points):
    i = 0
    k = 0
    for navn_rs2, navn_csv, (colname_innerpoints, l_inner_points) in zip(
            mappenavn_til_rs2, mappenavn_til_csv, ll_inner_points.iteritems()):
        for j, innerpoints in enumerate(l_inner_points):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2_interpret, path_fil_rs2])
                sleep(5)
                pag.press('tab', interval=time[1])
                pag.press('enter', interval=time[2])
                i = Auto.store_results_csv_prep_init(df_koordinater_mus, navn_kol_df_koord_mus, i)
                for k in range(ant_parametere_interpret):
                    navn_parameter = parameter_navn_interpret[k]
                    i = Auto.store_results_in_csv(df_koordinater_mus, navn_kol_df_koord_mus, path_fil_csv,
                                                  navn_parameter, i)
                # markere slutten på fila
                sr = pd.DataFrame(['end'])
                sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
                # lukke interpret
                pag.hotkey('ctrl', 's', interval=time[1])
                pag.hotkey('alt', 'f4', interval=time[1])
                # # lukke programmet
                # pag.hotkey('ctrl', 's', interval=time[1])
                # pag.hotkey('alt', 'f4', interval=time[1])
                i = 0
        k += 1


def execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv,
                            df_stier_csvfiler, list_points_to_check, sti_til_mapper_endelige_filer,
                            list_excluded_files_2linescalc, list_valnavn, list_2lines_inside):
    list_differences = mo.make_container_diff(mappenavn_til_rs2)
    list_values = mo.make_container_diff(mappenavn_til_rs2)
    parameter_navn_interpret0 = mo.prep_parameter_navn(parameter_navn_interpret)
    list_paths_differences = []
    list_diff_navn = []
    list_path_values = []
    for k, (navn_rs2, navn_csv, excluded_files, (twolines_colname, twolines_inside), (points_check_colname, points_to_check), valnavn) in \
            enumerate(zip(mappenavn_til_rs2, mappenavn_til_csv, list_excluded_files_2linescalc, list_2lines_inside.iteritems(),
                          list_points_to_check.iteritems(), list_valnavn)):
        # element_files_corrupted er definert mtp en treshold for filstørrelse, da de filer hvor feilklikking inntreffer
        # viser ca 1/3 mindre størrelse.
        elements_files_corrupted = mo.get_elements_corrupted_files(df_stier_csvfiler[navn_csv])
        list_paths_differences.append([])
        list_diff_navn.append([])
        list_path_values.append([])
        if not twolines_inside.isnull().values.any():
            twolines_no_corrupt = mo.get_paths_zone2lines(df_stier_csvfiler[navn_csv], elements_files_corrupted,
                                                          twolines_inside)
            for j, (stier, points) in enumerate(zip(twolines_no_corrupt, points_to_check)):
                print(j)
                print(stier)
                print(points)
                rs2_sti, csv_sti = stier[0], stier[1]
                query_values = mo.get_Query_values(csv_sti, parameter_navn_interpret0)
                to_plot = mo.get_values_to_plot(query_values)
                query_positions = mo.get_query_positions(query_values)
                differences = mo.get_difference(to_plot, points, query_positions)
                quad_high = mo.get_values_quad(to_plot, points, query_positions, [0, 1])
                quad_low = mo.get_values_quad(to_plot, points, query_positions, [2, 3])
                values_to_plot = [quad_high[0][0][0], quad_high[0][0][1], quad_high[1][0][1], quad_high[0][1][0],
                                  quad_high[0][1][1], quad_high[1][1][1],
                                  quad_low[0][0][0], quad_low[0][0][1], quad_low[1][0][1], quad_low[0][1][0],
                                  quad_low[0][1][1], quad_low[1][1][1]]
                if differences is not None:
                    list_differences[k].append(differences)
                if all(value is not None for value in values_to_plot):
                    list_values[k].append(values_to_plot)
            paths_fil_csv = df_stier_csvfiler[navn_csv]
            paths_differences, diff_navn = mo.create_difference_csv(navn_csv, list_differences[k], parameter_navn_interpret,
                                                                    paths_fil_csv, 'differenser',
                                                                    sti_til_mapper_endelige_filer, twolines_no_corrupt)
            list_paths_differences[k] = paths_differences
            list_diff_navn[k] = diff_navn
            path_value = mo.create_values_csv(navn_csv, list_values[k], parameter_navn_interpret, paths_fil_csv,
                                              elements_files_corrupted, 'values', sti_til_mapper_endelige_filer, valnavn,
                                              twolines_inside)
            list_path_values[k] = path_value
    return list_paths_differences, list_diff_navn, list_path_values


def execute_plots(list_paths_differences, list_diff_navn, list_path_values, list_valnavn,
                  mappenavn_til_rs2, mappenavn_til_csv, parameter_navn_interpret, df_stier_csvfiler,
                  list_of_lists_attributes, attribute_type, fysiske_enheter, list_exluded_files_2linescalc,
                  list_color_map, list_2lines_inside):
    for navn_rs2, navn_csv, paths_differences, diff_navn, path_value, (exl_files_colname, exluded_files), color_map, \
        valnavn, (twolines_colname, twolines_inside) in zip(
            mappenavn_til_rs2, mappenavn_til_csv, list_paths_differences, list_diff_navn, list_path_values,
            list_exluded_files_2linescalc.iteritems(), list_color_map, list_valnavn, list_2lines_inside.iteritems()):
        if twolines_inside.empty or twolines_inside.isnull().values.any():
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
                                                      twolines_inside, elements_files_corrupted,
                                                      exluded_files)
        mo.plot_difference_selection(paths_differences, parameter_navn_interpret0, diff_navn, fysiske_enheter,
                                     list_category, list_indices, attribute_type, color_map)
        mo.plot_value_selection(path_value, parameter_navn_interpret0, diff_navn, valnavn, fysiske_enheter,
                                list_category, list_indices, attribute_type, color_map)

    return
