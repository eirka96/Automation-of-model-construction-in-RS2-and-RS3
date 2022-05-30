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
    l = [25, 100, 200, 300, 500, 800, 1200]
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
                     sti_csv_gamle_rs2stier, sti_csv_gamle_csvstier, parameter_verdier_mappenavn,
                     ytre_grenser_utstrekning):
    while True:
        try:
            command = input('Vil du lage nye rs2-filer? j for ja og n for nei: ')
            if command == 'j':
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
    df_list_path_rs2 = df_name_rs2_files.copy()  # ved = alene så vil endringer på den ene føre til samme endringer på den andre
    df_list_path_csv = df_name_csv_files.copy()
    i = 0
    for k, (rs2, csv, ytre_grense) in enumerate(zip(name_rs2_folders, name_csv_folders, ytre_grenser_utstrekning)):
        # tilordner filnavn sine stier og copierer mal. Tomme elementer forblir tomme.
        for file in df_list_path_rs2.index.values:
            if df_name_rs2_files[rs2][file] is not None and df_name_csv_files[csv][file] is not None:
                df_list_path_rs2.loc[file, rs2] = path_storage_files + '/' + df_name_rs2_files[rs2][file]
                df_list_path_csv.loc[file, csv] = path_storage_files + '/' + df_name_csv_files[csv][file]
                if ytre_grense == ytre_grenser_utstrekning[i-1]:
                    continue
                else:
                    st.copyfile(path_file0_rs2[i], df_list_path_rs2[rs2][file])
                pd.DataFrame({}).to_csv(df_list_path_csv[csv][file])
        i += 1
    return df_list_path_rs2, df_list_path_csv


# def copy_and_store(path_file0_rs2, path_storage_files, parameter_verdier_csv, geometri='S'):
#     path_file0_rs2 = [alternate_slash([path])[0] for path in
#                       path_file0_rs2]  # alternate_slash kun laget for å funke på lister
#     name_rs2_folders, name_csv_folders = get_name_folders(path_storage_files)
#     path_storage_files = alternate_slash([path_storage_files])[0]
#     df_name_rs2_files = pd.DataFrame(columns=name_rs2_folders)
#     df_name_csv_files = pd.DataFrame(columns=name_csv_folders)
#     for rs2, csv, attributes in zip(name_rs2_folders, name_csv_folders,
#                                     parameter_verdier_csv):  # sammenlikner mappenavn med RS2-fil-navn.
#         list_rs2_file_names, list_csv_file_names = make_file_name(attributes, geometri)
#         rs21 = rs2.replace('/rs2/', '')
#         res_rs2 = [i for i in list_rs2_file_names if rs21 in i]  # Når det matcher blir filnavnet lagret i kolonna til
#         csv1 = csv.replace('/csv/', '')
#         res_csv = [i for i in list_csv_file_names if csv1 in i]
#         df_name_rs2_files.loc[:, rs2] = pd.Series(res_rs2, dtype=str)  # mappenavnet. Lagres i en dataframe.
#         df_name_csv_files.loc[:, csv] = pd.Series(res_csv, dtype=str)
#     df_name_rs2_files = df_name_rs2_files.fillna(np.nan).replace([np.nan], [None])  # Tomme elementer får verdien None.
#     df_name_csv_files = df_name_csv_files.fillna(np.nan).replace([np.nan], [None])
#     df_list_path_rs2 = df_name_rs2_files.copy()  # ved = alene så vil endringer på den ene føre til samme endringer på den andre
#     df_list_path_csv = df_name_csv_files.copy()
#     i = 0
#     for rs2, csv in zip(name_rs2_folders,
#                         name_csv_folders):  # tilordner filnavn sine stier. Tomme elementer forblir tomme.
#         for file in df_list_path_rs2.index.values:
#             if df_name_rs2_files[rs2][file] is not None and df_name_csv_files[csv][file] is not None:
#                 folder_name_rs2 = path_storage_files + '/' + rs2 + df_name_rs2_files[rs2][file].replace('.fea', '')
#                 folder_name_csv = path_storage_files + '/' + csv + df_name_csv_files[csv][file].replace('.csv', '')
#                 os.mkdir(os.path.join(path_storage_files + rs2, folder_name_rs2))
#                 os.mkdir(os.path.join(path_storage_files + csv, folder_name_csv))
#                 df_list_path_rs2.loc[file, rs2] = folder_name_rs2 + '/' + df_name_rs2_files[rs2][file]
#                 df_list_path_csv.loc[file, csv] = folder_name_csv + '/' + df_name_csv_files[csv][file]
#                 # print(df_list_path_rs2[rs2][file])
#                 st.copyfile(path_file0_rs2[i], df_list_path_rs2[rs2][file])
#                 pd.DataFrame({}).to_csv(df_list_path_csv[csv][file])
#                 # path_feaFileMap = df_list_path_rs2[rs2][file].replace(".fea", '')
#                 # with zipfile.ZipFile(df_list_path_rs2[rs2][file], "r") as zip_ref:  # unzipping the .fea file
#                 #     zip_ref.extractall(path_feaFileMap)
#                 # for filename in os.listdir(path_feaFileMap):
#                 #     extension = pathlib.Path(filename).suffix
#                 #     # print(extension)
#                 #     source = path_feaFileMap + '/' + filename
#                 #     destination = path_feaFileMap + '/' + df_name_rs2_files[rs2][file].replace(".fea", '') + extension
#                 #     os.rename(source, destination)
#             else:
#                 continue
#         i += 1
#     return df_list_path_rs2, df_list_path_csv


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


