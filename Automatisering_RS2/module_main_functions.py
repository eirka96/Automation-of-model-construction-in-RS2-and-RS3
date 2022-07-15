import pandas as pd
import numpy as np
import shutil as st
import os
import re
import time
import psutil
import pyautogui as pag


from subprocess import check_call
from colorama import Fore
from colorama import Style
from datetime import timedelta

"""
get_screen_width gets screen size and monitors it
"""


def get_screen_width(bool_know_size_monitor):
    if bool_know_size_monitor is False:
        return
    screenwidth, screenheight = pag.size()  # the size of main monitor
    print("the size of the main monitor is [" + str(screenwidth) + ", " + str(screenheight) + "].")
    return


"""
get_time_increments returns a list of time-increments used to make artificial breaks when any pag.'function' 
is to be used. It is commented in my thesis the reason for this at page 78.
The full name of the thesis is given in the head of the main file.
"""


def get_time_increments():
    time_list = [0, 0.5, 1, 2, 5]
    return time_list


"""
pause_script is used whenever it is handy to force the script to wait. When j is given as a command in python console
the scripts continues.
"""


def procede_script():
    while True:
        try:
            command = input('fortsette script? j for ja: ')
            if command == 'j' or command == 'n':
                return command
            else:
                print('j for ja din nisse!')
        except NameError:
            print('implementert verdi ukjent')
            continue
    return


"""make_file_empty deletes the content of a file"""


def make_file_empty(file):
    with open(file, 'w'):
        pass
    return


"""
calculate_computation_time, calculates the computation time when called, monitored in python console
used after each bigger operation in main, such as after calculation of the models
"""


def calculate_computation_time(time_start, category, storage_calculation_times):
    if is_file_empty(storage_calculation_times):
        mode = 'w'
    else:
        mode = 'a'
    time_mid = time.time()
    time_diff_in_seconds = time_mid - time_start
    time_diff_in_hours_min_sec = timedelta(seconds=time_diff_in_seconds)
    line = "Tid brukt for kjøring av script etter {}:     {}. (#hours#:#minutes#:#seconds#)\n"\
        .format(category, time_diff_in_hours_min_sec)
    print(line)
    with open(storage_calculation_times, mode=mode) as file:
        file.writelines(line)
    return


"""
Checks if process has started to run
"""


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


"""
gets the PID number of 
"""


def get_pid(procname):
    for proc in psutil.process_iter():
        if proc.name() == procname:
            return proc.pid

    return None


"""
this function copies a variable to clipboard
"""


def copy2clip(txt):
    cmd = 'echo '+txt.strip()+'|clip'
    return check_call(cmd, shell=True)


"""
separates parameters of the sensitivity study that are lists from the parameters that are single values. Used in main
line 119
"""


def separate_lists_and_values(list_attributes):
    checker = ['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']
    res = [elem for elem in zip(list_attributes, checker) if (isinstance(elem[0], list) and elem[1] not in
                                                              ['bm', 'ss', 'k', 'od'])]
    res = list(zip(*res))
    return list(res[0]), list(res[1])


"""
is_file_empty check if a specific file is empty
"""


def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0

1
"""
get_file_paths_batch gets the paths of the template models used to create the fea models of the experiment, and the
path to the csv where the model definition of each model is stored.
"""


def get_file_paths_batch(paths_shale_rs2, path_csv):
    overburdens = [25, 100, 200, 300, 500, 800, 1200]
    sti_kildefil_rs2 = []
    sti_kildefil_csv = []
    for i in overburdens:
        sti_kildefil_rs2.append(
            paths_shale_rs2.format(i, i, i))
        sti_kildefil_csv.append(path_csv)
    return sti_kildefil_rs2, sti_kildefil_csv


"""get file paths of already existing fea-files"""


def get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier):
    # df_gamle_rs2filer/csvfiler:
    # er en dataframe som inneholder stiene lest fra sti_csv_gamle_rs2stier
    df_gamle_stier_rs2filer = pd.read_csv(sti_csv_gamle_rs2stier, sep=';')
    df_gamle_stier_csvfiler = pd.read_csv(sti_csv_gamle_csvstier, sep=';')
    # Tomme elementer får verdien None.
    df_gamle_stier_rs2filer = df_gamle_stier_rs2filer.fillna(np.nan).replace([np.nan], [None])
    df_gamle_stier_csvfiler = df_gamle_stier_csvfiler.fillna(np.nan).replace([np.nan], [None])
    df_stier_rs2filer = df_gamle_stier_rs2filer.copy()
    df_stier_csvfiler = df_gamle_stier_csvfiler.copy()
    return df_stier_rs2filer, df_stier_csvfiler


