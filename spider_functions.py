
def crawl():
	"""
	Scrape the prices from providers's website
	"""
	# V-2.2
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.wait import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import pandas as pd

	# Initial variables
	links = list()
	products = list()
	i = 1
	last_page = False

	# Begin scraping
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')

	driver = webdriver.Chrome(options=options)
	driver.get("https://comercialtrevino.com/products-all.html")

	# Select the correct store
	el_city = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "selected_city")))
	all_opt = el_city.find_elements(By.TAG_NAME, "option")
	for option in all_opt:
		if option.get_attribute("value") == "1":
			correct_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(option))
			correct_option.click()
	el_select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "selectDealer_1")))
	el_select.click()

	# Collect all links
	while True:
		el_links = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.product_title a")))
		for link in el_links:
			link = link.get_attribute("href")
			if link in links:
				last_page = True
				break
			links.append(link)
		if last_page is True:
			break
		i += 1
		driver.get(f"https://comercialtrevino.com/products-all.html?disp_order=1&page={i}")
		
	# Nav and Extract
	for link in links:
		product = dict()
		ranges = list()
		j = 1
		driver.get(link)

		# Get code
		el_sku = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "pdl_model")))
		sku = ((el_sku.text).replace('SKU: ', '')).strip()
		product["SKU"] = sku

		# Get name
		el_name = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "productName")))
		name = el_name.text
		product["Name"] = name

		# Get base price
		try:
			el_base = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#productPrices span.productBasePrice")))
		except:
			el_base = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#productPrices span.productSpecialPrice")))
		product["Base"] = el_base.text

		# Get prices
		el_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
		for row in el_rows:
			key = row.find_element(By.CSS_SELECTOR, "td.text-left")
			value = row.find_element(By.CSS_SELECTOR, "td.product_price")
			product[f"{j}"] = value.text
			key = key.text
			key = key.replace("De ", "")
			key = key.replace(" productos", "")
			key = key.replace(" o más", "")
			key = key.replace(",", "")
			ranges.append(key)
			j += 1
		product["ranges"] = "- ".join(ranges)
		products.append(product)

	# Finish escraping
	driver.quit()

	# Export feed
	trevi_df = pd.DataFrame.from_dict(products)
	with pd.ExcelWriter('trevi_full.xlsx') as writer:
		trevi_df.to_excel(writer)

def get_order():
	"""
	Download the ordered list with GMAIL-API 

	"""
	import os
	import base64
	from google.auth.transport.requests import Request
	from google.oauth2.credentials import Credentials
	from google_auth_oauthlib.flow import InstalledAppFlow
	from googleapiclient.discovery import build
	from googleapiclient.errors import HttpError

	SCOPES = [
		"https://www.googleapis.com/auth/gmail.readonly"
	]

	# Get gmail authorization
	creds = None
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	if not creds or not creds.valid:
		try:
			os.remove("token.json")
		except:
			print("Exception!")
		
		flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
		creds = flow.run_local_server(port=0)
		with open("token.json", "w") as token:
			token.write(creds.to_json())
	 
	try:
		# Build
		service = build("gmail", "v1", credentials=creds)
		# Get correct message id
		result = service.users().messages().list(
			userId="me",
			labelIds=["INBOX"],
			q="filename:pedido.xlsx",
			maxResults=1
		).execute()
		messages = result.get("messages", [])
		msg_id = messages[0]["id"]
		# Get correct message
		message = service.users().messages().get(
			userId="me",
			id=msg_id
		).execute()
		# Export attachment
		for part in message["payload"]["parts"]:
			if part["filename"]:
				if "data" in part["body"]:
					data = part["body"]["data"]
				else:
					att_id = part["body"]["attachmentId"]
					att = service.users().messages().attachments().get(
						userId="me",
						messageId=msg_id,
						id=att_id
					).execute()
					data = att["data"]
					file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
					path = part["filename"]
				with open(path, "wb") as f:
					f.write(file_data)
		print("pedido.xlsx fue descargado correctamente")
	# Error catching
	except HttpError as error:
		print(f"An error occured: {error}")

def list_data():
	"""
	MAYBE *********
	Get 3 types of output:
		- Default: (All) take order into account and limit when not present and print merged info
		- IO: (Ignore Order)  dont take order into account and print new info 
		- OO: (Only Order) Only take order into account and print ordered info
	"""
	"""
	Update my DB with the new costs
	This program is dependant on:
	    "Provedores Todos.xlsm" ----> My DB
	    "pedido.xlsx" ----> downloaded by trevi_order.py (it's the ordered place to the provider)
	    "trevi_full.xlsx" ----> it's the list scraped by trevi_spider.py (all the provider's prices from the website)
	"""
	import pandas as pd
	import numpy as np
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
	new_df["Cantidad"] = my_df["Límite"] 

	# Clear memory
	del my_df
	gc.collect()

	# Read ordered placed
	order_df = pd.read_excel("pedido.xlsx")
	order_df.rename(columns={"Clave": "Key"}, inplace=True)

	# From ordered_df push Quantity ordered in the correct row
	new_df.set_index("Key", inplace=True)
	order_df.set_index("Key", inplace=True)
	order_df = order_df.groupby("Key")["Cantidad"].sum().reset_index()
	merged_df = new_df.merge(order_df[['Key', 'Cantidad']], how='left', on='Key')
	new_df["Cantidad"] = np.where(merged_df['Cantidad_y'].isna(), merged_df['Cantidad_x'], merged_df['Cantidad_y'])
	new_df.reset_index(inplace=True)

	""" OLD 
	new_df.set_index("Key", inplace=True)
	order_df.set_index("Key", inplace=True)
	order_df = order_df.groupby("Key")["Cantidad"].sum().reset_index()
	new_df = new_df.merge(order_df, on="Key", how="left")
	new_df.reset_index(inplace=True)
	"""
	
	# Clear memory
	del merged_df
	del order_df
	gc.collect()

	# Correct quantity: when unitary multiply pieces by packs 
	for idx, row in new_df.iterrows():
		if row["Cantidad"] == 0:
			new_df.loc[idx, "Cantidad"] = 1
		if not pd.isna(row["Cantidad"]):
			ref = (row["Ref"].split("-"))[0]
			if ref == "U":
				new_df.loc[idx, "Cantidad"] = new_df.loc[idx, "Cantidad"] * new_df.loc[idx, "Pieces"] 


	# Read treviño's full price data 
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
	"""
	Treviño's prices already include taxes
	IV == iva == 16%
	IE == ieps == 8%
	Sometimes Treviño's prices reflect the total in my DB and sometimes reflects the unitary price
	T == when Treviño's prices correspond to the total in my DB
	U == when Treviño's prices correspond to the unitary price in my DB
	"""
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
	    # if no new data keep existing one
	    else: 
	        merged_df.loc[idx, "New Subtotal"] = merged_df.loc[idx, "Sub"]
	    # Modify date column to facilitate excel macro "filtrar datos" which shows rise in prices 
	    merged_df.loc[idx, "Date"] = f"{datetime.date.today().day}/{datetime.date.today().month}/{datetime.date.today().year}"

	merged_df.to_excel("Final.xlsx")
	print("Final.xlsx file was created")