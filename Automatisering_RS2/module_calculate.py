import pyautogui as pag
import pandas as pd
import re
from time import sleep
from subprocess import Popen
import psutil


from Automatisering_RS2 import module_main_functions as mmf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

"""
get_files_unsuc_tolerance iterates over the log files created after each calculated fea-file, and stores the filenames
of log-files in where the tolerance is not below the limit set by the user. These filenames is stored in a csv file
set by the user. It is used by the function ea.calculate in experiment_actions line 148.
"""


def get_files_unsuc_tolerance(path_arbeidsfiler, list_navn_modell, path_store_unsuc_tol_models, tolerance):
    path_arbeidsfiler = mmf.alternate_slash([path_arbeidsfiler])[0]
    file_suffix = '.log'
    list_unsucsesful_tolerance = []
    subs_tol = 'Tolerance:'
    for navn in list_navn_modell:
        navn = navn.replace('.fea', '')
        check_path = path_arbeidsfiler+'/'+navn+file_suffix
        with open(check_path, 'r') as file:
            data = file.readlines()
        list_tol = [line for line in data if subs_tol in line]
        plist = []
        for line in list_tol:
            p = re.findall(r"([-+]?(?:\d*\.\d+[Ee]?[+-]?\d*\b(?!:))|[-+]?(?:\d*[Ee]?[+-]?\d*\b(?!:)))", line)[1]
            plist.append(p)
        list_tol = plist.copy()
        list_tol = [float(tol) for tol in list_tol if float(tol) > tolerance]
        if list_tol:
            list_unsucsesful_tolerance.append(check_path)

    with open(path_store_unsuc_tol_models, 'w') as file:
        file.writelines([f"{var1}\n" for var1 in list_unsucsesful_tolerance])
    return


"""
The three next functions is used to automize the calculation process. When the calculations is over, the main file
is allowed to continue with the next line.
"""

"""RS2 Calculate, with filename 'feawin.exe', used to get its process data."""


"""
This function opens RS2 Compute, opens the files to be calculated in RS2 Compute, executes calculations, and lastly,
tracks the cpu usage; when below 5 percent it lets the main script continue whit the next line
"""


def automation_actions_calculation(number_of_files, sti_til_mappe_for_arbeidsfiler, coordinate_rs2_compute,
                                   name_col_df_mouse, time=None, i=0):
    # if there is not defined a vector of time increments it is set to be time_list which is allocated on top of this
    # file.
    if time is None:
        time = mmf.get_time_increments()

    # sends the path of the workfolder to clipboard
    mmf.copy2clip(sti_til_mappe_for_arbeidsfiler)

    # For some reason rs2 can only add roughly 600 files at a time, thus since the thesis has 924 models for one
    # thickness, the process must be done twice. If the models for one experiment exceeds 1200 this function must
    # be reedited.
    num_first_batch = round(number_of_files/2)
    num_second_batch = number_of_files-num_first_batch+1

    # opening the workfolder
    pag.hotkey('alt', 'd', interval=time[2])
    pag.hotkey('ctrl', 'v', interval=time[2])
    # the first opening of files begin
    sleep(5)
    pag.press('enter', interval=time[1])
    sleep(5)
    pag.press('tab', presses=4, interval=time[2])
    pag.keyDown('shiftleft')
    pag.keyDown('shiftright')
    pag.press('down', presses=num_first_batch)
    pag.keyUp('shiftleft')
    pag.keyUp('shiftright')
    sleep(5)
    pag.press('enter', interval=time[1])
    # the first openings of files end
    sleep(60)
    # second openings of files begin
    pag.press('enter', interval=time[3])
    pag.keyDown('shiftleft')
    pag.keyDown('shiftright')
    pag.press('tab', presses=2, interval=time[1])
    pag.keyUp('shiftleft')
    pag.keyUp('shiftright')
    pag.press('down', presses=num_first_batch)
    pag.keyDown('shiftleft')
    pag.keyDown('shiftright')
    pag.press('down', presses=num_second_batch)
    pag.keyUp('shiftleft')
    pag.keyUp('shiftright')
    # second openings of files end
    sleep(15)
    pag.press('enter', interval=time[1])
    # kjøre kalkulasjon
    sleep(60)
    pag.press('tab', presses=2, interval=time[2])
    pag.press('space', interval=time[2])

    # if there is experienced trouble whith the automated calculation setup, uncomment below, and do it the hardway!
    # or solve the bug, up to you :))))
    # pause_script()

    # the last part checks the cpu-percentage used to the calculation operations. When it is below a limit of 5 percent
    # the while loop is exited and the script continues with the next step. Also, if there are problems with the file
    # fetching described above, this section can be commented out.
    procname = 'feawin.exe'  # feawin is the filename of RS2 Compute
    bool_proc = mmf.check_if_process_running(procname)
    sleep(5)
    while bool_proc:
        pid = mmf.get_pid(procname)
        process_compute = psutil.Process(pid)
        # this makes sure that the screen do not go to powersave mode for PCs lacking admin controll or lacking
        # controll over the functionality of the lock and sleep beaviour.
        pag.click(coordinate_rs2_compute[name_col_df_mouse[1]][i],
                  coordinate_rs2_compute[name_col_df_mouse[2]][i], interval=time[0])
        if process_compute.cpu_percent(interval=15) > 5.0:
            bool_proc = True
        else:
            bool_proc = False
    return


"""
calculate calls the Auto.automation_actions_calculation
when calculation finnished it calls get_files_unsuc_tolerance to get files that is exceeding allowed tolerance.
"""


def calculate(path_rs2_compute, time, df_filnavn_rs2, sti_til_mappe_for_arbeidsfiler, path_store_unsuc_tol_models,
              tolerance, number_of_files, bool_shall_execute_calculate, coordinate_rs2_compute, name_col_df_mouse,
              bool_stop_to_check_logs, storage_calculation_times):
    """

    @param path_rs2_compute:
    @param time:
    @param df_filnavn_rs2:
    @param sti_til_mappe_for_arbeidsfiler:
    @param path_store_unsuc_tol_models:
    @param tolerance:
    @param number_of_files:
    @param bool_shall_execute_calculate:
    @param coordinate_rs2_compute:
    @param name_col_df_mouse:
    @param bool_stop_to_check_logs:
    @param storage_calculation_times:
    @return:
    """
    if bool_shall_execute_calculate is False:
        return
    time_operation = time.time()
    category = 'calculation'
    Popen([path_rs2_compute])
    sleep(5)
    automation_actions_calculation(number_of_files, sti_til_mappe_for_arbeidsfiler, coordinate_rs2_compute,
                                   name_col_df_mouse)
    # lukke RS2 Compute
    pag.hotkey('alt', 'f4', interval=time[2])
    get_files_unsuc_tolerance(sti_til_mappe_for_arbeidsfiler, df_filnavn_rs2, path_store_unsuc_tol_models, tolerance)
    mmf.calculate_computation_time(time_operation, category, storage_calculation_times)
    if bool_stop_to_check_logs is True:
        mmf.procede_script()
    return
