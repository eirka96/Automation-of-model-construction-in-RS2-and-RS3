import pandas as pd
import shutil as st
import re
import numpy as np
import time

from Automatisering_RS2.modules_model_construction import module_model_construction_rs2 as mmcr
from Automatisering_RS2 import module_main_functions as mmf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

"""
This module does two things. First of all, it creates the geometry and material allocation of a given model and stores
the geomtrical data of this model needed for later operations in the main file.

Second of all, if called it returnes lists of the stored geometrical data needed in later operations of the main file.
This makes it possible to reuse experiments without doing all the geometry and material allocations.
"""


"""
alter_geometry executes all alterations to be made for each .fea-file. It reads the respective filenames
which consists of the information of the value of each parameter which defines the file. After this, it implements these 
values into the respective fea file by the Open-constructor.

zone is used interchangably with weakness zone
"""


def alter_geometry(zone_angle, x_translation_zone, y_translation_zone, thickness_zone, path_of_rs2_file,
                   list_which_material, _0lines_inside, _1line_inside, _2lines_inside,
                   _excluded_files_2linescalc, iterationnumber, _points_to_check, path_of_csv_file,
                   l_inner_points, _iternumber_0, _iternumber_1, _iternumber_2, x_attribute, num_outerpoints_zone=4,
                   num_lines_zone=2, tunnel_diameter=10, n_points_tunnel_boundary=360, extension_outerboundary=150):
    """

    @param zone_angle:
    @param x_translation_zone:
    @param y_translation_zone:
    @param thickness_zone:
    @param path_of_rs2_file:
    @param list_which_material:
    @param _0lines_inside:
    @param _1line_inside:
    @param _2lines_inside:
    @param _excluded_files_2linescalc:
    @param iterationnumber:
    @param _points_to_check:
    @param path_of_csv_file:
    @param l_inner_points:
    @param _iternumber_0:
    @param _iternumber_1:
    @param _iternumber_2:
    @param x_attribute:
    @param num_outerpoints_zone:
    @param num_lines_zone:
    @param tunnel_diameter:
    @param n_points_tunnel_boundary:
    @param extension_outerboundary:
    @return:
    """

    """
    Data from the .fea gile is extracted and prepared for the alternation proccess.
    """

    # fetches the content of .fea file and store it as a list.
    with open(path_of_rs2_file, 'r') as file:
        data = file.readlines()

    # fetches the key-elements to be used to navigate in the list data. These keywords were found by examining the
    # fea file using notepad++.
    index_material_mesh = data.index("materials mesh start:\n") + 3
    index_boundary1 = data.index("  boundary 1 start:\n") + 6
    points_tunnel_boundary0 = data[index_boundary1:index_boundary1 + n_points_tunnel_boundary].copy()

    # making list of the points defining the tunnel stored as float:
    points_tunnel_boundary = mmcr.prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1)

    # defines which points in tunnel boundary that belongs to a specific mathematical quadrant. There are four in trotal
    fourth_quad = points_tunnel_boundary[0:int(n_points_tunnel_boundary / 4)]
    first_quad = points_tunnel_boundary[int(n_points_tunnel_boundary / 4):int(n_points_tunnel_boundary / 2)]
    second_quad = points_tunnel_boundary[int(n_points_tunnel_boundary / 2):int(n_points_tunnel_boundary * (3 / 4))]
    third_quad = points_tunnel_boundary[int(n_points_tunnel_boundary * (3 / 4)):n_points_tunnel_boundary]

    # saves the categorized points in a list called quad
    quad = (fourth_quad, first_quad, second_quad, third_quad)

    """
    In this section the change in thickness, rotation and translation is executed
    """

    # thickness of weakness zone is changed before translation and rotation of the zone.
    # defines the weakness zone based on thickness and on the intersection between the zone and the outer boundary.
    # the zone is horizontal at first.
    x_right_def_zone = extension_outerboundary
    x_left_def_zone = -extension_outerboundary
    y_top_def_zone = thickness_zone / 2
    y_bot_def_zone = -thickness_zone / 2

    # defines the four points defining the zone. They work as pairs where each pair defines a line. Together, the two
    # lines spans out the zone. In the script they are systemized based on the sequence of points defining the tunnel.
    # There point zero is the point at the bottom of the circle and the sequence goes counter-clockwise.
    # Also, the third value of the lists is set to 1, to include the translation in the matrix equation.

    point_bot_right = [x_right_def_zone, y_bot_def_zone, 1]
    point_top_right = [x_right_def_zone, y_top_def_zone, 1]
    point_top_left = [x_left_def_zone, y_top_def_zone, 1]
    point_bot_left = [x_left_def_zone, y_bot_def_zone, 1]

    # instability occurs if the zone angle is too close [90,180,270,360] for some reason.
    # mmcr.prepare_angel solves that issue by making the angle close to the wanted value.
    # See modules_model_construction line 10 for more.
    zone_angle = mmcr.prepare_angel(zone_angle)
    # converts the zone angle to radians
    zone_angle_rad = np.deg2rad(zone_angle)

    # defines the conjoined translation and rotation matrix in where rotation happens first, then translation, or else,
    # no translation would happen.
    rottrans_matr = np.array([[np.cos(zone_angle_rad), -np.sin(zone_angle_rad), x_translation_zone],
                              [np.sin(zone_angle_rad), np.cos(zone_angle_rad), y_translation_zone]])

    # the rotation of the zone and translation is done simultaniously.
    # After rotation and translation the zone must be extended to intersect the outer boundary.
    if zone_angle != 0:
        # the rotation and translation of zone is done using np.matmul which does matrix product of two arrays
        outerpoint_bot_right0 = np.matmul(rottrans_matr, np.array(point_bot_right))
        outerpoint_top_right0 = np.matmul(rottrans_matr, np.array(point_top_right))
        outerpoint_top_left0 = np.matmul(rottrans_matr, np.array(point_top_left))
        outerpoint_bot_left0 = np.matmul(rottrans_matr, np.array(point_bot_left))

        # the finnished transformed points is categorised into the two line segments
        points_top = [outerpoint_top_right0, outerpoint_top_left0]
        points_bot = [outerpoint_bot_right0, outerpoint_bot_left0]

        # check if zone exeeds the outer boundary, which crashes RS2. If so the code is stopped.
        if mmcr.OuterBoundary.check_points_ob(points_top, points_bot, extension_outerboundary):
            print('Advarsel: svakhetssonen er utenfor de ytre grensene tilhørende modellen. Scriptet ble stanset.')
            quit()
        # the extension of the zone is executed
        outerpoint_top_right, outerpoint_top_left = \
            mmcr.OuterBoundary.find_points_on_outer_boundary(outerpoint_top_right0, outerpoint_top_left0,
                                                             extension_outerboundary, num_lines_zone)
        outerpoint_bot_right, outerpoint_bot_left = \
            mmcr.OuterBoundary.find_points_on_outer_boundary(outerpoint_bot_right0, outerpoint_bot_left0,
                                                             extension_outerboundary, num_lines_zone)
        # checking if the extension is succesfull
        len_topp = np.sqrt(
            (outerpoint_bot_left[0] - outerpoint_bot_right[0]) ** 2 +
            (outerpoint_bot_left[1] - outerpoint_bot_right[1]) ** 2)
        len_bunn = np.sqrt(
            (outerpoint_top_left[0] - outerpoint_top_right[0]) ** 2 +
            (outerpoint_top_left[1] - outerpoint_top_right[1]) ** 2)

        if len_topp < 5 or len_bunn < 5:
            print('Advarsel: svakhetssonens utstrekning er for liten, prøv igjen. Scriptet ble stanset.')
            quit()
    else:
        # defining zone if no rotation, only thickness is changed and true length is added to y,
        # the reason for this is that this situation can not be normalized since an x translation is not possible when
        # zone has no angle. See explaination for the term normalized in main file, line 244.
        outerpoint_bot_right = [x_right_def_zone, y_bot_def_zone + x_attribute]
        outerpoint_top_right = [x_right_def_zone, y_top_def_zone + x_attribute]
        outerpoint_top_left = [x_left_def_zone, y_top_def_zone + x_attribute]
        outerpoint_bot_left = [x_left_def_zone, y_bot_def_zone + x_attribute]

        # check if zone exeeds the outer boundary, which crashed RS2. If so the code is stopped.
        if outerpoint_bot_right[1] < -extension_outerboundary or outerpoint_top_right[1] > extension_outerboundary:
            print('Advarsel: svakhetssonen er utenfor de ytre grensene tilhørende modellen. Scriptet ble stanset.')
            quit()
    # the outer points of weakness zone is stored in a list
    outer_points = [outerpoint_bot_right, outerpoint_top_right, outerpoint_top_left, outerpoint_bot_left]

    """
    It must also be defined inner points of the weakness zone if the zone intersects the tunnel periphery. It will be
    zero, two or four points defined, depending if the none, one or two lineaments defing the zone are intersecting.

    The reason for this is due to RS2. If this is not defined, the material allocation will not work.
    """

    # an object is constructed containing all functions and variables needed to define the inner intersectionpoints
    # of a model. If there are innerpoints, theese are created and implemented in the fea-file in the section regarding
    # the specification of the tunnel boundary. See, the class mmcr.InnerBoundary in modules_model_construction_rs2.py
    # line 38 # for details.
    ib = mmcr.InnerBoundary(num_lines_zone, quad, outer_points, data, n_points_tunnel_boundary,
                            index_boundary1, tunnel_diameter, zone_angle, points_tunnel_boundary,
                            extension_outerboundary)
    if ib.inner_points:
        inner_points = ib.get_points_on_circular_boundary_2()
        ib.set_inner_boundary()
    else:
        inner_points = ib.get_points_on_circular_boundary_2()

    """
    In this section, the outerpoints defining the weakness zone is implemented into the.fea-file in the section 
    regarding the defintion of the outerboundary.
    """

    # the tokens needed to navigate the list data to implement the changes is defined.
    index_boundary1 = data.index("  boundary 1 start:\n") + 6
    index_boundary2 = data.index("  boundary 2 start:\n") + 6
    index_boundary3 = data.index("  boundary 3 start:\n") + 6
    index_boundary4 = data.index("  boundary 4 start:\n") + 6

    # creation of the object implements the changes. The details are given in modules_model_construction.py in the class
    # OuterBoundary in line 344.
    mmcr.OuterBoundary(outer_points, data, index_boundary2, zone_angle, num_outerpoints_zone, extension_outerboundary)

    """
    In this section, the outerpoints defining the weakness zone is implemented into the.fea-file in the section 
    regarding the defintion of the weakness zone. See modules_model_construction class BoundaryLines line 474 
    for details.
    """
    bl = mmcr.BoundaryLines(outer_points, inner_points, index_boundary3, index_boundary4, data, num_lines_zone)
    bl.set_weakness_points()

    """
    In this section the material allocations is done. See modules_model_construction class Materials line 752 
    for details.
    """

    # the updated list of the points defining the tunnel boundary is needed due to creation of new points above.
    points_tunnel_boundary0 = data[index_boundary1:index_boundary1 + ib.n_points_ib].copy()
    # making list of points stored as float:
    points_tunnel_boundary = mmcr.prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1)

    # allocating the materials.
    mls = mmcr.Materials(index_material_mesh, inner_points, extension_outerboundary,
                         num_lines_zone, quad, outer_points, data, n_points_tunnel_boundary, index_boundary1,
                         tunnel_diameter, zone_angle, points_tunnel_boundary, y_translation_zone, x_translation_zone,
                         list_which_material)
    mls.setmaterialmesh()

    """
    In this section the alterations is written into the given models fea-file
    """

    with open(path_of_rs2_file, 'w') as file:
        file.writelines(data)

    """
    in this section, the geometry data needed in later operations of the main file is stored in lists later to be stored
    in csv or pickle format
    """
    if all(points is None for points in inner_points):
        _0lines_inside.append([path_of_rs2_file, path_of_csv_file])
        _iternumber_0.append(iterationnumber)
        _excluded_files_2linescalc.append(iterationnumber)
        # _points_to_check.append(None)
    elif any(points is None for points in inner_points):
        _1line_inside.append([path_of_rs2_file, path_of_csv_file])
        _excluded_files_2linescalc.append(iterationnumber)
        _iternumber_1.append(iterationnumber)
        # _points_to_check.append(None)
    else:
        _2lines_inside.append([path_of_rs2_file, path_of_csv_file])
        _points_to_check.append(inner_points)
        _iternumber_2.append(iterationnumber)
    l_inner_points.append(inner_points)
    return


