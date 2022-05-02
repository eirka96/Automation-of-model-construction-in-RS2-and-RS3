import statistics

import pandas as pd
import numpy as np
import shutil as st
import os
import re
import zipfile
import pathlib
import itertools
import matplotlib.pyplot as plt

from colorama import Fore
from colorama import Style
from csv import writer
from ast import literal_eval

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# pd.set_option('display.max_colwidth', -1)
def get_range_changing_attributes(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                                  mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                 mektighet_attributes, angel_attributes, y_attributes, x_attributes]
    for idx, iter_object in enumerate(iter_list):
        if not isinstance(iter_object, (list, float, int, tuple)) or (isinstance(iter_object, (list, tuple)) and
                                                                      len(iter_object) != 3):
            print(
                "Advarsel!!!!! Input må være enten type int, float, list eller tupple. Dessuten må list eller tuple ha "
                "lengde 3 og være på formen [start_element, slutt_element, steg for element]")
            break
        elif isinstance(iter_object, (int, float)):
            iter_list[idx] = [iter_object]
        else:
            iter_list[idx] = np.arange(iter_object[0], iter_object[1], iter_object[2]).tolist()

    return iter_list[0], iter_list[1], iter_list[2], iter_list[3], iter_list[4], iter_list[5], iter_list[6], iter_list[
        7]


def get_shape_matrix(rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                     mektighet_attributes, angel_attributes, y_attributes, x_attributes):
    iter_list = [rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                 mektighet_attributes, angel_attributes, y_attributes, x_attributes]
    shape_matrix_list = []
    for iter_object in iter_list:
        if isinstance(iter_object, (int, float)):
            shape_matrix_list.append(1)
        else:
            shape_matrix_list.append(len(iter_object))
    return shape_matrix_list


def set_model_attributes(path_csv_attributes, rock_mass_material, weakness_zone_material, stress_ratio, overburden,
                         mektighet_attributes, angel_attributes, y_attributes, x_attributes):
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


def get_file_paths_batch(paths_shale_rs2, path_csv):
    l = [25, 100, 200, 300, 500, 800, 1000]
    sti_kildefil_rs2 = []
    sti_kildefil_csv = []
    for i in l:
        sti_kildefil_rs2.append(
            paths_shale_rs2.format(i, i, i))
        sti_kildefil_csv.append(path_csv)
    return sti_kildefil_rs2, sti_kildefil_csv


"""
Funksjon under brukes til nå ikke 
"""
# def get_original_file_paths():
#     l = [25, 100, 200, 300, 500, 800, 1000]
#     sti_kildefil_rs2 = []
#     sti_kildefil_csv = []
#     for i in l:
#         sti_kildefil_rs2.append(
#             r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine " \
#             r"modeller\RS2\tverrsnitt_sirkulær\sirkulær_mal\mal_S_bm80_ss1_k1_od{}" \
#             r"\S_bm80_ss1_k1_od{}_v0_m2_mal\S_bm80_ss1_k1_od{}_v0_m2_mal.fea ".format(i, i, i))
#         sti_kildefil_csv.append(r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave"
#                                 r"\modellering_svakhetssone\parameterstudie\excel\Pycharm_automatisering"
#                                 r"\parameter_verdier_filnavn\S_bm80_ss1_k1_od{}\S_bm80_ss1_k1_od{}.csv ".format(i, i))
#     return sti_kildefil_rs2, sti_kildefil_csv


""" henter ut stier fra elleredeeksisterende eksperiment"""


