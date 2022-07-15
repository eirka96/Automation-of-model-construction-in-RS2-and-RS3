"""
Import of modules created for this project is the ones starting with from.
Important note, these modules is again using modules created by others in conjunction with own modules etc.
So, thanks to all that contributes with useful tools on an open-source basis!!!! Without the python community
this project would not have been possible.
"""
import pandas as pd
import time

from Automatisering_RS2 import module_main_functions as mmf
from Automatisering_RS2.mouse_tracking import mouse_tracker as mt
from Automatisering_RS2 import module_plan_experiment as mpe
from Automatisering_RS2.modules_model_construction import module_execute_model_alteration as mema
from Automatisering_RS2 import module_create_mesh as mcm
from Automatisering_RS2 import module_calculate as mcal
from Automatisering_RS2 import module_store_data as msd
from Automatisering_RS2 import module_execute_data_processing as medp

"""
This is the main file of the automation script made automize the modelling process of the 2-dimensional FEM programme
RS2 by RocScience Inc.

It was created as an integral part of the master thesis: "" written by Eirik Kaasbøll Andresen the spring 2022. This
Thesis is available at NTNU Open. Rweading of the thesis will give the context of this script and may give the reader
new ideas thqat can maker use of this script and lead to further developments. You can get the script from my github
account.

The main file works as a hub and is putting togehter the contribution of several scripts developed in this project. The 
scripts is categorized and is developed to face certain needs.

If a certain script or module is not used for a paricular reason, it is commented out.
The script is designed with a memory storage solution. If one part of the script is finnished, all information is needed
stop the script, for then to comment out certain blocks and keep on from the point the script was stopped. 

However, this script is not optimized for being userfriendly. So, feel free to contact me if there are any questions.

BR
    Eirik Kaasbøll Andresen - the developer of this script.


PS
    All communinication through monitor and some variables are written in Norwegian, so have fun with google translate 
    and enjoy some words and sentences of this beautful language!
"""


"""
This is the controll panel stearing which operations to be done when running the script. If all is False, this 
script does nothing. If no changes is made to input parameters defining the models there is no need to go further.

#1 is True if the project is moved over to another screen. If there are difference from the new screen compared to old
this will mean that the mouse coordinates must be updated.

#2 is True if thwe mouse coordinates must be redefined

#3 is True if a new project is to be made. This will set up the folder strucure needed

#(4 to 10) with name bool_shall_execute_... is used to turn on and of different operations of the script in where all
seqence through all models of the experiment and does different tasks.

#4 True turns on the model alteration process
#5 True True turns on the create mesh process
#6 True turns on the calculation process
#8 True turns on the data storing process
#10 True turns on the first data processing process, in where the second data processing is done using Excel, 
see thesis.

#7 If true, the function calculate pauses after the creation of the log file analysis, so that the user can
   check the quality.

#9 is False if data storing is done a second time or more. This is due to how rs2 interpret works. The second time it is
run, it opens directly wit total deformation as parameter. However, the first parameter stored must be sigma 1.

NB!!! If there are done any changes to the template files on which all the models is based, all the parameters 
between #4 - 10 must  set to True. This is all from changing the parameters defining the calculation 
(iteration, tolerance), mesh, material parameterers and more.

Another important note. If the script must be stopped after for instance mesh creation this is fine. Just turn the 
processes already executed to False and the scripts run from where you stopped.

Furthermore, let say there was something going wrong with the mouse operations of the data storage after completing
overburden 100, 200, and 500, where the bug happened when overburden 800. It is not necessary to do the entire 
data storage process again. Using files_to_skip enables the user to controll which clusters of files to be operated
by refering to overburdens, which is the coarsest sorting defined in this thesis. 
An example; files_to_skip = [0,1,2] skips the overburdens 100, 200, 300 of the list 
overburdens = [100, 200, 300, 500, 800, 1200]. overburdens is allocated in line 220.

However, files_to_skip cannot be used on the function calculate from module_calculate. This is not as big issue since
calculate for the most case uses rs2's own batch functionality. Just set #4,5 and 6 to false. Open rs2 calculate and
choose the files that needs to be calculated. And then run the rest when the calculations are finnished. It is
adviced to check the file containing log-files exceeding the given tolerance, to see if the calculations are reliable by
setting #7 to true.

For yes, the calculate operation ends with analysing all the log-files created by rs2 compute after each completed 
calculation. If there is found tolerances greater than a certain error set by the user, it stores the path of these 
log-files, and the user can check if the differences are problematic. 
"""
#1
bool_know_size_monitor = False
#2
bool_shall_reedit_mouse_coordinates = False
#3
bool_create_new_project = False

