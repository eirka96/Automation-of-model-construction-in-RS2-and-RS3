# import Automatisering_RS2.source.filbehandling.make_objects as mo
from Automatisering_RS2.source.alter_geometry.model_construction import model_construction_RS2 as mc
import numpy as np
from Automatisering_RS2.source.filbehandling import make_objects as mo


"""
alter_geometry sørger for alle manipulasjoner av geometrien definert av en kildefil. Den leser av hvilke parametere som
endres ved å lese av filnavnet, og sørger for implementere disse endringene ved å endre på kildekoden til den respektive 
fil.
"""


def alter_geometry(vinkel_sone, forflytning_x_sone, forflytning_y_sone, mektighet_sone, path_of_RS2_file,
                   ant_pkt_sone_ytre=4, ant_linjer_sone=2, diameter_tunnel=10,
                   n_points_tunnel_boundary=360, ytre_grenser_utstrekning=150):
    # henter kildefilen til RS2, lagret som .fea
    with open(path_of_RS2_file, 'r') as file:
        data = file.readlines()
    # henter nøkkelelementer i listen data bassert på unike nøkkelord, som blir brukt til å navigere tekseditoren
    index_material_mesh = data.index("materials mesh start:\n") + 3
    index_boundary1 = data.index("  boundary 1 start:\n") + 6
    points_tunnel_boundary0 = data[45753:46113].copy()
    # making list of points stored as float:
    points_tunnel_boundary = mc.prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1)
    # definerer hvilke punkter i tunnel_boundary som tilhører hvilken matematiske kvadrant.
    fourth_quad = points_tunnel_boundary[0:90]
    first_quad = points_tunnel_boundary[90:180]
    second_quad = points_tunnel_boundary[180:270]
    third_quad = points_tunnel_boundary[270:359]
    quad = (fourth_quad, first_quad, second_quad, third_quad)

    # mektighet, legges til før forflytning og rotasjon, og endrer kun y-verdi siden sonen i utgangspunktet er horisontal
    x_hoyre = ytre_grenser_utstrekning
    x_venstre = -ytre_grenser_utstrekning
    y_topp = mektighet_sone / 2
    y_bunn = -mektighet_sone / 2

    # definerer svakhetssonen basert på de ytre grensebetingelsene:

    if vinkel_sone != 0:
        theta = np.deg2rad(vinkel_sone)
        matr = np.array([[np.cos(theta), -np.sin(theta), forflytning_x_sone], [np.sin(theta), np.cos(theta), forflytning_y_sone]])
        punkt_bunn_hoyre = np.matmul(matr, np.array([x_hoyre, y_bunn, 1]))
        punkt_topp_hoyre = np.matmul(matr, np.array([x_hoyre, y_topp, 1]))
        punkt_topp_venstre = np.matmul(matr, np.array([x_venstre, y_topp, 1]))
        punkt_bunn_venstre = np.matmul(matr, np.array([x_venstre, y_bunn, 1]))
        punkter_topp = [punkt_topp_hoyre, punkt_topp_venstre]
        punkter_bunn = [punkt_bunn_hoyre, punkt_bunn_venstre]
        if mc.OuterBoundary.check_points_ob(punkter_topp, punkter_bunn, ytre_grenser_utstrekning):
            print('Advarsel: svakhetssonen er utenfor de ytre grensene tilhørende modellen. Scriptet ble stanset.')
            quit()
        ytre_topp_hoyre, ytre_topp_venstre = mc.OuterBoundary.find_points_on_outer_boundary(punkt_topp_hoyre,
                                                                                            punkt_topp_venstre,
                                                                                            ytre_grenser_utstrekning, ant_linjer_sone)
        ytre_bunn_hoyre, ytre_bunn_venstre = mc.OuterBoundary.find_points_on_outer_boundary(punkt_bunn_hoyre,
                                                                                            punkt_bunn_venstre,
                                                                                            ytre_grenser_utstrekning, ant_linjer_sone)

        len_topp = np.sqrt(
            (ytre_bunn_venstre[0] - ytre_bunn_hoyre[0]) ** 2 + (ytre_bunn_venstre[1] - ytre_bunn_hoyre[1]) ** 2)
        len_bunn = np.sqrt(
            (ytre_topp_venstre[0] - ytre_topp_hoyre[0]) ** 2 + (ytre_topp_venstre[1] - ytre_topp_hoyre[1]) ** 2)

        if len_topp < 5 or len_bunn < 5:
            print('Advarsel: svakhetssonens utstrekning er for liten, prøv igjen. Scriptet ble stanset.')
            quit()
    else:
        ytre_bunn_hoyre = [x_hoyre, y_bunn + forflytning_y_sone]
        ytre_topp_hoyre = [x_hoyre, y_topp + forflytning_y_sone]
        ytre_topp_venstre = [x_venstre, y_topp + forflytning_y_sone]
        ytre_bunn_venstre = [x_venstre, y_bunn + forflytning_y_sone]

        if ytre_bunn_hoyre[1] < -ytre_grenser_utstrekning or ytre_topp_hoyre[1] > ytre_grenser_utstrekning:
            print('Advarsel: svakhetssonen er utenfor de ytre grensene tilhørende modellen. Scriptet ble stanset.')
            quit()

    punkter_ytre = [ytre_bunn_hoyre, ytre_topp_hoyre, ytre_topp_venstre, ytre_bunn_venstre]
    # indre grense, definerer punktene på tunnel_boundary og svakhetssonen

    ib = mc.InnerBoundary(ant_linjer_sone, quad, punkter_ytre, data, n_points_tunnel_boundary, index_boundary1, diameter_tunnel, vinkel_sone,
                          points_tunnel_boundary, ytre_grenser_utstrekning)
    if ib.inner_points:
        punkter_indre = ib.get_points_on_circular_boundary_2()
        ib.set_inner_boundary()
    else:
        punkter_indre = ib.get_points_on_circular_boundary_2()

    # sette startspunkt for endringer av de tre siste boundaries
    index_boundary2 = data.index("  boundary 2 start:\n") + 6
    index_boundary3 = data.index("  boundary 3 start:\n") + 6
    index_boundary4 = data.index("  boundary 4 start:\n") + 6

    # endre boundary i kildekoden til RS2, element 2 - ytre grense
    mc.OuterBoundary(punkter_ytre, data, index_boundary2, vinkel_sone, ant_pkt_sone_ytre, ytre_grenser_utstrekning)

    # endre boundary (svakhetssone) i kildekoden til RS2, element 3 og 4 - hhv. bunn og topp
    bl = mc.BoundaryLines(punkter_ytre, punkter_indre, index_boundary3, index_boundary4, data, ant_linjer_sone)
    bl.set_weakness_points()

    points_tunnel_boundary0 = data[45753:45753+ib.n_points_ib].copy()
    # making list of points stored as float:
    points_tunnel_boundary = mc.prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1)
    # indekser der data skal hentes ut blir her bestemt, returneres til main
    points_to_check = bl.sort_weakness_points()
    # endre materials mesh i kildekoden til RS2, element 1
    mls = mc.Materials(index_material_mesh, punkter_indre, ytre_grenser_utstrekning, ant_linjer_sone, quad, punkter_ytre, data,
                       n_points_tunnel_boundary, index_boundary1, diameter_tunnel, vinkel_sone, points_tunnel_boundary,
                       forflytning_y_sone, forflytning_x_sone)
    mls.setmaterialmesh()
    # and write everything back
    with open(path_of_RS2_file, 'w') as file:
        file.writelines(data)
    return points_to_check