"""
create_pickle_2lines_info stores the necessary geometry data used by operations succeding ea.execute_model_alteration
It is called from ea.execute_model_alteration in experiment_actions in line 109.

A pickle is a file format created to store python objects in the format of the python language. For example, pandas
datdaframes must be stored in this format if to be used later in another run or other scripts. If the dataframe was
stored in the csv format, the dataframe was altered in a awy that the information was destroyed.
"""


def create_pickle_2lines_info(list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc,
                              list_points_to_check, sti_list_variables_2lines_calculations, mappenavn_til_rs2,
                              list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points):
    iterable = [list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc,
                list_points_to_check, list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points]
    list_of_df_2lines_info, colnames_of_dfs_2lines_info = [], []

    for sti_variables, it in zip(sti_list_variables_2lines_calculations, iterable):
        # list_of_df_2lines_info.append([]), colnames_of_dfs_2lines_info.append([])
        d = {navn.replace('/rs2', ''): i for navn, i in zip(mappenavn_til_rs2, it)}
        df = pd.DataFrame({k: pd.Series(v) for k, v in d.items()})
        df.to_pickle(path=sti_variables)
        list_of_df_2lines_info.append(df), colnames_of_dfs_2lines_info.append(df.head())
    return list_of_df_2lines_info, colnames_of_dfs_2lines_info