def get_values_quad0(to_plot, points, query_positions):
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


def get_category(list_attributes, attribute_types, paths):
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
                if comb_str in path[1]:
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
    # for column in df:
    #     print(column)
    #     df[column] = df[column].apply(literal_eval)
    list_df_indices = get_start_index_df_value(parameter_navn, diff_navn)
    for k, (par_navn, enhet) in enumerate(zip(parameter_navn, fysiske_enheter)):
        for category, indices, type0 in zip(list_category, list_indices, attribute_type):
            df['category'] = category
            df['indices_true'] = indices
            groups = df.groupby('category')
            figure, axis = plt.subplots(1, 2)
            for i, diff_name in enumerate(diff_navn):
                axis[i].set_prop_cycle(color=color_map[type0])
                for z, (name, group) in enumerate(groups):
                    range0 = val_navn[list_df_indices[k][i]]
                    range1 = val_navn[list_df_indices[k][i]+1]
                    axis[i].plot(group['indices_true'], group[[range0]], marker="o", linestyle="", label=name)
                    # axis[i].plot(group['indices_true'], group[[range0]], marker="o", linestyle="--", label=name)
                    axis[i].plot(group['indices_true'], group[[range1]], marker="o", linestyle="", label=name)
                    axis[i].legend()
                    axis[i].set_xlabel('modellnummer')
                    axis[i].set_ylabel('differanse av ' + par_navn + ' ' + enhet)
                    axis[i].set_title('plot, differanse av ' + par_navn + 'sortert mhp. ' + type0 + ', ' + diff_name)
                    plt.savefig("difference_selection{}.png".format(z))
                # for j, txt in enumerate(df['indices_true']):
                #     axis[i].annotate(txt, (txt, df[diff_name][j]), fontsize=8)
                # plt.show()

    return


def plot_difference_selection(paths, parameter_navn, differanse_navn, fysiske_enheter, list_category, list_indices,
                              attribute_type, color_map):
    parameter_navn.pop()
    differanse_navn.pop(0)
    for par_navn, path, enhet in zip(parameter_navn, paths, fysiske_enheter):
        df = get_df_differences_from_csv(path)
        for k, (category, indices, type0) in enumerate(zip(list_category, list_indices, attribute_type)):
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
                    axis[i].plot(group['indices_true'], group[diff_name], marker="o", linestyle="-", label=name)
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
            # plt.show()
            plt.savefig("difference_selection{}.png".format(k))
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


