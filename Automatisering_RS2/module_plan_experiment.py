import numpy as np
import itertools
from csv import writer
from sys import exit

"""
This modulet is made to detect which defined parameters that is to be static and which to be dynamic, create the
ranges of each parameter, for then to create a set of values defining each model which is stored in a csv-file.

This script is called by the main file

"""

"""
This function gets the range of each parameter. If the range is greater than two it is dynamic, is it one it is static,
and is it zero it is not included. This is the function that is doing the detection work.
It is called in the function set_model_csv_attributes below
"""


def get_shape_matrix(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                     thickness_attributes, angle_attributes, y_attributes, x_attributes):
    """

    @param rock_mass_material:
    @param weakness_zone_material:
    @param stress_ratio:
    @param overburden:
    @param thickness_attributes:
    @param angle_attributes:
    @param y_attributes:
    @param x_attributes:
    @return:
    """
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                 thickness_attributes, angle_attributes, y_attributes, x_attributes]
    shape_matrix_list = []
    for iter_object in iter_list:
        if isinstance(iter_object, (int, float, str)):
            shape_matrix_list.append(1)
        else:
            shape_matrix_list.append(len(iter_object))
    return shape_matrix_list


"""
This function gets the ranges of the variables consisting of minimum a non-zero value. With one value this value is 
put into a vector with length 1. If two or more values a list is created out of the iter_object which must consist of
three values: (a)start value, (b) end value, and (c) the incremental step. 
It is calles in the function set_model_csv_attributes below
"""


def get_range_changing_attributes(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                                  thickness_attributes, angle_attributes, y_attributes, x_attributes):
    """

    @param rock_mass_material:
    @param weakness_zone_material:
    @param stress_ratio:
    @param overburden:
    @param thickness_attributes:
    @param angle_attributes:
    @param y_attributes:
    @param x_attributes:
    @return:
    """
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio,
                 thickness_attributes, angle_attributes, y_attributes, x_attributes]
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

    return iter_list[0], iter_list[1], iter_list[2], iter_list[3], iter_list[4], iter_list[5], iter_list[6], \
        iter_list[7]


"""
The two functions below is intertwined. Together they provide an integer that represents an overburden(ob) value. 
0 is ob 25m and 6 is ob 1200m. 

!!!!!!!!!!Thus, this must be updated if there are changes in which overburdens to be modelled!!!!!!!!!!!!!!!

get_ob_index is included in the function set_model_csv_attributes below
"""


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


"""
Add it is an iterator class. Purpose: iterate over list containing the distance between centre zone and 
centre of tunnel and add the half of the thickness of zone such that the lineament closest to tunnel centre is
always on the same spot of a given distance for any thicknesses. Used by get_x_distance below.

Important:
Sentinel: marks end of object and is allocated sentinel = object() if nothing else is defined. Do not change this if 
not being sure about it. 
"""


class AddIt:

    def __init__(self, iter_object, mektighet, sentinel=object()):
        self.count = 0
        self.len_iter_object = len(iter_object)
        self.iter_object = iter_object
        self.mektighet = mektighet
        self.sentinel = sentinel

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.len_iter_object:
            return self.sentinel
        if self.count == 0:
            ret = self.iter_object[self.count]
        else:
            ret = self.iter_object[self.count] + self.mektighet / 2
        self.count += 1
        return ret

    __call__ = __next__


"""get_x_distance uses add it class to iterate over the distances given from the experiment setup, leading to proper
changes. The reason is given in the description of the class. This function is used by set_model_csv_attributes_batch
below.
"""


def get_x_distance(normalized_distance_list, zone_angle, mektighet):
    zone_angle = np.deg2rad(zone_angle)
    sentinel = object()
    ai = AddIt(normalized_distance_list, mektighet, sentinel)
    x_distance_list = []
    for i in iter(ai, sentinel):
        x_distance_list.append(round(i / np.sin(zone_angle), 2))
    return x_distance_list


"""
This function writes the set of values defining each modeland writes it to a specified csv-file.
"""


def set_model_csv_attributes_batch(path_csv_attributes, rock_mass_material, weakness_zone_material, stress_ratio,
                                   overburden, thickness_attributes, angle_attributes, y_attributes, x_attributes):
    # rmm, wzm, sr, ob, m, v, y, x = get_range_changing_attributes(rock_mass_material, weakness_zone_material,
    #                                                              stress_ratio,
    #                                                              overburden, thickness_attributes, angle_attributes,
    #                                                              y_attributes, x_attributes)
    rmm, wzm, sr, ob, m, v, y, x = [rock_mass_material], [weakness_zone_material], [stress_ratio], overburden, \
                                   [thickness_attributes], angle_attributes, [y_attributes], x_attributes
    shape_matrix_list = get_shape_matrix(rmm, wzm, sr, ob, m, v, y, x)
    number_of_files = 0
    with open(path_csv_attributes, 'w', newline='') as file:
        writer_object = writer(file, delimiter=";")
        list_data = [['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']]
        for idx in itertools.product(*[range(s) for s in shape_matrix_list]):
            rmm_i, wzm_i, sr_i, ob_i, m_i, v_i, y_i, x_i = idx
            x_true = get_x_distance(normalized_distance_list=x.copy(), zone_angle=v[v_i], mektighet=m[m_i])
            list_data.append(['{}'.format(rmm[rmm_i]), '{}'.format(wzm[wzm_i]),
                              '{}'.format(sr[sr_i]), '{}'.format(ob[ob_i]),
                              '{}'.format(m[m_i]), '{}'.format(v[v_i]),
                              '{}'.format(y[y_i]), '{}'.format(x_true[x_i])])
            number_of_files += 1
        writer_object.writerows(list_data)
        file.close()
    return number_of_files
