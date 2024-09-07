"""
Extracts data from provider's website with SELENIUM
Downloads placed order with GMAIL-API (Requires a credentials.json file from google)
& Creates a new list of cost to update my DB with pandas (Requires a copy of my .xlsm database to work)
"""	
def main():
	import spider_functions
	import sys

	help_info = """

			~~~~Trevi Spider~~~~

Para ejecutar: 

	1.- Asegúrese de estar en la línea de comandos de "Anaconda" y tener activado el ambiente virtual "python_scraper".

	2.- En la ubicación del archivo ejecutar el comando:

					python main.py <Bandera_1> [<Bandera_2>]

Banderas:

	Bandera_1: 
		* Es obligatoria.
		* Describe las funciones a ejecutar.
		* Las opciones posibles son:
			-f | -o | -u | -s 
		* Donde:
			-f : (Full) Es el proceso completo; obtiene los datos del sitio web del provedor, descarga una copia de la última orden emitida por nosotros y produce una lista de precios actualizados.
			-o : (Order) Solo descarga la última orden emitida por nosotros.
			-u : (Update) Solo produce la lista de precios actualizados con la información existente(los archivos existentes en la carpeta de los datos del sitio web y la última orden emitida)
			-s : (Scrape) Solo obtiene los datos del sitio web del provedor

	Bandera_2:
		* Es opcional.
		* El comportamiento por defecto, sin esta bandera, es tomar en cuenta la lista de productos ordenados para determinar, con mayor precisión, la columna de "Cantidad" en el resultado final. Pero imprimir la fecha actual para todos los registros que el programa actualiza. Esta bandera determina si la fecha se actualiza únicamente para los productos ordenados (-OO) o si ignora la lista de productos ordenados para la columna de "Cantidad" (-IO).
		* Las opciones posibles son:
			-OO | -IO
		* Donde:
			-OO : (Only Order) Actualiza la fecha de los registros únicamente donde los productos fueron ordenados y toma en cuenta las cantidades ordenadas para determinar la columna de "Cantidad" en el resultado final. 
			-IO : (Ignore Order) Ignora la cantidad de productos ordenados y actualiza la fecha para todos los registros.  
		* Nota: La columna de "Cantidad" afecta el resultado final de "New Subtotal" en tanto que el precio del producto varia dependiento de la cantidad por comprar. 



	"""
	functions = {
		"-s": [spider_functions.crawl],
		"-o": [spider_functions.get_order],
		"-u": [spider_functions.list_data],
		"-f": [spider_functions.crawl, spider_functions.get_order, spider_functions.list_data]
	}
	bandera_2 = ["-OO", "-IO"]

	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print(help_info)
	elif not sys.argv[1] in list(functions.keys()):
		print(help_info)
	else:
		for func in functions[sys.argv[1]]:
			if len(sys.argv) > 2:
				if not sys.argv[2] in bandera_2:
					print(help_info)
					break
				elif func == spider_functions.list_data:
					func(sys.argv[2])
				elif func == spider_functions.get_order and sys.argv[2] == "-IO":
					continue
				else:
					func()
			else:
				func()

if __name__ == "__main__":
	main()

"""
TODO

maybe create a report of "price not found id's"
	- whenever using existing data instead of scraped push id to list 
	- at the end of execution print out the list to file price_not_found.txt 
"""
