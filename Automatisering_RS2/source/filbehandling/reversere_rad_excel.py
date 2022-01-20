import pandas as pd

tekst = 'invertere-liste.xlsx'

x = pd.read_excel(tekst)

print(x)

print(type(x))

x = x.sort_index(axis=1, ascending=True)  # får pandas til å lete radvis istedet for kolonnevis

x = x.iloc[::-1]  # reverserer rekkefølgen
print(x)
writer = pd.ExcelWriter(tekst, engine='xlsxwriter')  # skriver inn i den gitte excelfil
x.to_excel(writer, sheet_name='sheet1', index=False)
writer.save()