"""
get file paths of fea-files and csv to store ecxcavation query data. If bool_create_new_project True, old content is
deleted and new files and folder system is created, if False the olde ystem is kept and the file paths is fetched.
The fea files, if bool_create_new_project True, is created by copying the template files.
"""


def get_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2, sti_kildefil_csv,
                 sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier, parameter_verdier_mappenavn,
                 ytre_grenser_utstrekning, bool_create_new_project):

    if bool_create_new_project:
        # I create_folders:
        # vil mapper fra forrige prosjekt eventuelt bli slettet og mappene
        # til det nye prosjekt blir laget hvis dette er tilfelle
        delete_and_create_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer,
                                  parameter_verdier_mappenavn)
        # mappenavn_til_rs2, mappenavn_til_csv = get_name_folders(sti_til_mapper_endelige_filer)
        # copy_and_store:
        # lager alle kopiene av kildefilene og lagrer filene i rett mappe.
        # Dette gjøres ved å bruke mappenavn og filnavn som markør.
        df_nye_stier_rs2filer, df_nye_stier_csvfiler = copy_and_store(sti_kildefil_rs2,
                                                                      sti_til_mappe_for_arbeidsfiler,
                                                                      sti_til_mapper_endelige_filer,
                                                                      sti_kildefil_csv,
                                                                      ytre_grenser_utstrekning)
        # to_csv:
        # Her blir alle stiene til de nylagete rs2-filene lagret.
        df_nye_stier_rs2filer.to_csv(alternate_slash([sti_csv_gamle_rs2stier])[0], sep=';')
        df_nye_stier_csvfiler.to_csv(alternate_slash([sti_csv_gamle_csvstier])[0], sep=';')
        df_stier_rs2filer = df_nye_stier_rs2filer.copy()
        df_stier_csvfiler = df_nye_stier_csvfiler.copy()
    else:
        df_stier_rs2filer, df_stier_csvfiler = get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier)

    return df_stier_rs2filer, df_stier_csvfiler


"""
create_work_and_storage_folders creates the folders for storing the fea-files to be created and its results
is they do not exist.
"""


def create_work_and_storage_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer):
    # hvis mapper for arbeidsfiler og lagring av resultater ikke eksisterer så lages dette
    if not os.path.exists(alternate_slash([sti_til_mappe_for_arbeidsfiler])[0]):
        os.mkdir(alternate_slash([sti_til_mappe_for_arbeidsfiler])[0])
    if not os.path.exists(alternate_slash([sti_til_mapper_endelige_filer])[0]):
        os.mkdir(alternate_slash([sti_til_mapper_endelige_filer])[0])
    return


"""make_file_name har til hensikt å lage de filnavn tilhørende RS2-prosjekter
funksjonen skal returnere en liste med  alle filnavn på denne formen her:

Input:

parameter_navn:
er en liste av strenger som inneholder de parametere som er definert i excel-fila anvist over, foruten
geometri som ikke har en tallverdi knyttet til seg.
parameter_verdier_excel:
er en streng som inneholder pathen til excel-fila der verdiene til de tilhørende parameternavnene er lagret.
geometri:
inneholder informasjon om tunnelens geometri: s for sirkulær og hs for hestesko. Denne er satt deafult til sikrulær


Andre parametere: df_verdier: dataframe som inneholder verdiene som tilhører de ulike parameternavnene
file_name_liste: liste som tilslutt inneholder alle filnavnene tilhørende rs2-prosjektene som skal opprettes. path:
er variabelen som brukes til å bygge opp hver enkelt streng som tilsammen resulterer i et filnavn for et gitt
rs2-prosjekt.

returnerer:
file_name_list"""


