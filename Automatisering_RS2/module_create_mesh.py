import pyautogui as pag
import pandas as pd

from time import sleep
from subprocess import Popen
from Automatisering_RS2 import module_main_functions as mmf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


"""
create mesh opens rs2 of each file and creates the mesh, defined by the settings given in the template files,
succesively.
"""


def create_mesh(mappenavn_til_rs2, mappenavn_til_csv, df_stier_rs2filer, df_stier_csvfiler, path_rs2, time,
                files_to_skip, bool_shall_execute_create_mesh, storage_calculation_times):
    """

    @param mappenavn_til_rs2:
    @param mappenavn_til_csv:
    @param df_stier_rs2filer:
    @param df_stier_csvfiler:
    @param path_rs2:
    @param time:
    @param files_to_skip:
    @param bool_shall_execute_create_mesh:
    @param storage_calculation_times:
    @return:
    """

    if bool_shall_execute_create_mesh is False:
        return

    time_operation = time.time()
    category = 'mesh'

    mmf.procede_script()
    for k, (navn_rs2, navn_csv) in enumerate(zip(mappenavn_til_rs2, mappenavn_til_csv)):
        if k in files_to_skip:
            continue
        for j in range(df_stier_rs2filer.shape[0]):
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            path_fil_csv = df_stier_csvfiler[navn_csv][j]
            if isinstance(path_fil_rs2, str) and isinstance(path_fil_csv, str):
                Popen([path_rs2, path_fil_rs2])
                sleep(5)

                # chooses the rs2 window so hotkeys can be used
                pag.leftClick(927, 490, interval=time[1])
                # create discretization and mesh
                pag.hotkey('ctrl', 'm', interval=time[1])
                # save
                pag.hotkey('ctrl', 's', interval=time[1])
                # close window
                pag.hotkey('alt', 'f4', interval=time[1])

    mmf.calculate_computation_time(time_operation, category, storage_calculation_times)
    return