#4 to 10 Settings for the operations
bool_shall_execute_model_alteration = False

bool_shall_execute_create_mesh = False

bool_shall_execute_calculate = False
bool_stop_to_check_logs = False

bool_shall_execute_data_store = False
bool_is_first_time_execute_data_store = False

bool_shall_execute_data_processing = False

#11 skip overburdens
files_to_skip = []


"""NB!!!!!!!!!!!
It two functions in the modules created that must be updated if there are changes in 
the setup of the sensitivity experiment. The functions are:

    which_overburden and get_ob_index in module_plan_experiment.py, in where changes in overburden values 
    must be implemented.
    
"""

"""
It will be calculated computation time of each operation seperatly, due to the script is forced to take break
two times. 

The first break is when the quality of the models is to be checked. There are some few bugs in the material allocation
which must be attoned for. It is only necessary to check the models of overburden 100 and 200. The rest is based 
on the model of overburden 200 in where the only difference is the overburden. The differnece betweeen overburden 100
and 200 is the outerboundary. Thus, the two models experience differneces in their bugs. It is not knwon why the bugs
exist, however it does not affect many models.

The second break is under calculations. The reason for this is that there appeared some complications with rs2 compute.
It must be implemented the path of where rs2 compute finds its data. It is not done now due not having time, but it is
not a complicated thing to implement.

Also, due to symmetry reasons it was only necessary to caclulate for angles between 45 to 90 degrees. So, the problems
faced with the material allocations is more severe if the angles are not between this range. If the script is to be
used for more complex purposes, this problem must be resolved. It is not known why this occur at this stage.
"""

"""
This aks the user if the programme should be run. If not true, the script is exited.
"""

command = mmf.procede_script()

