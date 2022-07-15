import numpy as np
import os
import pandas as pd
import re
import time

from Automatisering_RS2 import module_main_functions as mmf


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def get_values_quad(to_plot, points, query_positions):
    if not (to_plot is not None and points is not None):
        return None
    value_intersect, indices_max_value = [], []
    points = [[round(point[0], 3), round(point[1], 3)] for point in points]
    for k, (data_sep, q_pos_sep) in enumerate(zip(reversed(to_plot), reversed(query_positions))):
        values, indices = [], []
        for point in points:
            for i, (value, q_pos) in enumerate(zip(data_sep, q_pos_sep)):
                if q_pos == point:
                    values.append(value[1])
                    indices.append(i)
        idx_a = indices[0]
        idx_b = indices[1]
        idx_c = indices[2]
        idx_d = indices[3]
        if k == 0:
            max_value_h, max_val_with_arc_h = get_max_totdef(idx_a, idx_b, data_sep)
            max_value_l, max_val_with_arc_l = get_max_totdef(idx_c, idx_d, data_sep)
            index_max_value_h = data_sep.index(max_val_with_arc_h)
            index_max_value_l = data_sep.index(max_val_with_arc_l)
            list_append = [values[0], values[1], max_value_h, values[3], values[2], max_value_l]
            for a in list_append:
                value_intersect.append(a)
            indices_max_value.append(index_max_value_h), indices_max_value.append(index_max_value_l)
        else:
            max_value_h = data_sep[indices_max_value[0]][1]
            max_value_l = data_sep[indices_max_value[1]][1]
            list_append = [values[0], values[1], max_value_h, values[3], values[2], max_value_l]
            for a in list_append:
                value_intersect.append(a)
    return value_intersect


def get_max_totdef(idx_a, idx_b, data_sep):
    if idx_a < idx_b:
        indices = [i for i in range(idx_a, idx_b + 1, 1)]
    else:
        l1 = [i for i in range(0, idx_b + 1, 1)]
        l2 = [i for i in range(idx_a, len(data_sep), 1)]
        indices = l1 + l2

    data = [data_sep[idx] for idx in indices]
    data_exl_arc = [data_sep[idx][1] for idx in indices]
    max_def = max(data_exl_arc)
    idx = data_exl_arc.index(max_def)
    max_def_with_arc = data[idx]
    return max_def, max_def_with_arc



def make_container_diff(mappenavn_rs2):
    container = []
    for i in range(len(mappenavn_rs2)):
        container.append([])
    return container



def get_parameter_values(navn_allines, params_varied):
    regex_shale = r'(?<=_{})\d*\.*\d*'
    param_values = []
    for param in params_varied:
        reg_pat = regex_shale.format(param)
        param_value = float(re.findall(reg_pat, navn_allines)[0])
        param_values.append(param_value)
    return param_values











def get_corrupted_file_paths(file_paths, elements_corrupted_files):
    if elements_corrupted_files is None:
        corrupted_paths = ['']
    else:
        corrupted_paths = [path for i, path in enumerate(file_paths) if elements_corrupted_files.count(i) > 0]
    return corrupted_paths


def get_paths_zone2lines(file_paths, elements_corrupted_files, twolines_inside):
    corrupted_paths = get_corrupted_file_paths(file_paths, elements_corrupted_files)
    paths = [iteration for iteration in twolines_inside if iteration[0] not in corrupted_paths]
    return paths


def get_paths_without_corrupted(file_paths, elements_corrupted_files):
    corrupted_paths = get_corrupted_file_paths(file_paths, elements_corrupted_files)
    paths = [iteration for iteration in file_paths if iteration not in corrupted_paths]
    return paths


"""

"""


