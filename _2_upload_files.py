import json
import os
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# --------------------------------------------------
# Configurations
list_of_CROSBI_input = 'list_of_CROSBI_input.json'

keywords 						= ['High energy physics', 'Experimental particle physics', 'LHC', 'CMS', 'Standard Model']
project_numbers 		= []
collaboration_name 	= 'CMS'

username 						= 'username@irb.hr'
password 						= 'password'

location_of_papers_pdf = os.path.dirname(os.path.realpath(__file__)) + '/pdf'

# --------------------------------------------------

def get_input_for_CROSBI(list_of_CROSBI_input):

	with open(list_of_CROSBI_input) as f:
		return json.load(f)

def upload_to_CROSBI(dict_papers, username, password):

	redni_brojevi_rada = []

	browser = webdriver.Firefox() #Chrome()
	browser.get("http://bib.irb.hr/")
	browser.find_element_by_partial_link_text('Upis novih radova').click()

	# Login
	username_element = browser.find_element_by_id("username")
	password_element = browser.find_element_by_id("password")
	username_element.send_keys(username)
	password_element.send_keys(password)
	browser.find_element_by_id('aai_loginbutton').click()
	browser.implicitly_wait(1)

	# Get list of already existing papers
	browser.get('http://bib.irb.hr/pretrazivanje_slozeno')
	check_author_element = browser.find_element_by_name('patt')
	check_author_element.send_keys('puljak, ivica')
	browser.execute_script("$('input[name=\"slozeno\"]').click();")	
	delay = 10
	try:
	    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
	    print "Page is ready!"
	except TimeoutException:
	    print "Loading took too much time!"

	# Gives you list(page source with lot of other data) of all existing papers for Ivica Puljak
	existing_papers = browser.page_source

	n = 0

	# Loop over all papers
	for _p, _info in dict_papers.iteritems():
		
		# if n<0 or n>0:
		# 	n += 1
		# 	continue

		print '\n', _p, _info['naslov']

		if _info['naslov'] in existing_papers:
			print 'Paper already in CROSBI.'
			continue
		else:
			print 'Paper not in CROSBI.'

		# Go to the first page
		browser.get('http://bib.irb.hr/upis-pocetak')
		browser.implicitly_wait(1)
		browser.find_element_by_name('novirad').click()

		# Izaberite kategoriju rada
		browser.find_element_by_xpath('//select[@name="kategorija"]/option[@value="Znanstveni"]').click()

		# URL rada u otvorenom pristupu
		url_element = browser.find_element_by_name('openurl')
		url_element.send_keys(_info['url'])
		
		# DOI rada
		doi_element = browser.find_element_by_name('doi')
		doi_element.send_keys(_info['doi'])

		# Odaberite vrstu recenzije
		browser.find_element_by_xpath('//select[@name="vrst_recenzije"]/option[@value="Recenzija"]').click()

		# Autori
		autori_element = browser.find_element_by_name('autori')
		autori_element.send_keys(_info['autori'])

		browser.find_element_by_xpath('//select[@name="suradnja_medjunarodna"]/option[@value="DA"]').click()

		# Ime kolaboracije
		autori_element = browser.find_element_by_name('kolaboracija')
		autori_element.send_keys(collaboration_name)		

		# Naslov rada na izvornom jeziku (na kojem je rad napisan)
		naslov_element = browser.find_element_by_name('naslov')
		naslov_element.send_keys(_info['naslov'])		

		# Naslov rada na engleskom jeziku ("trazi poseban tretman"-Jelena)
		title_element = browser.find_element_by_xpath("//div[@class='topdiv']//textarea[@name='title']")
		title_element.send_keys(_info['naslov'])

		# Godina
		godina_element = browser.find_element_by_name('godina')
		godina_element.send_keys(_info['godina'])

		# Puni naziv casopisa
		casopis_element = browser.find_element_by_name('casopis')
		casopis_element.send_keys(_info['casopis'])

		# ISSN
		issn_element = browser.find_element_by_name('issn')
		issn_element.send_keys(_info['issn'])

		issn_e_element = browser.find_element_by_name('issn_e')
		issn_e_element.send_keys(_info['issn'])

		# Volumen
		volumen_element = browser.find_element_by_name('volumen')
		volumen_element.send_keys(_info['volumen'])

		# # Broj
		# broj_element = browser.find_element_by_name('broj')
		# broj_element.send_keys(_info['broj'])

		# Pocetna stranica rada
		pocetna_stranica_element = browser.find_element_by_name('stranica_prva')
		pocetna_stranica_element.send_keys(_info['stranice'])

		# Zadnja stranica rada
		zadnja_stranica_element = browser.find_element_by_name('stranica_zadnja')
		zadnja_stranica_element.send_keys(_info['stranice'])

		# Kljucne rijeci na izvornom jeziku rada
		kljucne_rijeci_element = browser.find_element_by_name('kljucne_rijeci')
		kljucne_rijeci_element.send_keys(', '.join(keywords))

		# Kljucne rijeci na engleskom jeziku
		kljucne_rijeci_en_element = browser.find_element_by_name('key_words')
		kljucne_rijeci_en_element.send_keys(','.join(keywords))

		# Sazetak na izvornom jeziku rada
		sazetak_element = browser.find_element_by_name('sazetak')
		sazetak_element.send_keys(_info['sazetak'])

		# Brojevi projekata
		# Skip, Nothing for now

		# Cjeloviti tekst rada
		browser.find_element_by_name('datoteka').send_keys('{0}/{1}.pdf'.format( location_of_papers_pdf, _p))

		# Izvorni jezik rada
		browser.find_element_by_xpath('//select[@name="jezik"]/option[@value="ENG"]').click()

		# Provjera upisanih elemanta
		browser.find_element_by_name(".submit").click()
		browser.implicitly_wait(2)

		# Podrucje znanosti
		browser.execute_script("$('select[name=pozn_all] option[value=\"1.02\"]').click();")

		# Odabir znanstvene ustanove
		browser.execute_script("$('select[name=ustn_all] option[value=\"98\"]').click();")
		browser.execute_script("$('select[name=ustn_all] option[value=\"23\"]').click();")
		browser.execute_script("$('select[name=ustn_all] option[value=\"177\"]').click();")

		browser.find_element_by_name("ok").click()
		browser.implicitly_wait(2)

		# Redni brojevi radova
		_redni_broj_rada = browser.execute_script("return $('a[href*=\"/prikazi-rad?rad=\"]').text();")
		print 'Redni broj rada: {0}'.format(_redni_broj_rada)

		redni_brojevi_rada.append(_redni_broj_rada)

		n += 1

	browser.quit()

	# Spremi listu rednih brojeva
	# Listu rednih brojeva (.txt) dostaviti Bojanu Macanu
	with open('redni_brojevi_radova.txt', 'w') as f:
		f.write('\n'.join(redni_brojevi_rada))

def get_input_for_CROSBI(list_of_CROSBI_input):

	with open(list_of_CROSBI_input) as f:
		return json.load(f)

if __name__ == '__main__':
	
	# Open list of CROSBI input
	input_for_CROSBI = get_input_for_CROSBI(list_of_CROSBI_input)

	# Upload
	upload_to_CROSBI(input_for_CROSBI, username, password)