if command == 'j':
    """
    This starts the timer used to calculate the running time of the entire script.
    This will include the time used to check models and the delay if the user do not detect early enough that the 
    calculation is over.
    """
    time_start = time.time()

    """
    Settings for displaying panda dataframes is set. This helped the workflow quit a bit.
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', -1)

    """
    Do you want to know the size of the monitor, set bool_know_size_monitor = True in controll panel line 86. 
    This must be known to check if the mouse coordinates must be redefined if a ne sreen is to be used.
    """
    mmf.get_screen_width(bool_know_size_monitor)

    """
    liste_stier_PycharmProjects_automatisering contains the paths of the csv containing all paths used for a range
    of purposes of this script, and a path to
    """
    """
    main_stringobjects consist  all paths necessary to be defined for the script to run given by a list
    of paths with metadata taken from liste_stier_PycharmProjects_automatisering
    """
    main_stringobjects = pd.read_csv(r'C:\temp\thesis\eksperimenter\mektighet_1'
                                     r'\base_modeler\Pycharm_automatisering'
                                     r'\liste_stier_PycharmProjects_automatisering.txt',
                                     sep=';')
    """ 
    mt.mouse_tracker updates mouse operations if neccessary, if that the case,
    bool_shall_reedit_mouse_coordinates = True
    """
    mt.mouse_tracker(main_stringobjects['object'][7], bool_shall_reedit_mouse_coordinates)

    """
    This part defines the input parameters used in the numerical models.
    
    the plan_experiment module (shortened: pe) detects which defined parameters that is to be static and which that is
    to be dynamic.
    
    Then it creates the ranges of each parameter. These parameters is later used to define the material behaviour and
    geometry of the models.
    """

    # defines some general aspects regarding calculation behaviour used by rs2 compute,
    tolerance = 0.001
    maxiter = 10000

    # defines parameters regarding the output values to be stored in store_data function
    ant_parametere_interpret = 2
    parameter_navn_interpret = ['sigma 1:', 'total deformasjon:', 'end']  # also used in execute_data_processing

    # defines two parameters regarding the dynamic parameters of this experiment
    parameters_varied = ['od', 'v', 'x']  # used in execute_data_processing
    list_change_fieldstress = [300, 500, 800, 1200]  # used in execute_model_alteration

    """  
    These parameters defines the most central parameters describing geometry, stress situation and material parameters
    In this script, the shape of tunnel and material parameters is equal for all models, so these parameters is only
    set in the template files in which the models of the experiment is based. Thus, it is only stress, thickness of
    zone, angle of zone, and translation of zone that are implemented here. It would be possible to include material
    changes in the script at a later stage.
    
    Also, in the thesis, the thickness is only changed when a new experiment is done, just to reduce the size of each
    dataset.

    The filenames of the fea files is defined by the parameters below.
    The filenames are central in the implementation of the script for two reasons:
    1: To make it easy to differ the files from each other
    2: To let the script know which values needed to construct the varied geometry and stress
    
    The structure of the filenames is as follows (NB! Norwegian acronyms):
    S_bm80_ss1_k1_od500_m4_v22.5_x0_y0. In where,
    
    S (sirkulær): circular tunnel shape,
    bm (bergmassekvaliteten): rock mass quality given by GSI
    ss (svakhetssone): material quality of zone given by GSI (in the thesis it is given by mohr-columb parameters
                                                               , so the name is somewhat misleading)
    k: constant for the isotropic ratio of vertical to horizontal stress,
    od (overdekningen): the overburden,
    m (mektigheten): thickness of zone,
    v (vinkel): angle of zone,
    x: horizontal translation of zone,
    y: the vertical translation of zone.


    
    NB!!!!!! 
    The y_attributes is not used. It was, during the method development of the thesis, realised that the 
    radial distance was the most practical to use, not x and y.
    Thus, y is 0 because it is not used, and x_attributes will be normalised later in script. For instance,
    x = [0, 0, 0.25, 0.5, 0.75, 1, 2, 3, 4, 4.5, 5, 5.5, 5.75, 6, 7, 8, 9, 10, 11, 13, 15, 20], is the magnitude
    of the radial lengths, to be normalized later.
    Normalized: 
    It is the shortest distance from tunnel centre to zone we want to define, it is a radial vector which has the same 
    magnitude for all angles of the zone, and is same for all thicknesses too since it is the lineament closest to the 
    zone we are measuring from. Pythagoras is used to express this radial distance with its x-value, 
    which can be done since the shortest distance is the normal normal to the lineamnet of the zone intersecting the 
    tunnel centre. 
    
    To conclude, the x-values is later normalised using pythagoras to transform the radial distance. 
    And y is kept to zero.
    This is done in set_model_csv_attributes_batch from module_plan_experiment, where all the model names of the
    experiment is defined. Thus the x-value will be dependent on the zone angle.
    """

    rock_mass_material, weakness_zone_material, stress_ratio, overburdens, thickness_attributes, angle_attributes, \
        y_attributes, x_attributes = 80, 1, 1, [100, 200, 300, 500, 800, 1200], \
        4, [45, 52.5, 60, 67.5, 75, 82.5, 90], 0, \
        [0, 0, 0.25, 0.5, 0.75, 1, 2, 3, 4, 4.5, 5, 5.5, 5.75, 6, 7, 8, 9, 10, 11, 13, 15, 20]

    # True lengths is the magnitude of distance between tunnel centre and zone centre
    true_lengths = [x + thickness_attributes / 2 if i > 0 else x for i, x in enumerate(x_attributes)]

    # list contains the length of the sides of the quadratic outer boundary
    ytre_grenser_utstrekning = [100, 150, 150, 150, 150, 150]

    # the number of points defining the tunnel boundary of the model. For the script to function properly,
    # it must be possible to divide it by 4. The high number is due to it increases the accuracy around tunnel
    # periphery.
    n_points_tunnel_boundary = 360

    # this list defines the values for material allocation. 15 is weakness zone material and 16 is the rock mass
    # the smallest lsit element refers to one geometrical element of a model, and the two numbers refers to before exc
    # and after excavation respectively.
    # there are four scenarios:
    # 1:The zone do not cross tunnel at all.   -> 4 geometrical elements, excavation throug rock mass
    # 2:The zone is thicker than tunnel diameter and completely submerges the tunnel  -> 4 geometrical elements,
    #                                                                                     excav through weaknes zone
    # 3:Part of the zone cross tunnel -> 5 elements
    # 4:whole zone cross tunnel but is thinner than tunnel diameter -> 7 elements
    list_which_material = [[[[15, 15], [15, 15], [16, 16], [16, 0]], [[15, 15], [15, 15], [16, 16], [15, 0]]],
                           [[15, 15], [15, 15], [15, 0], [16, 0], [16, 16]],
                           [[15, 15], [15, 15], [15, 0], [15, 0], [16, 16], [16, 16], [16, 0]]]

    # the names of the columns of the parameters written to the csv containing the first round processed data, see
    # discussion in thesis for what this means
    valnavn = ['file_name', 'true_lengths', 'od', 'v', 'x', 'sigma 1, max', 'totaldeformasjon, max',
               'quad_high - sigma 1, inbetween', 'quad_high - totaldeformasjon, inbetween',
               'quad_low - sigma 1, inbetween', 'quad_low - totaldeformasjon, inbetween']
    list_valnavn = []
    list_valnavn += 7 * [valnavn]

    # this parameter contains the path to csv containing the descripton of variables of each model, as discussed in
    # line 217.
    path_csv_parameter_verdier_fil = main_stringobjects['object'][0]

    # set_model_csv_attributes_batch interprets the values given in line 267 and creates a csv file describing
    # the definition of each model of the experiment.
    number_of_files = mpe.set_model_csv_attributes_batch(path_csv_parameter_verdier_fil, rock_mass_material,
                                                         weakness_zone_material, stress_ratio, overburdens,
                                                         thickness_attributes, angle_attributes, y_attributes,
                                                         x_attributes)

    """
    In this section rest of paths given in main_stringobjects is allocated. They are explained as they come up.
    """

    # this path points to the csv containing the parameters describing the foldernames in where the results are stored,
    # categorized regarding overburden. The experiments are categorized regarding thickness of zone
    path_csv_parameter_verdier_mappe = main_stringobjects['object'][1]

    # shell for the fea models and the csv containg the results repectively.
    paths_shell_rs2 = main_stringobjects['object'][2]

    # paths of the programmes to be executed in the script:
    path_rs2 = main_stringobjects['object'][3]
    path_rs2_compute = main_stringobjects['object'][4]
    path_rs2_interpret = main_stringobjects['object'][5]

    # path to csv containing mouse coordinates
    sti_koordinater_mus = main_stringobjects['object'][6]

    # path for folder to conmtain the fea files
    sti_til_mappe_for_arbeidsfiler = main_stringobjects['object'][7]
    # path for folder to contain the folders that containes the categorized result files
    sti_til_mapper_endelige_filer = main_stringobjects['object'][8]

    # sti_csv_gamle_rs2stier og sti_csv_gamle_csvStier:
    # is the paths for the csv's containing the paths of the fea files and result csv files from the last run.
    sti_csv_gamle_rs2stier = main_stringobjects['object'][9]
    sti_csv_gamle_csvstier = main_stringobjects['object'][10]

    # sti_list_variables_2lines_calculations: a list containing the paths of the geometrical data needed for the
    # script to work without defining the geometri of all files each time.
    sti_list_variables_2lines_calculations = [main_stringobjects['object'][11], main_stringobjects['object'][12],
                                              main_stringobjects['object'][13], main_stringobjects['object'][14],
                                              main_stringobjects['object'][15], main_stringobjects['object'][16],
                                              main_stringobjects['object'][17], main_stringobjects['object'][18],
                                              main_stringobjects['object'][19]]

    # sti_tolerance_too_high: path to csv containing the list of log-files with tolerance exceeded
    sti_tolerance_too_high = main_stringobjects['object'][21]

    # sti_values_toplot: paths containing the first round of processed data as described in the thesis.
    sti_values_toplot = main_stringobjects['object'][22]

    # storage_calculation_times contains the path in where the caclulation times of the entire script and each
    # operation is stored. It is emptied for each run, so, if the calculation time of each run is to be stored, do
    # that in another file
    storage_calculation_times = main_stringobjects['object'][23]

    """
    the coordinates of the mouse operations is fetched here. The colnames is also defined.
    """
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    navn_kol_df_koord_mus = ['Handling', 'x', 'y']

    """
    paths to the template files is defined
    """
    sti_kildefil_rs2, sti_kildefil_csv = mmf.get_file_paths_batch(paths_shell_rs2, path_csv_parameter_verdier_fil)

    """
    create_work_and_storage_folders
    """
    mmf.create_work_and_storage_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)

    """
    mappenavn_til_rs2/csv: containes the column names of df_stier_rs2/csvfiler
    """
    mappenavn_til_rs2, mappenavn_til_csv = mmf.get_name_folders(sti_til_mapper_endelige_filer)
    df_filnavn_rs2, df_filnavn_csv = mmf.make_file_name(path_csv_parameter_verdier_fil)

    """
    get file paths of fea-files and csv to store ecxcavation query data. If bool_create_new_project True, old content is
    deleted and new files and folder system is created, if False the olde ystem is kept and the file paths is fetched.
    The fea files, if bool_create_new_project True, is created by copying the template files.
    """

    df_stier_rs2filer, df_stier_csvfiler = \
        mmf.get_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2,
                         sti_kildefil_csv, sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier,
                         path_csv_parameter_verdier_mappe, ytre_grenser_utstrekning,
                         bool_create_new_project)

    """
    df_endrede_attributter_rs2filer is dataframe containing the values defining all the models used in the geometry 
    construction. The columns are given by the overburdens.
    """

    df_endrede_attributter_rs2filer = mmf.get_changing_attributes(df_stier_rs2filer, mappenavn_til_rs2)

    """
    used by autogui processes to define how long the script shall wait before next operation is initiated. Given in
    seconds. Important to ensure that one command is completed before the next arrives. See, thesis for a more 
    thorough description.
    """
    time0 = [0, 0.7, 1, 2, 5]

    """
    the geometries of fea models is created, or if bool_shall_execute_model_alteration is False, necessary 
    geometry data is fetched from pickle-files
    """
    #
    list_of_df_2lines_info, colnames_of_dfs_2lines_info = \
        mema.execute_model_alteration(ytre_grenser_utstrekning, n_points_tunnel_boundary, overburdens,
                                      list_change_fieldstress,
                                      mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer,
                                      df_stier_csvfiler, df_endrede_attributter_rs2filer, list_which_material,
                                      sti_list_variables_2lines_calculations, x_attributes.copy(),
                                      len(angle_attributes), bool_shall_execute_model_alteration, files_to_skip,
                                      storage_calculation_times)

    # geometrical data used in execute_data_storage and execute_data_processing
    list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc, list_points_to_check, \
        list_iternumber_0, list_iternumber_1, list_iternumber_2, ll_inner_points = \
        list_of_df_2lines_info[0], list_of_df_2lines_info[1], list_of_df_2lines_info[2], list_of_df_2lines_info[3], \
        list_of_df_2lines_info[4], list_of_df_2lines_info[5], list_of_df_2lines_info[6], list_of_df_2lines_info[7], \
        list_of_df_2lines_info[8]

    """
    her lages diskretisering og mesh til alle modellene
    """

    mcm.create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time0,
                    files_to_skip, bool_shall_execute_create_mesh, storage_calculation_times)

    """
    her kjøres alle kalkulasjonene, med en dynamisk while-løkke slik at når alle kalkulasjonene er ferdig, 
    så fortsetter scriptet. Det er viktig å sørge for at rs2_compute allerede finner den mappen som filene ligger i.
    """

    mcal.calculate(path_rs2_compute, time0, df_filnavn_rs2, sti_til_mappe_for_arbeidsfiler, sti_tolerance_too_high,
                   tolerance, number_of_files, bool_shall_execute_calculate, df_koordinater_mus, navn_kol_df_koord_mus,
                   bool_stop_to_check_logs, storage_calculation_times)

    """
    åpner interpret, der alle resultater som skal benyttes hentes ut og lagres i csv-format
    """

    msd.store_data(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2_interpret,
                   df_koordinater_mus, navn_kol_df_koord_mus, ant_parametere_interpret,
                   parameter_navn_interpret, time0, ll_inner_points, bool_is_first_time_execute_data_store,
                   bool_shall_execute_data_store, files_to_skip, storage_calculation_times)

    """
    here the first processing of data, as explained in the thesis in page , is executed and the fetched data is stored
    in csv-files
    """

    medp.execute_data_processing(parameter_navn_interpret, mappenavn_til_rs2, mappenavn_til_csv,
                                 df_stier_csvfiler, list_points_to_check, sti_til_mapper_endelige_filer,
                                 list_excluded_files_2linescalc, list_valnavn, sti_values_toplot, list_0lines_inside,
                                 list_1line_inside, parameters_varied, true_lengths, bool_shall_execute_data_processing,
                                 files_to_skip, storage_calculation_times)

    category = 'end of script'
    # this will only be calculated if the script is not interrupted
    mmf.calculate_computation_time(time_start, category, storage_calculation_times)
    # if so, add the time used for each operation, which will give a good estrimate of the total computation time.