def create_csv_max_values(foldername_csv, list_values, parameternavn_interpret, paths_fil_csv,
                          path_data_storage, elements_corrupted_files, val_navn,
                          sti_values_toplot, parameters_varied, list_true_lengths):
    if all(path is None for path in paths_fil_csv):
        return None, None
    t = path_data_storage
    t = mmf.alternate_slash([t])[0]
    p = parameternavn_interpret.copy()
    p.pop()
    # fjerner de paths som er korruperte
    paths = get_paths_without_corrupted(paths_fil_csv, elements_corrupted_files)
    list_navn_allines = [name.replace('.csv', '') for name in paths]
    list_varied_param_values = [get_parameter_values(navn, parameters_varied) for navn in list_navn_allines]
    # lager paths til der hvor verdiene skal lagres
    path_all = t + '/' + foldername_csv + 'max_values.csv'
    list_to_df = []
    for navn, values, varied_param_values, true_len in zip(list_navn_allines, list_values, list_varied_param_values,
                                                 list_true_lengths):
        list_to_df.append([navn] + [true_len] + varied_param_values + values)
    df_values = pd.DataFrame(list_to_df, columns=val_navn)
    df_values.to_csv(path_or_buf=path_all, sep=';', mode='w', index=False)
    df_values.to_csv(path_or_buf=sti_values_toplot, sep=';', mode='a', index=False)
    return


"""
these functions
"""


def get_size_file(filepath):
    size = os.path.getsize(filepath) / 1000  # gives answear in kilobytes
    return size


def get_list_size_files(filepaths):
    file_sizes = []
    for path in filepaths:
        size = get_size_file(path)
        file_sizes.append(size)
    return file_sizes


def get_average(list0):
    return sum(list0) / len(list0)


def get_elements_small_files(file_sizes):
    mean = get_average(file_sizes)
    elements = [i for i, file_size in enumerate(file_sizes) if file_size < (mean - mean / 4)]
    return elements


def get_elements_corrupted_files(file_paths):
    if all(path is None for path in file_paths):
        return [None for _ in file_paths]
    file_sizes = get_list_size_files(file_paths)
    elements = get_elements_small_files(file_sizes)
    if not elements:
        elements = [None for _ in file_paths]
    return elements


"""
get_elements_corrupted_files_2lines 
"""


def get_elements_corrupted_files_2lines(file_paths):
    if all(path is None for path in file_paths):
        return None
    file_sizes = get_list_size_files(file_paths)
    elements = get_elements_small_files(file_sizes)
    if not elements:
        elements = None
    return elements


"""
skewness
"""


def calculate_skewness(_listoflists_values, tolerance, _listoflists_archlength):
    totdef_list = _listoflists_values[1]
    arclength_list = _listoflists_archlength[0]
    list_index = [index for val, index in enumerate(totdef_list)]
    list_index = list_index[90::] + list_index[0:90]
    list_bool = []
    indices_momentum = []
    #find indices to define ranges for momentum calculation
    for i in list_index:
        if i == list_index[-1]:
            delta = np.abs(totdef_list[i] - totdef_list[0])
        else:
            delta = np.abs(totdef_list[i] - totdef_list[i+1])
        if delta > tolerance:
            _bool = True
        else:
            _bool = False
        list_bool.append(_bool)
    for i in range(len(list_index)):
        if i == len(list_index)-1:
            if (list_bool[0] is True and list_bool[i] is False) or (list_bool[0] is False and list_bool[i] is True):
                indices_momentum.append(list_index[i])
        else:
            if (list_bool[i] is True and list_bool[i+1] is False) or (list_bool[i] is False and list_bool[i+1] is True):
                indices_momentum.append(list_index[i])
    #defining the ranges, both counterclockwise and clockwise for both intersections
    range_top_med_klokka = [indices_momentum[0], indices_momentum[1]]
    range_top_mot_klokka = [indices_momentum[1], indices_momentum[0]]
    range_bot_med_klokka = [indices_momentum[2], indices_momentum[3]]
    range_bot_mot_klokka = [indices_momentum[3], indices_momentum[2]]

    totdef_top_cclockwise = totdef_list[range_top_mot_klokka[0]:range_top_mot_klokka[1]:1]
    totdef_top_clockwise = totdef_list[range_top_med_klokka[0]:range_top_med_klokka[1]:-1]
    totdef_bot_cclockwise = totdef_list[range_bot_mot_klokka[0]:range_bot_mot_klokka[1]:1]
    totdef_bot_clockwise = totdef_list[range_bot_med_klokka[0]:range_bot_med_klokka[1]:-1]
    iter_totdef = [totdef_top_cclockwise, totdef_top_clockwise, totdef_bot_cclockwise, totdef_bot_clockwise]
    momentum = []
    for list_def, ist_arc in zip(iter_totdef, iter_arc):

    #\n må legges til hver rad der hver rad lagres som streng
    return momentum