def make_file_name(parameter_verdier_csv, geometri='S'):
    df_verdier = pd.read_csv(parameter_verdier_csv, sep=';')
    parameter_navn = df_verdier.columns.values.tolist()
    file_name_rs2_list = []
    file_name_csv_list = []
    for i in range((df_verdier.shape[0])):
        path = ''
        path += (geometri + "_")
        for navn in parameter_navn:
            path += (navn + str(df_verdier[navn][i]) + "_")
        path = path[:-1]
        path1 = path
        path += '.fea'  # denne er eneste forskjellen mellom make_folder_name og make_file_name
        path1 += '.csv'
        file_name_rs2_list.append(path)
        file_name_csv_list.append(path1)
    return file_name_rs2_list, file_name_csv_list


"""beskrivelsen for denne er identisk med den over bare at denne er tilpasset for mappenavn
parameter_verdier_excel har en annen sti og det blir ikke lagt til .fea i enden av navnet."""


def make_folder_name(parameter_verdier_mappenavn, geometri='S'):
    df_verdier = pd.read_csv(parameter_verdier_mappenavn, sep=';')
    parameter_navn = df_verdier.columns.values.tolist()
    folder_name_list = []
    for i in range((df_verdier.shape[0])):
        path = ''
        path += (geometri + "_")
        for navn in parameter_navn:
            path += (navn + str(df_verdier[navn][i]) + "_")
            if navn == 'y' or navn == 'x':
                if df_verdier[navn][i] == 0:
                    path = path.replace((navn + str(df_verdier[navn][i]) + "_"), "")
        path = path[:-1]
        folder_name_list.append(path)
    return folder_name_list


"""
delete_and_create_folders asks if the user wants to delete content already stored in the working directory. If yes,
it deletes the old and creates
"""


def delete_and_create_folders(storage_path, storage_final_folders, parameter_verdier_mappenavn):
    storage_path = alternate_slash([storage_path])[0]
    storage_final_folders = alternate_slash([storage_final_folders])[0]
    folder_names = make_folder_name(parameter_verdier_mappenavn)
    folder_paths = folder_names
    for i in range(len(folder_names)):
        folder_paths[i] = (storage_final_folders + '/' + folder_names[i] + '/')
    while True:
        try:
            x = input('Vil du slette mapper/filer på denne stien? ')
            if x == 'j':
                if os.path.exists(storage_path):
                    st.rmtree(storage_path, ignore_errors=True)  # folder_paths[i]
                    os.mkdir(storage_path)
                if os.path.exists(storage_final_folders):
                    st.rmtree(storage_final_folders, ignore_errors=True)
                    os.mkdir(storage_final_folders)
                for folder in folder_paths:
                    os.mkdir(os.path.join(storage_final_folders, folder))
                    os.mkdir(os.path.join(folder, folder + '/csv/'))
                    os.mkdir(os.path.join(folder, folder + '/rs2/'))
                break
            elif x == 'n':
                if not os.path.exists(storage_final_folders):
                    for folder in folder_paths:
                        os.mkdir(os.path.join(storage_final_folders, folder))
                        os.mkdir(os.path.join(folder, folder + '/csv/'))
                        os.mkdir(os.path.join(folder, folder + '/rs2/'))
                break
            else:
                print('j for ja din fjomp!')
        except NameError:
            print('implementert verdi ukjent')
            continue
    return


"""hensikten med get_path_folders er å hente stier på de mapper som RS2-filene skal bli lagret i
mappenavn kommer til å være definert utifra de parametere som til en hver tid holdes konstant/skiftes sjeldent,
samt en hovedsti.


parametere:
main_path:
er en streng og er pathen til der hvor de ulike mappene og filene skal lagres. Må sørge for at det er en
backslash i slutten av strengen
list_folders:
liste som inneholder navnene til alle mapper som er relevante for lagring av de produserte RS2-filer


returnerer:
list_folders"""


def get_name_folders(path_storage_files):
    path_storage_files = alternate_slash([path_storage_files])[0]
    list_folders = os.listdir(path_storage_files)  # henter de mappenavn som ligger i main_path
    # list_folders.pop(0)
    # list_folders.pop(0)
    list_folders.sort(key=len)  # sørger for at mappenavnene blir sortert i stigende rekkefølge
    list_csv_folders, list_rs2_folders = [s + '/csv/' for s in list_folders], [s + '/rs2/' for s in list_folders]
    # må endres hvis mappestrukturen endres!!!!!!
    return list_rs2_folders, list_csv_folders


