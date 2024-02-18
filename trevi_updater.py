"""
Update my DB with the new costs
This program is dependant on:
    "Provedores Todos.xlsm" ----> My DB
    "pedido.xlsx" ----> downloaded by trevi_order.py (it's the ordered place to the provider)
    "trevi_full.xlsx" ----> it's the list scraped by trevi_spider.py (all the provider's prices from the website)
"""
import pandas as pd
import gc
import datetime

# Start with an emprty df
new_df = pd.DataFrame()

# Read my DB
my_df = pd.read_excel("C:\\Users\\casa\\Desktop\\Provedores Todos.xlsm", sheet_name="Datos", index_col=0, na_values="--", skipfooter=10, usecols="A:AG")
my_df = my_df[my_df["Provedor"] == "Treviño"]

# From my DB 
new_df["Name"] = my_df["Descripción"]
new_df["Ref"] = my_df["TVENTA_TREVI"]
new_df["Key"] = my_df["Clave Provedor"]
new_df["Unitary"] = my_df["Costo Unitario"]
new_df["Total"] = my_df["Total"]
new_df["Pieces"] = my_df["Piezas"]
new_df["Sub"] = my_df["Subtotal"]
new_df["Date"] = my_df["Última Rev. Costos"]

# Clear memory
del my_df
gc.collect()

# Read ordered placed
order_df = pd.read_excel("pedido.xlsx")
order_df.rename(columns={"Clave": "Key"}, inplace=True)

# From ordered_df push Quantity ordered in the correct row
new_df.set_index("Key", inplace=True)
order_df.set_index("Key", inplace=True)
new_df.loc[new_df.index.intersection(order_df.index), "Cantidad"] = order_df["Cantidad"]
new_df.reset_index(inplace=True)

# Clear memory
del order_df
gc.collect()

# Correct quantity
for idx, row in new_df.iterrows():
    if not pd.isna(row["Cantidad"]):
        ref = (row["Ref"].split("-"))[0]
        if ref == "U":
            new_df.loc[idx, "Cantidad"] = new_df.loc[idx, "Cantidad"] * new_df.loc[idx, "Pieces"] 


# Read trevi_df
trevi_df = pd.read_excel("trevi_full.xlsx")
trevi_df.rename(columns={"SKU": "Key"}, inplace=True)
trevi_df.set_index("Key", inplace=True)
trevi_df.drop("Name", axis=1, inplace=True)

# Merge trevi's full prices list with my price list on key
merged_df = new_df.merge(trevi_df, how="left", on="Key")
merged_df.set_index("Key", inplace=True)
merged_df.drop("Unnamed: 0", axis=1, inplace=True)

# Clear memory
del trevi_df
gc.collect()

# Set new price data based on the price ranges from trevi's website
merged_df["New Price"] = ""
def get_new_price(row):
    quantity = row["Cantidad"]
    new_price = 0
    i = 1
    if not isinstance(row["ranges"], str):
        if not pd.isna(row["Base"]):
            new_price = float((str(row["Base"]).replace("$", "")))
            return new_price
        else:
            return "NA"
    else:
        ranges = row["ranges"].split("-")
        for x in ranges:
            x = x.strip()
            x = x.replace("a", "")
            x = x.split()
            if int(quantity) <= int(x[-1]):
                new_price = float(row[f"{i}"].replace("$", ""))
                break
            i += 1
        return new_price
for idx, row in merged_df.iterrows():
    if not pd.isna(row["Cantidad"]):
        merged_df.loc[idx, "New Price"] = get_new_price(row)
    else:
        merged_df.loc[idx, "New Price"] = "NA"

# Set New subtotal to replace my existing subtotal column 
merged_df.reset_index(inplace=True)
merged_df["New Subtotal"] = 0
for idx, row in merged_df.iterrows():
    ref1 = (row["Ref"].split("-"))[0]
    ref2 = (row["Ref"].split("-"))[1]
    if merged_df.loc[idx, "New Price"] != "NA":
        if ref1 == "T":
            if ref2 == "NA":
                merged_df.loc[idx, "New Subtotal"] = round(merged_df.loc[idx, "New Price"], 2)
            elif ref2 == "IV":
                merged_df.loc[idx, "New Subtotal"] = round(merged_df.loc[idx, "New Price"] / 1.16, 2)
            elif ref2 == "IE":
                merged_df.loc[idx, "New Subtotal"] = round(merged_df.loc[idx, "New Price"] / 1.08, 2)
        elif ref1 == "U":
            if ref2 == "NA":
                merged_df.loc[idx, "New Subtotal"] = round(merged_df.loc[idx, "New Price"] * merged_df.loc[idx, "Pieces"], 2)
            elif ref2 == "IV":
                merged_df.loc[idx, "New Subtotal"] = round((merged_df.loc[idx, "New Price"] / 1.16) * merged_df.loc[idx, "Pieces"], 2)
            elif ref2 == "IE":
                merged_df.loc[idx, "New Subtotal"] = round((merged_df.loc[idx, "New Price"] / 1.08) * merged_df.loc[idx, "Pieces"], 2)
    else:
        merged_df.loc[idx, "New Subtotal"] = merged_df.loc[idx, "Sub"]
    merged_df.loc[idx, "Date"] = f"{datetime.date.today().day}/{datetime.date.today().month}/{datetime.date.today().year}"

merged_df.to_excel("Final.xlsx")
