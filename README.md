# Trevi Spider

## What it does:
It can execute three distinct functions to populate the local business database with carefully extracted data from the provider's website:
	- It scrapes the price data from the provider's website.
	- Retrieves the placed ordered via email to the provider. 
	- Creates a dataframe with the new data when available.  

## What technologies does it need:
	- Python
 	- google-api-python-client 
 	- google-auth-httplib2 
 	- google-auth-oauthlib
 	- numpy
  	- Selenium
   	- Pandas
   	- openpyxl 


## What files does it need (stdin):
	- To get placed-order:
		- token.json ~ GMAIL API **git ignored**
		- credentials.json ~ GMAIL.API **git ignored**
		- mygmailaccount.inbox.message_with_pedido.xlsx

	- To update:
		- Provedores Todos.xlsm ~ Local database **git ignored**
		- pedido.xlsx ~ Placed-order to provider, retrieved from GMAIL **git ignored**
		- trevi_full.xlsx ~ Scraped data from provider's website **git ignored**


## What files does it create (stdout):
	- After scraping the data:
		- trevi_full.xlsx ~ Scraped data from provider's website **git ignored**

	- After retrieving placed-order:
		- pedido.xlsx ~ Placed-order to provider, retrieved from GMAIL **git ignored**

	- After creating an updtaded dataframe:
		- Final.xlsx ~ Updated dataframe with necesary information **git ignored**

## What I'm thinking about:
	- Uploading all the necessary sample_files.
	- Adding a second flag to ignore, or only consider, the placed-order in the final output. 