"""copy_and_store:
er en funksjon som tar get_path_folders, make_file_name og alternate_slash i bruk.
Hensikten er å gjøre klar alle filer som skal igjennom sine respektive endringer i RS2.
Gi de tenkte RS2-filene navn som tilsvarer hvordan modellen i et gitt tilfelle skal se ut,
så bestemme i hvilken mappe en gitt fil tilhører for tilslutt å kopiere kildefila n ganger, der hver kopi blir
tilordnet hver sin sti. Mao. ingen av filene er klargjort etter å ha kalt på denne funksjonen
Denne funksjonen oppretter også et excel ark til hver enkelt fil. Der skal lister med resultater lagres.


input:
de som er gitt i funksjonene over.
path_file0 viser til kildefilens sti


andre parametere:
list_name_folders:
Liste av navnene til mappene som RS2_fil_stiene skal lagres i
list_rs2_file_names:
Liste over alle stiene til RS2_filene
df_name_files:
En pandas dataframe som er en 2-dimensjonal matrise med mange tillegsfunksjoner.
I denne er rs2_fil-lagret lagret i de mappene de hører hjemme ved at rs2_filnavnet blir tilordnet den kolonne
som har den rette label gitt av mappenavnet.
df_list_path_files:
Er eksakt lik som df_name_files bare at denne inneholder stien til RS2-fila.


returnerer:
navnet til mappene og dataframe med filplasseringene, samt dataframe med filnavnene."""


def copy_and_store(path_file0_rs2, path_storage_files, path_final_folders, parameter_verdier_csv,
                   ytre_grenser_utstrekning, geometri='S'):
    path_file0_rs2 = [alternate_slash([path])[0] for path in
                      path_file0_rs2]  # alternate_slash kun laget for å funke på lister
    name_rs2_folders, name_csv_folders = get_name_folders(path_final_folders)
    path_storage_files = alternate_slash([path_storage_files])[0]
    df_name_rs2_files = pd.DataFrame(columns=name_rs2_folders)
    df_name_csv_files = pd.DataFrame(columns=name_csv_folders)
    for rs2, csv, attributes in zip(name_rs2_folders, name_csv_folders,
                                    parameter_verdier_csv):  # sammenlikner mappenavn med RS2-fil-navn.
        list_rs2_file_names, list_csv_file_names = make_file_name(attributes, geometri)
        rs21 = rs2.replace('/rs2/', '')
        res_rs2 = [i for i in list_rs2_file_names if rs21 in i]  # Når det matcher blir filnavnet lagret i kolonna til
        csv1 = csv.replace('/csv/', '')  # mappenavnet. Lagres i en dataframe.
        res_csv = [i for i in list_csv_file_names if csv1 in i]
        df_name_rs2_files.loc[:, rs2] = pd.Series(res_rs2, dtype=str)
        df_name_csv_files.loc[:, csv] = pd.Series(res_csv, dtype=str)
    df_name_rs2_files = df_name_rs2_files.fillna(np.nan).replace([np.nan], [None])  # Tomme elementer får verdien None.
    df_name_csv_files = df_name_csv_files.fillna(np.nan).replace([np.nan], [None])
    df_list_path_rs2 = df_name_rs2_files.copy()
    df_list_path_csv = df_name_csv_files.copy()
    i = 0
    for k, (rs2, csv, ytre_grense) in enumerate(zip(name_rs2_folders, name_csv_folders, ytre_grenser_utstrekning)):
        # tilordner filnavn sine stier og copierer mal. Tomme elementer forblir tomme.
        for file in df_list_path_rs2.index.values:
            if df_name_rs2_files[rs2][file] is not None and df_name_csv_files[csv][file] is not None:
                df_list_path_rs2.loc[file, rs2] = path_storage_files + '/' + df_name_rs2_files[rs2][file]
                df_list_path_csv.loc[file, csv] = path_storage_files + '/' + df_name_csv_files[csv][file]
                if ytre_grense == ytre_grenser_utstrekning[i - 1]:
                    continue
                else:
                    st.copyfile(path_file0_rs2[i], df_list_path_rs2[rs2][file])
                pd.DataFrame({}).to_csv(df_list_path_csv[csv][file])
        i += 1
    return df_list_path_rs2, df_list_path_csv


