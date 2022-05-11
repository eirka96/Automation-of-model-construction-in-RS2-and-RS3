import numpy as np
import itertools
from csv import writer
from sys import exit


def delete_content_csv(csv_paths):
    for path in csv_paths:
        with open(path, 'w', newline='') as file:
            file.truncate(0)
            file.close()
    return


def make_csv_paths(list_iter_ob, path_shell_rs2):
    csv_paths = []
    for i in range(len(list_iter_ob)):
        csv_paths.append(path_shell_rs2.format(list_iter_ob[i], list_iter_ob[i]))
    return csv_paths


def get_range_changing_attributes(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                                  mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio,
                 mektighet_attributes, angel_attributes, y_attributes, x_attributes]
    for idx, iter_object in enumerate(iter_list):
        if not isinstance(iter_object, (list, float, int, tuple, str)) or (isinstance(iter_object, (list, tuple)) and
                                                                           len(iter_object) != 3):
            print(
                "Advarsel!!!!! Input må være enten type int, float, list eller tupple. Dessuten må list eller tuple ha "
                "lengde 3 og være på formen [start_element, slutt_element, steg for element]")
            exit()
        elif isinstance(iter_object, (int, float, str)):
            iter_list[idx] = [iter_object]
        else:
            iter_list[idx] = np.arange(iter_object[0], iter_object[1], iter_object[2]).tolist()
    iter_list.insert(3, overburden)
    return iter_list[0], iter_list[1], iter_list[2], iter_list[3], iter_list[4], iter_list[5], iter_list[6], iter_list[7]


def get_shape_matrix(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                     mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                 mektighet_attributes, angel_attributes, y_attributes, x_attributes]
    shape_matrix_list = []
    for iter_object in iter_list:
        if isinstance(iter_object, (int, float, str)):
            shape_matrix_list.append(1)
        else:
            shape_matrix_list.append(len(iter_object))
    return shape_matrix_list


def which_overburden(element):
    if element == 25:
        return 'ob_25'
    elif element == 100:
        return 'ob_100'
    elif element == 200:
        return 'ob_200'
    elif element == 300:
        return 'ob_300'
    elif element == 500:
        return 'ob_500'
    elif element == 800:
        return 'ob_800'
    elif element == 1200:
        return 'ob_1200'
    else:
        return None


def get_ob_index(element):
    switcher = {
        'ob_25': 0,
        'ob_100': 1,
        'ob_200': 2,
        'ob_300': 3,
        'ob_500': 4,
        'ob_800': 5,
        'ob_1200': 6,
    }
    return switcher.get(which_overburden(element), None)


def set_model_csv_attributes(paths_csv_attributes, rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                             mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    rmm, wzm, sr, ob, m, v, y, x = get_range_changing_attributes(rock_mass_material, weakness_zone_material,
                                                                 stress_ratio,
                                                                 overburden, mektighet_attributes, angel_attributes,
                                                                 y_attributes, x_attributes)
    shape_matrix_list = get_shape_matrix(rmm, wzm, sr, ob, m, v, y, x)
    shape_matrix_list.pop(3)
    for o in ob:
        with open(paths_csv_attributes[get_ob_index(o)], 'w', newline='') as file:
            writer_object = writer(file, delimiter=";")
            list_data = [['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']]
            for idx in itertools.product(*[range(s) for s in shape_matrix_list]):
                rmm_i, wzm_i, sr_i, m_i, v_i, y_i, x_i = idx
                list_data.append(['{}'.format(rmm[rmm_i]), '{}'.format(wzm[wzm_i]),
                                  '{}'.format(sr[sr_i]), '{}'.format(o),
                                  '{}'.format(m[m_i]), '{}'.format(v[v_i]),
                                  '{}'.format(y[y_i]), '{}'.format(x[x_i])])
            writer_object.writerows(list_data)
            file.close()
    return


def set_model_csv_attributes_batch(path_csv_attributes, rock_mass_material, weakness_zone_material, stress_ratio,
                                   overburden, mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    rmm, wzm, sr, ob, m, v, y, x = get_range_changing_attributes(rock_mass_material, weakness_zone_material,
                                                                 stress_ratio,
                                                                 overburden, mektighet_attributes, angel_attributes,
                                                                 y_attributes, x_attributes)
    shape_matrix_list = get_shape_matrix(rmm, wzm, sr, ob, m, v, y, x)
    with open(path_csv_attributes, 'w', newline='') as file:
        writer_object = writer(file, delimiter=";")
        list_data = [['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']]
        for idx in itertools.product(*[range(s) for s in shape_matrix_list]):
            rmm_i, wzm_i, sr_i, ob_i, m_i, v_i, y_i, x_i = idx
            list_data.append(['{}'.format(rmm[rmm_i]), '{}'.format(wzm[wzm_i]),
                              '{}'.format(sr[sr_i]), '{}'.format(ob[ob_i]),
                              '{}'.format(m[m_i]), '{}'.format(v[v_i]),
                              '{}'.format(y[y_i]), '{}'.format(x[x_i])])
        writer_object.writerows(list_data)
        file.close()
    return