def create_difference_csv(foldername_csv, list_differences, parameternavn_interpret, paths_fil_csv,
                          type_verdi, path_data_storage, twolines_no_corrupt):
    if all(path is None for path in paths_fil_csv):
        return None, None
    t = path_data_storage
    t = alternate_slash([t])[0]
    p = parameternavn_interpret.copy()
    p.pop()
    paths_2lines = []
    # for path in twolines_no_corrupt:
    #     p = path[1]
    #     z = re.findall(r'/(?:.(?!/))+$', p)[0][1:]
    #     paths_2lines.append(z)
    paths_2lines = [re.findall(r'/(?:.(?!/))+$', path[1])[0][1:] for path in twolines_no_corrupt]
    navn_2lines = [name.replace('.csv', '') for name in paths_2lines]
    # lager paths til der hvor differensene skal lagres
    paths = [[t + '/' + foldername_csv + type_verdi + '_' + navn.replace(':', '').replace(' ', '') + '.csv'] for navn in p]
    # df_differences = pd.DataFrame(columns=['file_name', 'quad_low', 'quad_high'])
    for navn, differences in zip(navn_2lines, list_differences):
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


def create_values_csv(foldername_csv, list_values_2line, list_values, parameternavn_interpret, paths_fil_csv,
                      elements_corrupted_files_2lines, type_verdi, path_data_storage, val_navn_2lines,
                      list_2lines_inside, sti_values_toplot_2lines, elements_corrupted_files, val_navn,
                      sti_values_toplot, parameters_varied, list_true_lengths):
    if all(path is None for path in paths_fil_csv):
        return None, None
    t = path_data_storage
    t = alternate_slash([t])[0]
    p = parameternavn_interpret.copy()
    p.pop()
    # fjerner de paths som er korruperte
    paths_2lines = get_paths_zone2lines(paths_fil_csv, elements_corrupted_files_2lines, list_2lines_inside)
    paths_2lines = [re.findall(r'/(?:.(?!/))+$', path[1])[0][1:] for path in paths_2lines]
    list_navn_2lines = [name.replace('.csv', '') for name in paths_2lines]
    paths = get_paths_without_corrupted(paths_fil_csv, elements_corrupted_files)
    list_navn_allines = [name.replace('.csv', '') for name in paths]
    list_varied_param_values = [get_parameter_values(navn, parameters_varied) for navn in list_navn_allines]
    list_varied_param_values_2lines = [get_parameter_values(navn, parameters_varied) for navn in list_navn_2lines]
    # lager paths til der hvor verdiene skal lagres
    path_2lines = t + '/' + foldername_csv + type_verdi + '.csv'
    path_all = t + '/' + foldername_csv + 'max_values.csv'
    list_to_df_2lines = []
    list_to_df = []
    for navn, values, varied_param_values_2lines, true_len in zip(list_navn_2lines, list_values_2line,
                                                                  list_varied_param_values_2lines, list_true_lengths):
        # d = list(map(list, zip(*differences)))  # transposes the list of lists
        list_to_df_2lines.append([navn] + [true_len] + varied_param_values_2lines + values)
    for navn, values, varied_param_values, true_len in zip(list_navn_allines, list_values, list_varied_param_values,
                                                 list_true_lengths):
        list_to_df.append([navn] + [true_len] + varied_param_values + values)
    df_values_2lines = pd.DataFrame(list_to_df_2lines, columns=val_navn_2lines)
    df_values_2lines.to_csv(path_or_buf=path_2lines, sep=';', mode='w', index=False)
    df_values_2lines.to_csv(path_or_buf=sti_values_toplot_2lines, sep=';', mode='a', index=False)
    df_values = pd.DataFrame(list_to_df, columns=val_navn)
    df_values.to_csv(path_or_buf=path_all, sep=';', mode='w', index=False)
    df_values.to_csv(path_or_buf=sti_values_toplot, sep=';', mode='a', index=False)
    return path_2lines, path_all


