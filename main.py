"""
Extracts data from provider's website with SELENIUM
Downloads placed order with GMAIL-API (Requires a credentials.json file from google)
& Creates a new list of cost to update my DB with pandas (Requires a copy of my .xlsm database to work)
"""	
def main():
	import spider_functions
	import sys

	help_info = """

			~~~Trevi Spider~~~

Para ejecutar: 

	1.- Asegurarse de estar en una linea de comandos de "Anaconda" y tener activado el ambiente virtual "python_scraper"

	2.- En la ubicación del archivo ejecutar el comando "python main.py -flag" (la bandera no es opcional)

Banderas (Flags):

		-f | -o | -u | -s 

	-f : (Full) Es el proceso completo; obtiene los datos del sitio web del provedor, descarga una copia de la última orden emitida por nosotros y produce una lista de precios actualizados.

	-o : (Order) Solo descarga la última orden emitida por nosotros.

	-u : (Update) Solo produce la lista de precios actualizados con la información existente(los archivos existentes en la carpeta de los datos del sitio web y la última orden emitida)

	-s : (Scrape) Solo obtiene los datos del sitio web del provedor

	"""

	if len(sys.argv) < 2:
		print(help_info)

	for arg in sys.argv:
		if arg != "main.py":
			arg = arg.upper()
			if arg == "-F":
				print("Full process: scrape, get order and make updated list")
				print("Beginning to scrape the data...")
				spider_functions.crawl()
				print("Scraping successfull!")
				print("Downloading placed order...")
				spider_functions.get_order()
				print("Formatting data...")
				spider_functions.list_data()
				print("All done! Check Final.xlsm to begin updating the DB")
			elif arg == "-O":
				print("Only order")
				print("Downloading placed order...")
				spider_functions.get_order()
			elif arg == "-U":
				print("Only update")
				print("Formatting data...")
				spider_functions.list_data()
				print("All done! Check Final.xlsm to begin updating the DB")
			elif arg == "-S":
				print("Only scrape")
				print("Beginning to scrape the data...")
				spider_functions.crawl()
				print("Scraping successfull!")
			else:
				print("Bandera no encontrada\n")
				print(help_info)

if __name__ == "__main__":
	main()

"""
TODO

maybe add a second flag
	- optional
	- -IO (Ignore Order) | -OO (Only Order)
	- works with -f | -u 
	- -IO : for "Cantidad" only takes into consideration the "Límite" column in my DB and not the placed order.
	- -OO : in "final.xlsx" I only get ordered product's updated info (price and date) the rest can remain same.

for -IO to work i would've to pass a argument to updater (list_data()) to not consider the placed order into "Cantidad" 

for -OO to work i would've to pass an argument to updater (list_data()) to adjust the date to only write down when key with products match with placed order. maybe explicitly ignore other data, i mean other info from products not ordered, or leave as is; as long as date is only recorder for ordered products 

maybe create a report of "price not found id's"
	- whenever using existing data instead of scraped push id to list 
	- at the end of execution print out the list to file price_not_found.txt 
"""