def get_old_paths_df(sti_csv_gamle_rs2stier, sti_csv_gamle_csvStier):
    # df_gamle_rs2filer/csvfiler:
    # er en dataframe som inneholder stiene lest fra sti_csv_gamle_rs2stier
    df_gamle_stier_rs2filer = pd.read_csv(sti_csv_gamle_rs2stier, sep=';')
    df_gamle_stier_csvfiler = pd.read_csv(sti_csv_gamle_csvStier, sep=';')
    # Tomme elementer får verdien None.
    df_gamle_stier_rs2filer = df_gamle_stier_rs2filer.fillna(np.nan).replace([np.nan], [None])
    df_gamle_stier_csvfiler = df_gamle_stier_csvfiler.fillna(np.nan).replace([np.nan], [None])
    df_stier_rs2filer = df_gamle_stier_rs2filer.copy()
    df_stier_csvfiler = df_gamle_stier_csvfiler.copy()
    return df_stier_rs2filer, df_stier_csvfiler


def get_new_paths_df(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer, sti_kildefil_rs2, sti_kildefil_csv,
                     sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier):
    while True:
        try:
            command = input('Vil du lage nye rs2-filer? j for ja og n for nei: ')
            if command == 'j':
                # I create_folders:
                # vil mapper fra forrige prosjekt eventuelt bli slettet og mappene
                # til det nye prosjekt blir laget hvis dette er tilfelle
                delete_and_create_folders(sti_til_mappe_for_arbeidsfiler, sti_til_mapper_endelige_filer)
                # mappenavn_til_rs2, mappenavn_til_csv = get_name_folders(sti_til_mapper_endelige_filer)
                # copy_and_store:
                # lager alle kopiene av kildefilene og lagrer filene i rett mappe.
                # Dette gjøres ved å bruke mappenavn og filnavn som markør.
                df_nye_stier_rs2filer, df_nye_stier_csvfiler = copy_and_store0(sti_kildefil_rs2,
                                                                               sti_til_mappe_for_arbeidsfiler,
                                                                               sti_til_mapper_endelige_filer,
                                                                               sti_kildefil_csv)
                # to_csv:
                # Her blir alle stiene til de nylagete rs2-filene lagret.
                df_nye_stier_rs2filer.to_csv(alternate_slash([sti_csv_gamle_rs2stier])[0], sep=';')
                df_nye_stier_csvfiler.to_csv(alternate_slash([sti_csv_gamle_csvstier])[0], sep=';')
                df_stier_rs2filer = df_nye_stier_rs2filer.copy()
                df_stier_csvfiler = df_nye_stier_csvfiler.copy()
                return [True, df_stier_rs2filer, df_stier_csvfiler]
            elif command == 'n':
                return [False]
            else:
                print('j for ja din nisse!')
        except NameError:
            print('implementert verdi ukjent')
            continue


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
    file_name_excel_list = []
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
        file_name_excel_list.append(path1)
    return file_name_rs2_list, file_name_excel_list


"""beskrivelsen for denne er identisk med den over bare at denne er tilpasset for mappenavn
parameter_verdier_excel har en annen sti og det blir ikke lagt til .fea i enden av navnet."""

def make_folder_name(geometri='S'):
    parameter_verdier_csv = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
                            r"\parameterstudie" \
                            r"\excel\Pycharm_automatisering\parameter_verdier_mappenavn.csv "
    df_verdier = pd.read_csv(parameter_verdier_csv, sep=';')
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


