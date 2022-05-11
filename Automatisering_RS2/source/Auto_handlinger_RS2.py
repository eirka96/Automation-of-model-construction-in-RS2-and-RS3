import pyautogui as pag
import psutil
import pandas as pd

from time import sleep

from Automatisering_RS2.source.alter_geometry import geometry_operations as go

time_list = [0, 0.5, 1, 2, 5]


def klargjore_rs2(df_koordinater_mus, navn_kol, i=0, time=None):
    if time is None:
        time = time_list
    pag.click(df_koordinater_mus[navn_kol[1]][i], df_koordinater_mus[navn_kol[2]][i],
              interval=time[0])  # muliggjør hurtigtaster
    i += 1
    pag.press('enter', interval=time[0])
    pag.press('f2', interval=time[0])  # sørge for at prosjektet er zoomet helt ut
    pag.hotkey('ctrl', 'r', interval=time[2])  # fjerne mesh
    return i


def alter_model(ytre_grenser_utstrekning, path_of_rs2_file, path_of_csv_file, df_endrede_attributter_rs2filer,
                mappenavn_til_stikategori, list_which_material, _0lines_inside, _1line_inside, _2lines_inside,
                _excluded_files_2linescalc, _points_to_check, i, j, _iternumber_0, _iternumber_1, _iternumber_2,
                l_inner_points):
    # endrer materialparametere og geometri for rs2-modelen, basert på filnavnet
    vinkel = df_endrede_attributter_rs2filer[mappenavn_til_stikategori[i]][j]['v']
    vinkel = float(vinkel)
    forflytning_y = float(df_endrede_attributter_rs2filer[mappenavn_til_stikategori[i]][j]['y'])
    forflytning_x = float(df_endrede_attributter_rs2filer[mappenavn_til_stikategori[i]][j]['x'])
    if forflytning_x == 1.0:
        forflytning_x = 0.99
    mektighet = float(df_endrede_attributter_rs2filer[mappenavn_til_stikategori[i]][j]['m'])
    # print(vinkel), print(forflytning_y), print(forflytning_x), print(mektighet), print(mappenavn_til_stikategori)
    go.alter_geometry(vinkel, forflytning_x, forflytning_y, mektighet, path_of_rs2_file,
                      list_which_material, _0lines_inside, _1line_inside, _2lines_inside,
                      _excluded_files_2linescalc, i, _points_to_check, path_of_csv_file,
                      _iternumber_0, _iternumber_1, _iternumber_2, l_inner_points,
                      ytre_grenser_utstrekning=ytre_grenser_utstrekning)
    return


def store_results_csv_prep_init(df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
              interval=time[1])  # velg stage 2
    i += 1
    pag.hotkey('f6', interval=time[1])
    # pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #                interval=time[1])  # endre type
    i += 1
    # pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #                interval=time[1])  # velg tot sigma
    i += 1
    # pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
    #           interval=time[1])  # velge sig1
    i += 1
    pag.hotkey('ctrl', 'e', interval=time[1])  # genererer excavation query, da boundaryline unnlater siste node
    return i


def store_results_csv_prep(df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
              interval=time[1])  # velg stage 2
    i += 1
    pag.hotkey('f6', interval=time[1])
    pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                   interval=time[1])  # endre type
    i += 1
    pag.leftClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                   interval=time[1])  # velg tot sigma
    i += 1
    pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
              interval=time[1])  # velge sig1
    i += 1
    pag.hotkey('ctrl', 'e', interval=time[1])  # genererer excavation query, da boundaryline unnlater siste node
    return i


def store_results_in_csv(df_koordinates_mouse, name_col_df, path_fil_csv, navn_parameter, i=0, time=None):
    if time is None:
        time = time_list
    if i == 4:
        sr = pd.DataFrame([navn_parameter])
        sr.to_csv(path_or_buf=path_fil_csv, mode='w', sep=';', header=False, index=False)
        pag.rightClick(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                       interval=time[1])  # velg boundary 1ste gang, høyreklikk
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1])  # velg copy data
        i += 1
        data = pd.read_clipboard()  # henter ut resultat fra interpret RS2, se full beskrivelse i
        # Logg - Mastergradsoppgave_Modellering, 10.08.2021
        data.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=True)  # data lagres i respektiv csv
    else:
        sr = pd.DataFrame([navn_parameter])
        sr.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=False, index=False)
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # endre parameter
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # velg deformation
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # velg total deformation
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='right')  # velg boundary 2dre gang, høyreklikk
        i += 1
        pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i],
                  interval=time[1], button='left')  # velg copy data
        i += 1
        data = pd.read_clipboard()  # henter ut resultat fra interpret RS2, se full beskrivelse i
        # Logg - Mastergradsoppgave_Modellering, 10.08.2021
        data.to_csv(path_or_buf=path_fil_csv, mode='a', sep=';', header=None, index=True)  # data lagres i respektiv csv
    return i


def handlinger_kalkulasjon(time=None):
    if time is None:
        time = time_list
    # velge antall filer som skal kalkuleres
    pag.press('enter', interval=time[1])
    pag.press('tab', presses=9, interval=time[1])
    pag.hotkey('ctrl', 'a', interval=time[2])
    pag.press('enter', interval=time[1])
    # kjøre kalkulasjon
    pag.press('tab', presses=2, interval=time[2])
    pag.press('space', interval=time[2])
    # sjekke prosessor bruken, så lenge den er over en grense så venter resten av scriptet med å kjøre
    procname = 'feawin.exe'
    bool_proc = check_if_process_running(procname)  # feawin er navnet på .exe-fila til RS2 Compute
    sleep(5)
    while bool_proc:
        pid = get_pid(procname)
        process_compute = psutil.Process(pid)
        pag.click(962, 255, interval=time[0])
        if process_compute.cpu_percent(interval=15) > 5.0:
            bool_proc = True
        else:
            bool_proc = False
    return


def interpret_resultat_til_clipboard(time=None):
    if time is None:
        time = time_list
    pag.press('f6', interval=time[2])
    pag.click(754, 527, interval=time[1], button='right')
    pag.click(846, 666, interval=time[1])
    return


def check_if_process_running(process_name):
    """
    Check if there is any running process that contains the given name processName.
    """
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_pid(PROCNAME):
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            return proc.pid

    return None