"""
gets values of material parameters and geometry for a rs2-model extracted from its filename and calls 
alter_geometry
"""


def alter_model(extension_outerboundary, n_points_tunnel_boundary,
                path_of_rs2_file, path_of_csv_file, df_changing_attributes_rs2files,
                foldername_of_pathcategory, list_which_material, _0lines_inside, _1line_inside, _2lines_inside,
                _excluded_files_2linescalc, _points_to_check, i, j, _iternumber_0, _iternumber_1, _iternumber_2,
                l_inner_points, x_attributes):
    """

    @param extension_outerboundary:
    @param n_points_tunnel_boundary:
    @param path_of_rs2_file:
    @param path_of_csv_file:
    @param df_changing_attributes_rs2files:
    @param foldername_of_pathcategory:
    @param list_which_material:
    @param _0lines_inside:
    @param _1line_inside:
    @param _2lines_inside:
    @param _excluded_files_2linescalc:
    @param _points_to_check:
    @param i:
    @param j:
    @param _iternumber_0:
    @param _iternumber_1:
    @param _iternumber_2:
    @param l_inner_points:
    @param x_attributes:
    @return:
    """
    # fetching which values to be changed for a specific model
    angle = df_changing_attributes_rs2files[foldername_of_pathcategory[i]][j]['v']
    angle = float(angle)
    x_attribute = x_attributes[j]
    y_translation_zone = float(df_changing_attributes_rs2files[foldername_of_pathcategory[i]][j]['y'])
    x_translation_zone = float(df_changing_attributes_rs2files[foldername_of_pathcategory[i]][j]['x'])
    thickness_zone = float(df_changing_attributes_rs2files[foldername_of_pathcategory[i]][j]['m'])

    # function which executes the alterations by changing certain lines of the .fea-files using the Open-constructor
    alter_geometry(angle, x_translation_zone, y_translation_zone, thickness_zone, path_of_rs2_file,
                   list_which_material, _0lines_inside, _1line_inside, _2lines_inside,
                   _excluded_files_2linescalc, i, _points_to_check, path_of_csv_file,
                   _iternumber_0, _iternumber_1, _iternumber_2, l_inner_points, x_attribute,
                   extension_outerboundary=extension_outerboundary,
                   n_points_tunnel_boundary=n_points_tunnel_boundary)
    return