"""get_changing_attribute:
henter ut de attributter som skal endres i RS2-fila, disse blir returnert som en streng


input:
df_name_files:
en dataframe som inneholder alle filnavn kategorisert etter mappe. Hver mappe har sin egen kolonne
Tomme celler har verdien None.
folder_names:
innehar navnene på hver enkelt mappe


andre parametere:
df_marker_of_change:
dataframe som til slutt kun innehar informasjonen om hvordan hver enkelt fil skal endres.
Denne informasjonen er selv lagret i en dataframe. 1. kolonne inneholder type-informasjon
og 2. kolonne inneholder verdien til denne typen. Tilsammen beskriver en rad i df hvilken endring
som gjelder for en bestemt type.


returnerer:
df_marker_of_change"""


def get_changing_attributes(df_path_files, folder_names):
    df_marker_of_change = df_path_files.copy()  # copy for at lhs blir uavhengig av rhs
    for folder in folder_names:
        for file in df_path_files.index.values:
            if df_path_files[folder][file] is None:  # hoppe over tomme plasseringer
                continue
            y = df_path_files[folder][file].rsplit('/', 1)[0] + '/' + folder.replace('/rs2/', '') + '_'
            x = df_path_files[folder][file].replace(y, '')
            x = x.replace('.fea', '')
            num = []
            char = []
            while len(x) != 0:
                x = x.partition('_')
                q = str(x[0])
                num1 = re.findall(r'[+-]?\d+\.?\d*', q)[0]
                char.append(q.replace(num1, ''))
                num.append(num1)
                x = x[2]
            attributes = pd.Series(data=num, name='values', index=char)
            df_marker_of_change.at[file, folder] = attributes
    return df_marker_of_change


"""alternate_slash bytter ut alle bakstreker i hver streng av en liste med strenger og gjør dem om til skråstreker
og omvendt.
hensikt: formatet til stiene som skiller mappenavn med bakstreker blir ikke forstått av python som forstår skråstreker
         Derfor er det nødvendig med en kornvertering.
Hvis input ikke kun består av stier der mappenavn blir kun skilt av bakstreker eller skråstreker,
så stopper funksjonen å kjøre og ingen endring blir oppnådd.


input:
list_path:
liste over stier til gitte objekter.


andre parametere:
find_backslash:
for hver sti som inneholder bakstrek blir et nytt element lagt til i denne lista.
find_frontslash:
for hver sti som inneholder skråstrek blir et nytt element lagt til i denne lista.


returnerer:
-1 hvis en feil har oppstått
list_path hvis alt gikk bra"""


def alternate_slash(list_path):
    try:
        backslash = r"\ "
        backslash = backslash[:-1]
        find_backslash = [i for i in list_path if backslash in i]
        find_frontslash = [j for j in list_path if '/' in j]
        if len(find_backslash) == len(list_path) and len(find_frontslash) == 0:  # kjører kun hvis inputfiler
            find_backslash = [sub.replace(backslash, '/') for sub in find_backslash]  # er i rett format (se over)
            list_path = find_backslash
            for i in range(len(list_path)):
                if list_path[i][-1] == ' ':  # sørger for at formatet til strengen blir rett etter konverteringen
                    list_path[i] = list_path[i][:-1]  # python klarer ikke å lese filplasseringer som er delt med en
                # if path[-1] != '/':                # enkelt bakstrek.
                #     path += '/'
        elif len(find_backslash) == 0 and len(find_frontslash) == len(list_path):  # kjører kun hvis inputfiler
            find_frontslash = [sub.replace('/', backslash) for sub in find_frontslash]  # # er i rett format (se over)
            list_path = find_frontslash
        else:
            print(f'{Fore.RED}Feil!  Listen av stier er ikke ensartet med skråstrek eller ensartet med bakstrek, eller '
                  f'så er det ikke en liste. Funksjonen ble derfor stoppet '
                  f'stoppet{Style.RESET_ALL}')  # Fore og style sørger for feilmelding med rød skrift
            return -1
    except TypeError:
        print(f'{Fore.RED}Feil!  Input er enten ikke en liste, eller en liste av strenger.{Style.RESET_ALL}')
        return -1  # Fore og style sørger for feilmelding med rød skrift

    return list_path