def delete_and_create_folders(storage_path, storage_final_folders):
    storage_path = alternate_slash([storage_path])[0]
    storage_final_folders = alternate_slash([storage_final_folders])[0]
    folder_names = make_folder_name()
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
    list_folders.sort(key=len)  # sørger for at mappenavnene blir sortert i stigende rekkefølge
    list_csv_folders, list_rs2_folders = [s + '/csv/' for s in list_folders], [s + '/rs2/' for s in list_folders]
    # må endres hvis mappestrukturen endres!!!!!!
    return list_rs2_folders, list_csv_folders


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
def copy_and_store0(path_file0_rs2, path_storage_files, path_final_folders, parameter_verdier_csv, geometri='S'):
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
    df_list_path_rs2 = df_name_rs2_files.copy()  # ved = alene så vil endringer på den ene føre til samme endringer på den andre
    df_list_path_csv = df_name_csv_files.copy()
    i = 0
    for rs2, csv in zip(name_rs2_folders,
                        name_csv_folders):  # tilordner filnavn sine stier. Tomme elementer forblir tomme.
        for file in df_list_path_rs2.index.values:
            if df_name_rs2_files[rs2][file] is not None and df_name_csv_files[csv][file] is not None:
                df_list_path_rs2.loc[file, rs2] = path_storage_files + '/' + df_name_rs2_files[rs2][file]
                df_list_path_csv.loc[file, csv] = path_storage_files + '/' + df_name_csv_files[csv][file]
                st.copyfile(path_file0_rs2[i], df_list_path_rs2[rs2][file])
                pd.DataFrame({}).to_csv(df_list_path_csv[csv][file])
        i += 1
    return df_list_path_rs2, df_list_path_csv


def copy_and_store(path_file0_rs2, path_storage_files, parameter_verdier_csv, geometri='S'):
    path_file0_rs2 = [alternate_slash([path])[0] for path in
                      path_file0_rs2]  # alternate_slash kun laget for å funke på lister
    name_rs2_folders, name_csv_folders = get_name_folders(path_storage_files)
    path_storage_files = alternate_slash([path_storage_files])[0]
    df_name_rs2_files = pd.DataFrame(columns=name_rs2_folders)
    df_name_csv_files = pd.DataFrame(columns=name_csv_folders)
    for rs2, csv, attributes in zip(name_rs2_folders, name_csv_folders,
                                    parameter_verdier_csv):  # sammenlikner mappenavn med RS2-fil-navn.
        list_rs2_file_names, list_csv_file_names = make_file_name(attributes, geometri)
        rs21 = rs2.replace('/rs2/', '')
        res_rs2 = [i for i in list_rs2_file_names if rs21 in i]  # Når det matcher blir filnavnet lagret i kolonna til
        csv1 = csv.replace('/csv/', '')
        res_csv = [i for i in list_csv_file_names if csv1 in i]
        df_name_rs2_files.loc[:, rs2] = pd.Series(res_rs2, dtype=str)  # mappenavnet. Lagres i en dataframe.
        df_name_csv_files.loc[:, csv] = pd.Series(res_csv, dtype=str)
    df_name_rs2_files = df_name_rs2_files.fillna(np.nan).replace([np.nan], [None])  # Tomme elementer får verdien None.
    df_name_csv_files = df_name_csv_files.fillna(np.nan).replace([np.nan], [None])
    df_list_path_rs2 = df_name_rs2_files.copy()  # ved = alene så vil endringer på den ene føre til samme endringer på den andre
    df_list_path_csv = df_name_csv_files.copy()
    i = 0
    for rs2, csv in zip(name_rs2_folders,
                        name_csv_folders):  # tilordner filnavn sine stier. Tomme elementer forblir tomme.
        for file in df_list_path_rs2.index.values:
            if df_name_rs2_files[rs2][file] is not None and df_name_csv_files[csv][file] is not None:
                folder_name_rs2 = path_storage_files + '/' + rs2 + df_name_rs2_files[rs2][file].replace('.fea', '')
                folder_name_csv = path_storage_files + '/' + csv + df_name_csv_files[csv][file].replace('.csv', '')
                os.mkdir(os.path.join(path_storage_files + rs2, folder_name_rs2))
                os.mkdir(os.path.join(path_storage_files + csv, folder_name_csv))
                df_list_path_rs2.loc[file, rs2] = folder_name_rs2 + '/' + df_name_rs2_files[rs2][file]
                df_list_path_csv.loc[file, csv] = folder_name_csv + '/' + df_name_csv_files[csv][file]
                # print(df_list_path_rs2[rs2][file])
                st.copyfile(path_file0_rs2[i], df_list_path_rs2[rs2][file])
                pd.DataFrame({}).to_csv(df_list_path_csv[csv][file])
                # path_feaFileMap = df_list_path_rs2[rs2][file].replace(".fea", '')
                # with zipfile.ZipFile(df_list_path_rs2[rs2][file], "r") as zip_ref:  # unzipping the .fea file
                #     zip_ref.extractall(path_feaFileMap)
                # for filename in os.listdir(path_feaFileMap):
                #     extension = pathlib.Path(filename).suffix
                #     # print(extension)
                #     source = path_feaFileMap + '/' + filename
                #     destination = path_feaFileMap + '/' + df_name_rs2_files[rs2][file].replace(".fea", '') + extension
                #     os.rename(source, destination)
            else:
                continue
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