"""
get parameters kalles på hvis det skal gjøres videre bearbeiding av et allerede eksisterende experiment. For eksempel 
hvis det har blitt gjort endringer på et mesh som fører til ny kalkulasjon og informajsoninnhenting fra interpret. Den
sørger for å returnere de punkter hvor linjelementene som definerer svakhetssonen krysser tunnelkonturen.
"""


def get_parameters(df_stier_rs2filer, mappenavn_til_rs2, mappenavn_til_csv):
    points_to_check = []
    p = 4
    i = 0
    for navn_rs2, navn_csv in zip(mappenavn_til_rs2, mappenavn_til_csv):
        points_to_check.append([])
        for j in range(df_stier_rs2filer.shape[0]):
            if j == 135 or j == 149:
                p = 2
            path_fil_rs2 = df_stier_rs2filer[navn_rs2][j]
            if isinstance(path_fil_rs2, str):
                with open(path_fil_rs2, 'r') as file:
                    data = file.readlines()
                # henter nøkkelelementer i listen data bassert på unike nøkkelord, som blir brukt til å navigere tekseditoren
                index_boundary1 = data.index("  boundary 1 start:\n") + 6
                index_boundary3 = data.index("  boundary 3 start:\n") + 6
                index_boundary4 = data.index("  boundary 4 start:\n") + 6
                points_tunnel_boundary0 = mo.get_tunnel_boundary_points(data, index_boundary1)
                # making list of points stored as float:
                points_tunnel_boundary = mc.prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1)
                points_wb3 = data[index_boundary3:index_boundary3+p].copy()
                points_wb4 = data[index_boundary4:index_boundary4+p].copy()
                points_wb3 = mc.prep_points_tunnel_boundary(points_wb3, data, index_boundary3)
                points_wb4 = mc.prep_points_tunnel_boundary(points_wb4, data, index_boundary4)
                if j == 135 or j == 149:
                    points_to_check[i].append(None)
                else:
                    points_to_check[i].append([points_wb3[1], points_wb3[2], points_wb4[1], points_wb4[2]])
                p = 4
        i += 1
        p = 4
    return points_to_check