def numerical_momentum_per_meter(list_def, list_arc,radius, youngs_modulus):
    momentum = 0
    for i in range(len(list_def)-1):
        strain0, strain1 = list_def[i]/radius, list_def[i+1]/radius
        arc0, arc1 = list_arc[i], list_arc[i+1]
        momentum = momentum + calculate_momentum_i_per_meter(youngs_modulus, strain0, strain1, arc0, arc1)
    return


def calculate_momentum_i_per_meter(youngs_modulus, strain0, strain1, arc0, arc1):
    delta_strain = strain1 - strain0
    delta_arc = arc1 - arc0
    delta_arc2 = arc1**2 - arc0**2
    delta_arc3 = arc1**3 - arc0**3

    momentum_i_per_meter = (youngs_modulus/2)*((delta_arc2-arc0*delta_arc)*strain0 +
                                               (1/12)*((2*delta_arc3-3*arc0*delta_arc2)/delta_arc)*delta_strain)
    return momentum_i_per_meter


def prep_parameter_navn(parameter_navn):
    p = []
    for navn in parameter_navn:
        navn = navn + '\n'
        p.append(navn)
    return p


def prep_strings_to_float(data):
    prepped_data = []
    for index, points in enumerate(data):
        if index < 2:
            continue
        points_string = re.findall(r"[-+]?(?:\d*\.\d+|\d+\b(?!:))", points)
        points = [float(point) for point in points_string]
        prepped_data.append(points)
    return prepped_data


def get_query_values(path_to_csv, parameternavn):
    if path_to_csv is None:
        data_split = None
        return data_split
    with open(path_to_csv, 'r') as file:
        data = file.readlines()
    data_split = []
    for i in range(len(parameternavn) - 1):
        index_start = data.index(parameternavn[i])
        index_slutt = data.index(parameternavn[i + 1])
        p = data[index_start:index_slutt].copy()
        p = [l for l in p if 'UNDEFINED' not in l]
        p = prep_strings_to_float(p)
        data_split.append(p)
    return data_split


def get_query_positions(query_values):
    positions = []
    for i, query in enumerate(query_values):
        positions.append([])
        for value in query:
            positions[i].append(value[3:5])
    return positions


def get_values_to_plot(query_values):
    arclengths = []
    values = []
    for i, query in enumerate(query_values):
        arclengths.append([])
        values.append([])
        for value in query:
            arclengths[i].append(value[5])
            values[i].append(value[6])
    return arclengths, values



def get_values_to_plot_arc_and_val(query_values):
    to_plot = []
    for i, query in enumerate(query_values):
        to_plot.append([])
        for value in query:
            to_plot[i].append(value[5:])
    return to_plot


"""

"""


def execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv,
                            df_stier_csvfiler, list_points_to_check, sti_til_mapper_endelige_filer,
                            list_excluded_files_2linescalc, list_valnavn, sti_values_toplot,
                            list_0lines_inside, list_1line_inside, parameters_varied, true_lengths,
                            bool_shall_execute_data_processing, files_to_skip,
                            storage_calculation_times):
    """

    @param parameter_navn_interpret:
    @param mappenavn_til_rs2:
    @param mappenavn_til_csv:
    @param df_stier_csvfiler:
    @param list_points_to_check:
    @param sti_til_mapper_endelige_filer:
    @param list_excluded_files_2linescalc:
    @param list_valnavn:
    @param sti_values_toplot:
    @param list_0lines_inside:
    @param list_1line_inside:
    @param parameters_varied:
    @param true_lengths:
    @param bool_shall_execute_data_processing:
    @param files_to_skip:
    @param storage_calculation_times:
    @return:
    """
    if bool_shall_execute_data_processing is False:
        return
    time_operation = time.time()
    category = 'data_processing'

    list_values = make_container_diff(mappenavn_til_rs2)

    list_momentum_values = make_container_diff(mappenavn_til_rs2)
    parameter_navn_interpret0 = prep_parameter_navn(parameter_navn_interpret)

    for k, (navn_rs2, navn_csv, excluded_files,
            (points_check_colname, points_to_check), valnavn, (zerolines_colname, _0lines_inside),
            (oneline_colname, _1line_inside)) in \
            enumerate(zip(mappenavn_til_rs2, mappenavn_til_csv, list_excluded_files_2linescalc, list_points_to_check.iteritems(),
                          list_valnavn, list_0lines_inside.iteritems(), list_1line_inside.iteritems())):
        if k in files_to_skip:
            continue
        # element_files_corrupted er definert mtp en treshold for filstørrelse, da de filer hvor feilklikking inntreffer
        # viser ca 1/3 mindre størrelse.
        elements_files_corrupted = get_elements_corrupted_files(df_stier_csvfiler[navn_csv])
        idx0, idx1, idx2 = 0, 0, 0
        true_lengths_copy = true_lengths.copy()
        list_true_lengths = []
        for z, (csv_sti, corrupted) in enumerate(zip(df_stier_csvfiler[navn_csv], elements_files_corrupted)):
            if true_lengths_copy:
                true_len = true_lengths_copy.pop(0)
            else:
                true_lengths_copy = true_lengths.copy()
                true_len = true_lengths_copy.pop(0)
            if corrupted is not None:
                continue
            list_true_lengths.append(true_len)
            query_values = get_query_values(csv_sti, parameter_navn_interpret0)
            #her kan jeg legge inn for mentberegninger
            arclengths_to_plot, values_to_plot = get_values_to_plot(query_values)
            to_plot = get_values_to_plot_arc_and_val(query_values)
            query_positions = get_query_positions(query_values)
            if csv_sti == _0lines_inside[idx0][1]:
                max_val_def = max(values_to_plot[1])
                idx_max_val_def = values_to_plot[1].index(max_val_def)
                arclen_max_val_def = arclengths_to_plot[1][idx_max_val_def]
                sig1_max_val_def = values_to_plot[0][idx_max_val_def]
                values = [max_val_def, sig1_max_val_def, None, None, None, None]
                list_values[k].append(values)
                _0lines_inside.pop(idx0)
                idx0 += 1
            elif csv_sti == _1line_inside[idx1][1]:
                max_val_def = max(values_to_plot[1])
                idx_max_val_def = values_to_plot[1].index(max_val_def)
                arclen_max_val_def = arclengths_to_plot[1][idx_max_val_def]
                sig1_max_val_def = values_to_plot[0][idx_max_val_def]
                values = [max_val_def, sig1_max_val_def, None, None, None, None]
                list_values[k].append(values)
                _1line_inside.pop(idx1)
                idx1 += 1
            else:
                points = points_to_check.pop(idx2)
                idx2 += 1
                values_to_plot_2lines = get_values_quad(to_plot, points, query_positions)
                values = [None, None, values_to_plot_2lines[2], values_to_plot_2lines[5], values_to_plot_2lines[8],
                          values_to_plot_2lines[11]]
                if all(value is not None for value in values_to_plot_2lines):
                    list_values[k].append(values)
        paths_fil_csv = df_stier_csvfiler[navn_csv]
        create_csv_max_values(navn_csv, list_values[k], parameter_navn_interpret, paths_fil_csv,
                              sti_til_mapper_endelige_filer,
                              elements_files_corrupted, valnavn,
                              sti_values_toplot, parameters_varied, list_true_lengths)

        mmf.calculate_computation_time(time_operation, category, storage_calculation_times)
    return