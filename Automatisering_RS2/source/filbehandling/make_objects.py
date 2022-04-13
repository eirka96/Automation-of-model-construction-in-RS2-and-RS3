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


def get_file_paths_batch():
    l = [25, 100, 200, 300, 500, 800, 1000]
    sti_kildefil_rs2 = []
    sti_kildefil_csv = []
    for i in l:
        sti_kildefil_rs2.append(
            r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine " \
            r"modeller\RS2\tverrsnitt_sirkulær\sirkulær_mal\mal_S_bm80_ss1_k1_od{}" \
            r"\S_bm80_ss1_k1_od{}_v0_m2_mal\S_bm80_ss1_k1_od{}_v0_m2_mal.fea ".format(i, i, i))
        sti_kildefil_csv.append(r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave"
                                r"\modellering_svakhetssone\parameterstudie\excel\Pycharm_automatisering"
                                r"\parameter_verdier_filnavn.csv ")
    return sti_kildefil_rs2, sti_kildefil_csv


def get_original_file_paths():
    l = [25, 100, 200, 300, 500, 800, 1000]
    sti_kildefil_rs2 = []
    sti_kildefil_csv = []
    for i in l:
        sti_kildefil_rs2.append(
            r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine " \
            r"modeller\RS2\tverrsnitt_sirkulær\sirkulær_mal\mal_S_bm80_ss1_k1_od{}" \
            r"\S_bm80_ss1_k1_od{}_v0_m2_mal\S_bm80_ss1_k1_od{}_v0_m2_mal.fea ".format(i, i, i))
        sti_kildefil_csv.append(r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave"
                                r"\modellering_svakhetssone\parameterstudie\excel\Pycharm_automatisering"
                                r"\parameter_verdier_filnavn\S_bm80_ss1_k1_od{}\S_bm80_ss1_k1_od{}.csv ".format(i, i))
    return sti_kildefil_rs2, sti_kildefil_csv


# make_file_name har til hensikt å lage de filnavn tilhørende RS2-prosjekter
# funksjonen skal returnere en liste med  alle filnavn på denne formen her:


# Input:

# parameter_navn:
# er en liste av strenger som inneholder de parametere som er definert i excel-fila anvist over, foruten
# geometri som ikke har en tallverdi knyttet til seg.
# parameter_verdier_excel:
# er en streng som inneholder pathen til excel-fila der verdiene til de tilhørende parameternavnene er lagret.
# geometri:
# inneholder informasjon om tunnelens geometri: s for sirkulær og hs for hestesko. Denne er satt deafult til sikrulær


# Andre parametere: df_verdier: dataframe som inneholder verdiene som tilhører de ulike parameternavnene
# file_name_liste: liste som tilslutt inneholder alle filnavnene tilhørende rs2-prosjektene som skal opprettes. path:
# er variabelen som brukes til å bygge opp hver enkelt streng som tilsammen resulterer i et filnavn for et gitt
# rs2-prosjekt.

# returnerer:
# file_name_list


def make_file_name(parameter_verdier_csv, geometri='S'):
    # parameter_verdier_csv = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
    #                         r"\parameterstudie" \
    #                         r"\excel\Pycharm_automatisering\parameter_verdier_filnavn.csv "
    df_verdier = pd.read_csv(parameter_verdier_csv, sep=';')
    parameter_navn = df_verdier.columns.values.tolist()
    file_name_rs2_list = []
    file_name_excel_list = []
    for i in range((df_verdier.shape[0])):
        path = ''
        path += (geometri + "_")

        for navn in parameter_navn:
            path += (navn + str(df_verdier[navn][i]) + "_")
            # if navn == 'y' or navn == 'x':
            #     if df_verdier[navn][i] == 0:
            #         path = path.replace((navn + str(df_verdier[navn][i]) + "_"), "")
        path = path[:-1]
        path1 = path
        path += '.fea'  # denne er eneste forskjellen mellom make_folder_name og make_file_name
        path1 += '.csv'
        file_name_rs2_list.append(path)
        file_name_excel_list.append(path1)
    return file_name_rs2_list, file_name_excel_list


# beskrivelsen for denne er identisk med den over bare at denne er tilpasset for mappenavn
# parameter_verdier_excel har en annen sti og det blir ikke lagt til .fea i enden av navnet.

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


# hensikten med get_path_folders er å hente stier på de mapper som RS2-filene skal bli lagret i
# mappenavn kommer til å være definert utifra de parametere som til en hver tid holdes konstant/skiftes sjeldent,
# samt en hovedsti.


# parametere:
# main_path:
# er en streng og er pathen til der hvor de ulike mappene og filene skal lagres. Må sørge for at det er en
# backslash i slutten av strengen
# list_folders:
# liste som inneholder navnene til alle mapper som er relevante for lagring av de produserte RS2-filer


# returnerer:
# list_folders

def get_name_folders(path_storage_files):
    path_storage_files = alternate_slash([path_storage_files])[0]
    list_folders = os.listdir(path_storage_files)  # henter de mappenavn som ligger i main_path
    list_folders.sort(key=len)  # sørger for at mappenavnene blir sortert i stigende rekkefølge
    list_csv_folders, list_rs2_folders = [s + '/csv/' for s in list_folders], [s + '/rs2/' for s in list_folders]
    # må endres hvis mappestrukturen endres!!!!!!
    return list_rs2_folders, list_csv_folders


# alternate_slash bytter ut alle bakstreker i hver streng av en liste med strenger og gjør dem om til skråstreker
# og omvendt.
# hensikt: formatet til stiene som skiller mappenavn med bakstreker blir ikke forstått av python som forstår skråstreker
#          Derfor er det nødvendig med en kornvertering.
# Hvis input ikke kun består av stier der mappenavn blir kun skilt av bakstreker eller skråstreker,
# så stopper funksjonen å kjøre og ingen endring blir oppnådd.


# input:
# list_path:
# liste over stier til gitte objekter.


# andre parametere:
# find_backslash:
# for hver sti som inneholder bakstrek blir et nytt element lagt til i denne lista.
# find_frontslash:
# for hver sti som inneholder skråstrek blir et nytt element lagt til i denne lista.


# returnerer:
# -1 hvis en feil har oppstått
# list_path hvis alt gikk bra


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


# copy_and_store:
# er en funksjon som tar get_path_folders, make_file_name og alternate_slash i bruk.
# Hensikten er å gjøre klar alle filer som skal igjennom sine respektive endringer i RS2.
# Gi de tenkte RS2-filene navn som tilsvarer hvordan modellen i et gitt tilfelle skal se ut,
# så bestemme i hvilken mappe en gitt fil tilhører for tilslutt å kopiere kildefila n ganger, der hver kopi blir
# tilordnet hver sin sti. Mao. ingen av filene er klargjort etter å ha kalt på denne funksjonen
# Denne funksjonen oppretter også et excel ark til hver enkelt fil. Der skal lister med resultater lagres.


# input:
# de som er gitt i funksjonene over.
# path_file0 viser til kildefilens sti


# andre parametere:
# list_name_folders:
# Liste av navnene til mappene som RS2_fil_stiene skal lagres i
# list_rs2_file_names:
# Liste over alle stiene til RS2_filene
# df_name_files:
# En pandas dataframe som er en 2-dimensjonal matrise med mange tillegsfunksjoner.
# I denne er rs2_fil-lagret lagret i de mappene de hører hjemme ved at rs2_filnavnet blir tilordnet den kolonne
# som har den rette label gitt av mappenavnet.
# df_list_path_files:
# Er eksakt lik som df_name_files bare at denne inneholder stien til RS2-fila.


# returnerer:
# navnet til mappene og dataframe med filplasseringene, samt dataframe med filnavnene.
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


# get_changing_attribute:
# henter ut de attributter som skal endres i RS2-fila, disse blir returnert som en streng


# input:
# df_name_files:
# en dataframe som inneholder alle filnavn kategorisert etter mappe. Hver mappe har sin egen kolonne
# Tomme celler har verdien None.
# folder_names:
# innehar navnene på hver enkelt mappe


# andre parametere:
# df_marker_of_change:
# dataframe som til slutt kun innehar informasjonen om hvordan hver enkelt fil skal endres.
# Denne informasjonen er selv lagret i en dataframe. 1. kolonne inneholder type-informasjon
# og 2. kolonne inneholder verdien til denne typen. Tilsammen beskriver en rad i df hvilken endring
# som gjelder for en bestemt type.


# returnerer:
# df_marker_of_change

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
            print(attributes)
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
        points = [float(points_string[0]), float(points_string[1])]
        prepped_data.append(points)
    return prepped_data


def get_parameter_to_plot(path_to_csv, parameternavn):
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
        p = prep_strings_to_float(p)
        data_split.append(p)
    return data_split


def get_difference(data, indices):
    if data is None:
        return None
    diff1, diff2 = [], []
    for data_sep in data:
        diff1.append(abs(data_sep[indices[0]][1] - data_sep[indices[1]][1]))
        diff2.append(abs(data_sep[indices[2]][1] - data_sep[indices[3]][1]))
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


def make_container_diff(mappenavn_rs2):
    container = []
    for i in range(len(mappenavn_rs2)):
        container.append([])
    return container


def get_filenames_col_rs2(paths_fil_rs2, path_arbeidsmappe):
    path_arbeidsmappe = alternate_slash([path_arbeidsmappe])[0]
    file_names_rs2 = [path.replace(path_arbeidsmappe + '/', '') for path in paths_fil_rs2 if isinstance(path, str)]
    file_names_rs2 = [path.replace('.fea', '') for path in file_names_rs2]
    return file_names_rs2


def create_difference_csv(foldername_csv, list_differences, parameternavn_interpret, paths_fil_rs2, path_arbeidsmappe):
    if all(path is None for path in paths_fil_rs2):
        return
    t = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie" \
        r"\Mine modeller\RS2\tverrsnitt_sirkulær\sluttprodukt\ "
    t = alternate_slash([t])[0]
    filnavn_rs2 = get_filenames_col_rs2(paths_fil_rs2, path_arbeidsmappe)
    p = parameternavn_interpret.copy()
    p.pop()
    paths = [[t + foldername_csv + 'differenser' + '_' + navn.replace(':', '').replace(' ', '') + '.csv'] for navn in p]
    # df_differences = pd.DataFrame(columns=['file_name', 'quad_low', 'quad_high'])
    for navn, differences in zip(filnavn_rs2, list_differences):
            d = list(map(list, zip(*differences)))  # transposes the list of lists
            for path, difference in zip(paths, d):
                path.append([navn] + difference)
    # df_differences.to_csv(path_or_buf=path, sep=';', mode='w')
    for path in paths:
        j = path[1:]
        df_difference = pd.DataFrame(j, columns=['file_name', 'quad_low', 'quad_high'])
        df_difference.set_index('file_name', inplace=True)
        df_difference.to_csv(path_or_buf=path[0], sep=';', mode='w')
    return


# path_arbeidsmappe = r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone" \
#                     r"\parameterstudie\Mine modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler "
# folder_name = "S_bm80_ss1_k1_od500/csv/"
# stier = pd.Series([r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x0.csv ",
# r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x1.csv ",
# r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x2.csv ",
# r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x3.csv "	])
# parameternavn = ['sigma 1:\n', 'total deformasjon:\n', 'end\n']
#
# paths_rs2 = pd.Series([alternate_slash([r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x0.fea "])[0],
# alternate_slash([r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x1.fea "])[0],
# alternate_slash([r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x2.fea "])[0],
# alternate_slash([r"C:\Users\Eirik\OneDrive\Documents\10.Prosjekt_og_masteroppgave\modellering_svakhetssone\parameterstudie\Mine "
#                      r"modeller\RS2\tverrsnitt_sirkulær\arbeidsfiler\S_bm80_ss1_k1_od500_m5_v22.5_y0_x3.fea "])[0]])
# indices = [59, 125, 284, 350]
# par_navn = ['sigma 1:', 'total deformasjon:', 'end']
# differences = []
# for sti, fil in zip(stier, paths_rs2):
#     data = get_parameter_to_plot(sti, parameternavn)
#     difference = get_difference(data, indices)
#     if difference is not None:
#         differences.append(difference)
#     plot_data(data, parameternavn)
#     parameternavn = ['sigma 1:\n', 'total deformasjon:\n', 'end\n']
#
# create_difference_csv(folder_name, differences, par_navn, paths_rs2, path_arbeidsmappe)
