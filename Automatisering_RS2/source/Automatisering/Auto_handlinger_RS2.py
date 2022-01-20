import pyautogui as pag


time_list = [0, 0.5, 1, 2, 5]


def klargjore_rs2(df_koordinater_mus, navn_kol, i=0, time=None):
    if time is None:
        time = time_list
    pag.click(df_koordinater_mus[navn_kol[1]][i], df_koordinater_mus[navn_kol[2]][i], interval=time[0])  # muliggjør hurtigtaster
    i += 1
    pag.press('enter', interval=time[0])
    pag.press('f2', interval=time[0])  # sørge for at prosjektet er zoomet helt ut
    pag.hotkey('ctrl', 'r', interval=time[2])  # fjerne mesh
    return i





def rotere_svakhetssone(df_endrede_attributter_rs2filer, mappenavn_til_stikategori, j, df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    pag.hotkey('ctrl', 'shift', 'r', interval=time[1])  # verktøy: rotate boundary
    vinkel = df_endrede_attributter_rs2filer[mappenavn_til_stikategori][j]['v']
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velg grense som ska roteres
    pag.press('enter', interval=time[0])
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # rotasjonspunkt
    pag.write(vinkel, interval=time[2])
    pag.press('enter', interval=time[2])  # utføre handling
    pag.press('enter', interval=time[2])  # fjerne eventuell melding om at ingenting har skjedd
    return i


def forflytning_svakhetssone(df_endrede_attributter_rs2filer, mappenavn_til_stikategori, j, df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    forflytning_x = df_endrede_attributter_rs2filer[mappenavn_til_stikategori][j]['x']
    forflytning_y = df_endrede_attributter_rs2filer[mappenavn_til_stikategori][j]['y']
    pag.press('f2', interval=time[0])  # sørge for at prosjektet er zoomet helt ut
    pag.hotkey('ctrl', 'shift', 'b', interval=time[2])  # verktøy: move boundary
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velge grense som ska flyttes
    pag.press('enter', interval=time[2])
    pag.hotkey('altright', '2')
    pag.write('({}, {})'.format(forflytning_x, forflytning_y), interval=time[1])
    pag.press('enter', interval=time[2])  # utføre handling
    pag.press('enter', interval=time[2])  # fjerne eventuell melding om at ingenting har skjedd
    return i


def skalering_svakhetssone(df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    pag.press('f6', interval=time[0])  # zoomer in siden de to grensene som skaleres må skaleres hver for seg.
    pag.hotkey('ctrl', 'shift', 's', interval=time[1])  # hurtigtast for funksjonen scale boundary

    # velge grenser skalering 1
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velge grenser skalering 1
    pag.press('enter', interval=time[0])
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velge senter for skalering 1
    pag.write('(100,100)', interval=time[1])  # skalering i x og y valgt stort for å sikre at det alltid går bra
    # Disse linjene blir kuttet når de treffer ytre grense.
    pag.press('enter', interval=time[0])  # utfører handlingen.

    pag.hotkey('ctrl', 'shift', 's', interval=time[0])  # hurtigtast for funksjonen scale boundary

    # velge grenser skalering 2
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velge grenser skalering 2
    pag.press('enter', interval=time[1])
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[0])  # velge senter for skalering 2
    pag.write('(100,100)', interval=time[1])  # skalering i x og y valgt stort for å sikre at det alltid går bra
    # Disse linjene blir kuttet når de treffer ytre grense.
    pag.press('enter', interval=time[1])  # utfører handlingen.
    pag.press('f2', interval=time[0])  # zoomer ut for å komme tilbake til grunnstørrelsen
    return i


def utgraving(df_koordinates_mouse, name_col_df, i=0, time=None):
    if time is None:
        time = time_list
    pag.press('f6', interval=time[0])  # zoomer in siden de to grensene som skaleres må skaleres hver for seg.
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[1])  # velge stage: initial

    # initial stage
    # tilordne GSI 80 til de rette stedene, der hvor det er "inntakt" berg. GSI80
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI80

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI80

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI80

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI80


    # tilordne GSI 1 til de rette stedene, der hvor det er svakhetssone. GSI1
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI1

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI1

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: GSI1


    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[1])  # velge stage: excavation
    # excavation stage
    # graver ut tunnelen ved å tilordne dem ingen materiale.
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: excavation

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: excavation

    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2], button='right')  # høyreklikke musa, velge materialet
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge uttreksmenyen: assign material
    i += 1
    pag.click(df_koordinates_mouse[name_col_df[1]][i], df_koordinates_mouse[name_col_df[2]][i], interval=time[2])  # velge materialet å tilordne: excavation

    pag.press('f2', interval=time[0])  # zoomer ut for å komme tilbake til grunnstørrelsen.
    return i


def interpret_resultat_til_clipboard(time=None):
    if time is None:
        time = time_list
    pag.press('f6', interval=time[2])
    pag.click(754, 527, interval=time[1], button='right')
    pag.click(846, 666, interval=time[1])
    return