"""
get_parameters_2lines_inside is called if there there are going to be done operations on files that already have their
geometry been defined in an earlier run of the script. For example, if the mesh of the models must be refined, leading
to new calculations and fetching of values with interpret, this function can be called. The geometrical data needed
in the comming operations is stored in pickle-files in the end of alter_geometry.
"""


def get_parameters_2lines_inside(sti_list_variables_2lines_calculations):
    list_of_df_2lines_info = []
    colnames_of_dfs_2lines_info = []
    for sti_variables_2lines in sti_list_variables_2lines_calculations:
        df = pd.read_pickle(filepath_or_buffer=sti_variables_2lines)
        list_of_df_2lines_info.append(df)
        colnames_of_df = df.head()
        colnames_of_dfs_2lines_info.append(colnames_of_df)
    return list_of_df_2lines_info, colnames_of_dfs_2lines_info


"""
execute_model_alteration either sequence through each model and creates them based opn the content of their filenames
calling alter_model, or it retrieves the necessary geometry data for the rest of the operations of the main file calling
get_parameters_2lines_inside.
"""


def execute_model_alteration(ytre_grenser_utstrekning, n_points_tunnel_boundary, overburdens, list_change_fieldstress,
                             mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
                             df_stier_csvfiler, df_endrede_attributter_rs2filer, list_which_material,
                             sti_list_variables_2lines_calculations, x_attributes, len_angle_attributes,
                             bool_shall_execute_model_alteration, files_to_skip, storage_calculation_times):
    """

    @param ytre_grenser_utstrekning:
    @param n_points_tunnel_boundary:
    @param overburdens:
    @param list_change_fieldstress:
    @param mappenavn_til_rs2:
    @param mappenavn_til_csv:
    @param df_stier_rs2filer:
    @param df_stier_csvfiler:
    @param df_endrede_attributter_rs2filer:
    @param list_which_material:
    @param sti_list_variables_2lines_calculations:
    @param x_attributes:
    @param len_angle_attributes:
    @param bool_shall_execute_model_alteration:
    @param files_to_skip:
    @param storage_calculation_times:
    @return:
    """
    if bool_shall_execute_model_alteration is True:
        time_operation = time.time()
        category = 'geometri'

        # x_attributes is used if zone angle is zero and must be repeated as defined under, to work with alter_model
        x_attributes = len_angle_attributes*x_attributes

        # lists to contain geometry data later to be used in data_storage and data_processing
        list_0lines_inside, list_1line_inside, list_2lines_inside, list_iternumber_0, list_iternumber_1, \
            list_iternumber_2, list_excluded_files_2linescalc, list_points_to_check, ll_inner_points = \
            [], [], [], [], [], [], [], [], []
        q = 0
        for k, (navn_rs2, navn_csv, utskrekning, overdekning) in enumerate(zip(mappenavn_til_rs2, mappenavn_til_csv,
                                                                               ytre_grenser_utstrekning, overburdens)):
            if k in files_to_skip:
                continue
            list_0lines_inside.append([]), list_1line_inside.append([]), list_2lines_inside.append([]),
            list_excluded_files_2linescalc.append([]), list_points_to_check.append([]),
            list_iternumber_0.append([]), list_iternumber_1.append([]), list_iternumber_2.append([]),
            ll_inner_points.append([])
            p = 2
            if utskrekning == ytre_grenser_utstrekning[k - 1]:
                q += 1
                overburden = list_change_fieldstress[q - 1]
                if q == 1:
                    print('ferdig å undersøke filer?')
                    mmf.procede_script()

                list_0lines_inside[k], list_1line_inside[k], list_2lines_inside[k], \
                    list_excluded_files_2linescalc[k], list_points_to_check[k], list_iternumber_0[k], \
                    list_iternumber_1[k], list_iternumber_2[k], ll_inner_points[k] = \
                    list_0lines_inside[p], list_1line_inside[p], list_2lines_inside[p], \
                    list_excluded_files_2linescalc[p], list_points_to_check[p], list_iternumber_0[p], \
                    list_iternumber_1[p], list_iternumber_2[p], ll_inner_points[p]

                list_0lines_inside[k] = [[paths[0].replace('od200', 'od{}'.format(overdekning)),
                                          paths[1].replace('od200', 'od{}'.format(overdekning))]
                                         for paths in list_0lines_inside[k]]
                list_1line_inside[k] = [[paths[0].replace('od200', 'od{}'.format(overdekning)),
                                         paths[1].replace('od200', 'od{}'.format(overdekning))]
                                        for paths in list_1line_inside[k]]
                list_2lines_inside[k] = [[paths[0].replace('od200', 'od{}'.format(overdekning)),
                                          paths[1].replace('od200', 'od{}'.format(overdekning))]
                                         for paths in list_2lines_inside[k]]
                for j in range(df_stier_rs2filer.shape[0]):
                    path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
                    path_fil_csv = df_stier_csvfiler[navn_csv][j]
                    if isinstance(path_fil_rs2, str):
                        path_to_copy_rs2 = df_stier_rs2filer['S_bm80_ss1_k1_od200/rs2/'][j]
                        path_to_copy_csv = df_stier_csvfiler['S_bm80_ss1_k1_od200/csv/'][j]
                        st.copyfile(path_to_copy_rs2, path_fil_rs2)
                        st.copyfile(path_to_copy_csv, path_fil_csv)
                key_word = 'field stress:\n'
                for j in range(df_stier_rs2filer.shape[0]):
                    path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
                    if isinstance(path_fil_rs2, str):
                        with open(path_fil_rs2, 'r') as file:
                            data = file.readlines()
                            index_fieldstress = data.index(key_word) + 1
                            data[index_fieldstress] = re.sub(r'^(\s*(?:\S+\s+){5})\S+', r'\1 '
                                                             + str('{}'.format(overburden)), data[index_fieldstress])
                        with open(path_fil_rs2, 'w') as file:
                            file.writelines(data)
            else:
                for j in range(df_stier_rs2filer.shape[0]):
                    path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
                    path_fil_csv = df_stier_csvfiler[navn_csv][j]
                    print(path_fil_rs2)
                    # print(path_fil_csv)
                    if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                        alter_model(utskrekning, n_points_tunnel_boundary,
                                    path_fil_rs2, path_fil_csv, df_endrede_attributter_rs2filer,
                                    mappenavn_til_rs2, list_which_material, list_0lines_inside[k],
                                    list_1line_inside[k], list_2lines_inside[k], list_excluded_files_2linescalc[k],
                                    list_points_to_check[k], k, j, list_iternumber_0[k], list_iternumber_1[k],
                                    list_iternumber_2[k], ll_inner_points[k], x_attributes)
                    else:
                        ll_inner_points[k].append(None)
        list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
            create_pickle_2lines_info(list_0lines_inside, list_1line_inside, list_2lines_inside,
                                      list_excluded_files_2linescalc, list_points_to_check,
                                      sti_list_variables_2lines_calculations, mappenavn_til_rs2,
                                      list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points)
        mmf.calculate_computation_time(time_operation, category, storage_calculation_times)
    else:
        list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
            get_parameters_2lines_inside(sti_list_variables_2lines_calculations)

    return list_of_df_2lines_info, colnames_of_dfs_2lines_info