def transform_coordinates_mouse(sti_koordinater_mus, navn_kol_df_koord_mus, q=10, x=0, y=0):
    ox = 1153
    oy = 510
    q = np.deg2rad(10)
    df_koordinater_mus = pd.read_csv(sti_koordinater_mus, sep=';')
    df_koordinater_mus.pop(navn_kol_df_koord_mus[0])
    # df = df_koordinater_mus.copy().head(3)  # uendrete koordinater, de to andre blir appenda til denne etter endring

    # rotere
    # df_rot = df_koordinater_mus.copy().iloc[3:]  # koordinater som skal roteres
    # print(df_koordinater_mus)
    R = np.array([[np.cos(q), -np.sin(q)], [np.sin(q), np.cos(q)]])  # rotasjonsmatrise, mot klokka når vinkel q er +
    r = pd.DataFrame(data=R, index=['x', 'y'])
    # print(r)
    # df_koordinater_mus.iloc[2:, 0] -= ox
    # df_koordinater_mus.iloc[2:, 1] -= oy
    df_koordinater_mus.iloc[3:] = df_koordinater_mus.iloc[3:].dot(r)
    # df_koordinater_mus.iloc[2:, 0] += ox
    # df_koordinater_mus.iloc[2:, 1] += oy
    df_koordinater_mus.columns = ['x', 'y']
    # print(df_koordinater_mus)

    # forflytning
    # df_trans = df_rot.copy().iloc[1:]  # koordinater som skal forflyttes
    df_koordinater_mus.iloc[4:, 0] += x
    df_koordinater_mus.iloc[4:, 1] -= y
    return df_koordinater_mus


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


def get_Query_values(path_to_csv, parameternavn):
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
    to_plot = []
    for i, query in enumerate(query_values):
        to_plot.append([])
        for value in query:
            to_plot[i].append(value[5:])
    return to_plot