def get_parameter_values(navn_allines, params_varied):
    regex_shale = r'(?<=_{})\d*\.*\d*'
    param_values = []
    for param in params_varied:
        reg_pat = regex_shale.format(param)
        param_value = float(re.findall(reg_pat, navn_allines)[0])
        param_values.append(param_value)
    return param_values


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


def set_corrupted_files(file_paths, path_list_corrupted_files):
    file_sizes = get_list_size_files(file_paths)
    elements_corrupted_files = get_elements_small_files(file_sizes)
    corrupted_files = get_corrupted_file_paths(file_paths, elements_corrupted_files)
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
        return [None for i in file_paths]
    file_sizes = get_list_size_files(file_paths)
    elements = get_elements_small_files(file_sizes)
    if not elements:
        elements = [None for i in file_paths]
    return elements


def get_elements_corrupted_files_2lines(file_paths):
    if all(path is None for path in file_paths):
        return None
    file_sizes = get_list_size_files(file_paths)
    elements = get_elements_small_files(file_sizes)
    if not elements:
        elements = None
    return elements


# returns which of the parameters in the sensitivity study that are lists and returns a lis of the lists
def return_lists(list_attributes):
    checker = ['bm', 'ss', 'k', 'od', 'm', 'v', 'y', 'x']
    res = [elem for elem in zip(list_attributes, checker) if (isinstance(elem[0], list) and elem[1] not in
                                                              ['bm', 'ss', 'k', 'od'])]
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


def create_csv_2lines_info(list_0lines_inside, list_1line_inside, list_2lines_inside, list_excluded_files_2linescalc,
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


def clean_alt_list(list_):
    list_ = list_.replace(', ', '","')
    list_ = list_.replace('[', '["')
    list_ = list_.replace(']', '"]')
    return list_


def get_files_unsuc_tolerance(path_arbeidsfiler, list_navn_modell, path_store_unsuc_tol_models, tolerance):
    path_arbeidsfiler = alternate_slash([path_arbeidsfiler])[0]
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

    with open(path_store_unsuc_tol_models, 'w') as file:  #evt df to csv???
        file.writelines([f"{var1}\n" for var1 in list_unsucsesful_tolerance])
    return


class AddIt:

    """
    Add it er en iterator klasse. Hensikt: iterere over vektor for minste avstand fra senter sone til senter tunnel
    og legge til halvemektigheten slik at lineament nærest tunnelsenter alltid er på samme sted uavhengig av mektigheten

    Viktig:
    Sentinel: markerer slutten for objektet og vil være tilordnet: sentinel = object(), med mindre noe annet er definert
    """

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


def get_x_distance(normalized_distance_list, zone_angle, mektighet):
    zone_angle = np.deg2rad(zone_angle)
    sentinel = object()
    ai = AddIt(normalized_distance_list, mektighet, sentinel)
    x_distance_list = []
    for i in iter(ai, sentinel):
        x_distance_list.append(round(i/np.sin(zone_angle), 2))
    return x_distance_list


def create_csv_files(sti_arbeidsfiler, parameter_verdier_csv):
    sti_arbeidsfiler = alternate_slash([sti_arbeidsfiler])[0]
    fname_list = make_file_name(parameter_verdier_csv)
    for fname in fname_list[1]:
        with open(sti_arbeidsfiler + fname, 'w') as my_new_csv_file:
            pass
    return


def open_csv_files(sti_exe, sti_csv_stier):
    from subprocess import Popen
    with open(sti_csv_stier, 'r') as file:
        liste_csv_stier = file.readlines()
    for csv_sti in liste_csv_stier:
        Popen([sti_exe, csv_sti.replace('\n', ' ')])
    return

