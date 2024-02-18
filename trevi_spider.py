"""
Scrape the prices from comercial treviño's website
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
driver = webdriver.Chrome()
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

# **************************************************************************************

""" V-2.1
# It DOES work but it's dependant on the correct "name"


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Initial variables
excel_df = pd.read_excel('Provedores Todos.xlsm', sheet_name='Datos', index_col=0, na_values='--', skipfooter=10, usecols='A:AF')
products = list()
search_names = list()
not_found = list()

# Populate search_names
for idx, row in excel_df.iterrows():
	if excel_df.loc[idx, 'Provedor'] == 'Treviño':
		search_names.append(excel_df.loc[idx, 'Descripción'])

# Begin scraping
driver = webdriver.Chrome()
driver.get("https://comercialtrevino.com/")

# Select the correct store
el_city = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "selected_city")))
all_opt = el_city.find_elements(By.TAG_NAME, "option")
for option in all_opt:
	if option.get_attribute("value") == "1":
		correct_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(option))
		correct_option.click()
el_select = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID, "selectDealer_1")))
el_select.click()

# Mine the data
for name in search_names:
	
	# Search
	el_search = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="keyword"]')))
	el_search.send_keys(name)
	el_search.send_keys(Keys.RETURN)

	# Navigate
	try:
		el_link = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.LINK_TEXT, name)))
		el_link.click()
	except:
		not_found.append(name)
		continue

	# Extract
	el_sku = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "pdl_model")))
	sku = ((el_sku.text).replace('SKU: ', '')).strip()
	el_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
	prices = dict()
	for row in el_rows:
		key = row.find_element(By.CSS_SELECTOR, "td.text-left")
		value = row.find_element(By.CSS_SELECTOR, "td.product_price")
		prices[f"{key.text}"] = value.text
	products.append({sku: prices})

# Finish escraping	
driver.quit()
"""