def get_values_quad(to_plot, points, query_positions, ind_to_plot):
    if not (to_plot is not None and points is not None):
        return None
    value_intersect, max_value, indices_max_value = [], [], []
    points = [[round(point[0], 3), round(point[1], 3)] for point in points]
    for data_sep, q_pos_sep in zip(to_plot, query_positions):
        values = [value for value, q_pos in zip(data_sep, q_pos_sep) if q_pos in points]
        positions = [q_pos for q_pos in q_pos_sep if q_pos in points]
        indices = [i for i, q_pos in enumerate(q_pos_sep) if q_pos in points]
        value_intersect.append([values[ind_to_plot[0]][1], values[ind_to_plot[1]][1]])
        a = max([indices[ind_to_plot[0]], indices[ind_to_plot[1]]])
        b = min([indices[ind_to_plot[0]], indices[ind_to_plot[1]]])
        check = [i for i in range(b, a + 1, 1)]
        index_max_value = int(statistics.median(check)//1)  # //1 rounds number down to closest integer
        max_value.append(data_sep[index_max_value])
        indices_max_value.append(index_max_value)
    return [value_intersect, max_value]


def get_difference(to_plot, points, query_positions):
    if not (to_plot is not None and points is not None):
        return None
    points = [[round(point[0], 3), round(point[1], 3)] for point in points]
    diff1, diff2 = [], []
    for data_sep, q_pos_sep in zip(to_plot, query_positions):
        values = []
        i = 0
        for value, q_pos in zip(data_sep, q_pos_sep):
            # print(i)
            # i += 1
            if q_pos in points:
                values.append(value)
        diff1.append(abs(values[0][1] - values[2][1]))
        diff2.append(abs(values[1][1] - values[3][1]))
    return diff1, diff2


def plot_data(data, parameter_navn):
    parameter_navn.pop()
    for idx, navn in enumerate(parameter_navn):
        df = pd.DataFrame(data[idx], columns=['x', 'y'])
        plt.plot(df['x'], df['y'])
        # color = 'green', linestyle = 'dashed', linewidth = 3,
        # marker = 'o', markerfacecolor = 'blue', markersize = 12

        # # labels for bars
        # tick_label = ['one', 'two', 'three', 'four', 'five']
        #
        # # plotting a bar chart
        # plt.bar(left, height, tick_label=tick_label,
        #         width=0.8, color=['red', 'green'])
        plt.xlabel('Buelengden til tunnelkontur')
        plt.ylabel(navn)
        plt.title('plot av ' + navn + 'langs tunnelkontur.')
        # plt.legend()
        plt.show()
    return


def get_df_differences_from_csv(path):
    df = pd.read_csv(path, sep=';')
    print(df)
    return df


def get_list_file_indices(num_models, elements_corrupted_files):
    index = [i for i in range(num_models)]
    index.pop()
    index.pop(135)
    index = [i for i in index if i not in elements_corrupted_files]
    return index


def plot_differences(paths, parameter_navn, elements_corrupted_files, differanse_navn, fysiske_enheter):
    parameter_navn = parameter_navn.copy()
    parameter_navn.pop()
    differanse_navn = differanse_navn.copy()
    differanse_navn.pop(0)
    index = get_list_file_indices(150, elements_corrupted_files)
    for par_navn, path, enhet in zip(parameter_navn, paths, fysiske_enheter):
        df = get_df_differences_from_csv(path)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for diff_navn in differanse_navn:
            y = df[diff_navn]
            ax.scatter(index, y)
        # color = 'green', linestyle = 'dashed', linewidth = 3,
        # marker = 'o', markerfacecolor = 'blue', markersize = 12

        # # labels for bars
        # tick_label = ['one', 'two', 'three', 'four', 'five']
        #
        # # plotting a bar chart
        # plt.bar(left, height, tick_label=tick_label,
        #         width=0.8, color=['red', 'green'])
        plt.xlabel('modellnummer')
        plt.ylabel('differanse av ' + par_navn + ' ' + enhet)
        plt.title('plot, differanse av ' + par_navn)
        # plt.legend()
        plt.show()
    return


def get_indices_paths_selection(list_attributes, attribute_types, paths, elements_corrupted_files, list_exluded_files):
    indices_true = []
    indices_augm = []
    i = 0
    for attributes, attribute_type in zip(list_attributes, attribute_types):
        indices_true.append([])
        indices_augm.append([])
        attributes = np.arange(attributes[0], attributes[1], attributes[2])
        attributes = attributes.tolist()
        comb_str_list = combine_str(attributes, attribute_type)
        for comb_str in comb_str_list:
            selected_idx_true = [j for j, path in enumerate(paths) if comb_str in path and
                                 (j not in elements_corrupted_files and j not in list_exluded_files)]
            selected_idx_augm = [j for j in range(len(selected_idx_true))]
            indices_true[i].append(selected_idx_true)
            indices_augm[i].append(selected_idx_augm)
        i += 1
    return indices_true, indices_augm


def get_category(list_attributes, attribute_types, paths, elements_corrupted_files, list_exluded_files):
    category = []
    indices = []
    i, p = 0, 0
    for attributes, attribute_type in zip(list_attributes, attribute_types):
        category.append([])
        indices.append([])
        attributes = np.arange(attributes[0], attributes[1], attributes[2])
        attributes = attributes.tolist()
        comb_str_list = combine_str(attributes, attribute_type)
        for comb_str in comb_str_list:
            for j, path in enumerate(paths):
                if comb_str in path and (j not in elements_corrupted_files and j not in list_exluded_files):
                    category[i].append(comb_str)
                    indices[i].append(p)
                    p += 1
        p = 0
        i += 1
    return category, indices


def get_start_index_df_value(parameter_navn, diff_navn):
    list_indices = []
    for i in range(len(parameter_navn)):
        list_indices.append([])
        for j in range(len(diff_navn)):
            list_indices[i].append(i*2+4*j)
    return list_indices


def plot_value_selection(path, parameter_navn, diff_navn, val_navn, fysiske_enheter, list_category, list_indices,
                         attribute_type, color_map):
    parameter_navn.pop()
    diff_navn.pop(0)
    val_navn.pop(0)
    df = get_df_differences_from_csv(path)
    df = df.iloc[:, 1:]
    for column in df:
        print(column)
        df[column] = df[column].apply(literal_eval)
    list_df_indices = get_start_index_df_value(parameter_navn, diff_navn)
    for k, (par_navn, enhet) in enumerate(zip(parameter_navn, fysiske_enheter)):
        for category, indices, type0 in zip(list_category, list_indices, attribute_type):
            df['category'] = category
            df['indices_true'] = indices
            groups = df.groupby('category')
            figure, axis = plt.subplots(1, 2)
            for i, diff_name in enumerate(diff_navn):
                axis[i].set_prop_cycle(color=color_map[type0])
                for name, group in groups:
                    range0 = val_navn[list_df_indices[k][i]]
                    range1 = val_navn[list_df_indices[k][i]+1]
                    axis[i].plot(group['indices_true'], group[[range0]], marker="o", linestyle="--", label=name)
                    axis[i].plot(group['indices_true'], group[[range0]], marker="o", linestyle="--", label=name)
                    axis[i].plot(group['indices_true'], group[[range1]], marker="o", linestyle="--", label=name)
                    axis[i].legend()
                    axis[i].set_xlabel('modellnummer')
                    axis[i].set_ylabel('differanse av ' + par_navn + ' ' + enhet)
                    axis[i].set_title('plot, differanse av ' + par_navn + 'sortert mhp. ' + type0 + ', ' + diff_name)
                # for j, txt in enumerate(df['indices_true']):
                #     axis[i].annotate(txt, (txt, df[diff_name][j]), fontsize=8)
            plt.show()

    return


def plot_difference_selection(paths, parameter_navn, differanse_navn, fysiske_enheter, list_category, list_indices,
                              attribute_type, color_map):
    parameter_navn.pop()
    differanse_navn.pop(0)
    for par_navn, path, enhet in zip(parameter_navn, paths, fysiske_enheter):
        df = get_df_differences_from_csv(path)
        for category, indices, type0 in zip(list_category, list_indices, attribute_type):
            df['category'] = category
            df['indices_true'] = indices
            groups = df.groupby('category')
            # figure, axis = plt.subplot()
            i = 0
            figure, axis = plt.subplots(1, 2)
            for diff_name in differanse_navn:
                axis[i].set_prop_cycle(color=color_map[type0])
                # plt.figure(i)
                # i += 1
                for name, group in groups:
                    axis[i].plot(group['indices_true'], group[diff_name], marker="", linestyle="-", label=name)
                    axis[i].legend()
                    axis[i].set_xlabel('modellnummer')
                    axis[i].set_ylabel('differanse av ' + par_navn + ' ' + enhet)
                    axis[i].set_title('plot, differanse av ' + par_navn + 'sortert mhp. ' + type0 + ', ' + diff_name)
                for j, txt in enumerate(df['indices_true']):
                    axis[i].annotate(txt, (txt, df[diff_name][j]), fontsize=8)
                # for indices_true, indices_augm in zip(indices_selection_true, indices_selection_augm):
                #     fig = plt.figure()
                #     ax = fig.add_subplot(111)
                #     for indices0_true, indices0_augm in zip(indices_true, indices_augm):
                #         for diff_navn in differanse_navn:
                #             y = df.loc[indices0_augm, diff_navn]
                #             ax.scatter(indices0_true, y)
                # color = 'green', linestyle = 'dashed', linewidth = 3,
                # marker = 'o', markerfacecolor = 'blue', markersize = 12

                # # labels for bars
                # tick_label = ['one', 'two', 'three', 'four', 'five']
                #
                # # plotting a bar chart
                # plt.bar(left, height, tick_label=tick_label,
                #         width=0.8, color=['red', 'green'])
                #     plt.
                #     plt.
                #     plt.
                i += 1
                # plt.legend()
                # plt.legend()
            plt.show()
    return


def make_container_diff(mappenavn_rs2):
    container = []
    for i in range(len(mappenavn_rs2)):
        container.append([])
    return container


def get_filenames_col_csv(paths_fil_csv, path_arbeidsmappe):
    path_arbeidsmappe = alternate_slash([path_arbeidsmappe])[0]
    file_names_csv = [path.replace(path_arbeidsmappe + '/', '') for path in paths_fil_csv if isinstance(path, str)]
    file_names_csv = [path.replace('.csv', '') for path in file_names_csv]
    return file_names_csv


def create_difference_csv(foldername_csv, list_differences, parameternavn_interpret, paths_fil_csv, path_arbeidsmappe,
                          elements_corrupted_files, type_verdi, path_data_storage):
    paths_csv = paths_fil_csv.copy()
    if all(path is None for path in paths_fil_csv):
        return None, None
    t = path_data_storage
    t = alternate_slash([t])[0]
    filnavn_csv = get_filenames_col_csv(paths_csv, path_arbeidsmappe)
    p = parameternavn_interpret.copy()
    p.pop()
    # fjerner de paths som er korruperte
    paths_to_remove = get_subset_file_paths(paths_fil_csv, elements_corrupted_files)
    names_to_remove = [re.findall(r'/(?:.(?!/))+$', path)[0][1:] for path in paths_to_remove]
    names_to_remove = [name.replace('.csv', '') for name in names_to_remove]
    names_to_remove = names_to_remove + ['S_bm80_ss1_k1_od500_m5.0_v22.5_y0_x7',
                                         'S_bm80_ss1_k1_od500_m5.0_v22.5_y0_x-7']
    filnavn_csv = [name for name in filnavn_csv if name not in names_to_remove]
    # lager paths til der hvor differensene skal lagres
    paths = [[t + '/' + foldername_csv + type_verdi + '_' + navn.replace(':', '').replace(' ', '') + '.csv'] for navn in p]
    # df_differences = pd.DataFrame(columns=['file_name', 'quad_low', 'quad_high'])
    for navn, differences in zip(filnavn_csv, list_differences):
        d = list(map(list, zip(*differences)))  # transposes the list of lists
        for path, difference in zip(paths, d):
            path.append([navn] + difference)
    # df_differences.to_csv(path_or_buf=path, sep=';', mode='w')
    diff_navn = ['file_name', 'quad_high', 'quad_low']
    for path in paths:
        j = path[1:]
        df_difference = pd.DataFrame(j, columns=diff_navn)
        df_difference.set_index('file_name', inplace=True)
        df_difference.to_csv(path_or_buf=path[0], sep=';', mode='w')
    return [paths[0][0], paths[1][0]], diff_navn


def create_values_csv(foldername_csv, list_values, parameternavn_interpret, paths_fil_csv, path_arbeidsmappe,
                      elements_corrupted_files, type_verdi, path_data_storage, val_navn):
    paths_csv = paths_fil_csv.copy()
    if all(path is None for path in paths_fil_csv):
        return None, None
    t = path_data_storage
    t = alternate_slash([t])[0]
    filnavn_csv = get_filenames_col_csv(paths_csv, path_arbeidsmappe)
    p = parameternavn_interpret.copy()
    p.pop()
    # fjerner de paths som er korruperte
    paths_to_remove = get_subset_file_paths(paths_fil_csv, elements_corrupted_files)
    names_to_remove = [re.findall(r'/(?:.(?!/))+$', path)[0][1:] for path in paths_to_remove]
    names_to_remove = [name.replace('.csv', '') for name in names_to_remove]
    names_to_remove = names_to_remove + ['S_bm80_ss1_k1_od500_m5.0_v22.5_y0_x7',
                                         'S_bm80_ss1_k1_od500_m5.0_v22.5_y0_x-7']
    filnavn_csv = [name for name in filnavn_csv if name not in names_to_remove]
    # lager paths til der hvor verdiene skal lagres
    path = t + '/' + foldername_csv + type_verdi + '.csv'
    # df_differences = pd.DataFrame(columns=['file_name', 'quad_low', 'quad_high'])
    list_to_df = []
    for navn, values in zip(filnavn_csv, list_values):
        # d = list(map(list, zip(*differences)))  # transposes the list of lists
        list_to_df.append([navn] + values)
    # df_differences.to_csv(path_or_buf=path, sep=';', mode='w')
    df_difference = pd.DataFrame(list_to_df, columns=val_navn)
    df_difference.to_csv(path_or_buf=path, sep=';', mode='w', index=False)
    return path


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


def get_subset_file_paths(file_paths, elements):
    sub_paths = [path for i, path in enumerate(file_paths) if elements.count(i) > 0]
    return sub_paths


def set_corrupted_files(file_paths, path_list_corrupted_files):
    file_sizes = get_list_size_files(file_paths)
    elements_corrupted_files = get_elements_small_files(file_sizes)
    corrupted_files = get_subset_file_paths(file_paths, elements_corrupted_files)
    with open(path_list_corrupted_files, mode='a') as file:
        file.writelines('\n'.join(corrupted_files))
        file.write('\n')
    return


def empty_file(path):
    open(path, mode='w').close()
    return


def get_list_paths(folder_name, df_paths):
    return df_paths[folder_name]


def get_elements_corrupted_files(file_paths):
    if all(path is None for path in file_paths):
        return
    file_sizes = get_list_size_files(file_paths)
    elements = get_elements_small_files(file_sizes)
    return elements


# returns which of the parameters in the sensitivity study that are lists and returns a lis of the lists
def return_lists(list_attributes):
    checker = ['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']
    res = [elem for elem in zip(list_attributes, checker) if isinstance(elem[0], list)]
    res = list(zip(*res))
    return list(res[0]), list(res[1])


def get_paths_sorted(list_attributes, attribute_types, paths):
    sorted_paths = []
    i = 0
    for attributes, attribute_type in zip(list_attributes, attribute_types):
        sorted_paths.append([])
        comb_str_list = combine_str(attributes, attribute_type)
        for comb_str in comb_str_list:
            selected_paths = [path for path in paths if comb_str in path]
            sorted_paths[i].append(selected_paths)
        i += 1
    return sorted_paths


def combine_str(attributes, type0):
    comb_str_list = []
    for attribute in attributes:
        comb_str = type0 + str(attribute)
        comb_str_list.append(comb_str)
    return comb_str_list


def get_tunnel_boundary_points(data, index_boundary1):
    d = data.copy()
    d = d[index_boundary1:]
    tunnel_boundary_points = []
    for line in d:
        if line == '      dpoint array end:\n':
            break
        tunnel_boundary_points.append(line)
    return tunnel_boundary_points

