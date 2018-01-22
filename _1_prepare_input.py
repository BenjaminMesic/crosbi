import os
import urllib2
import json

import bibtexparser

from bs4 import BeautifulSoup

from selenium import webdriver

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

# --------------------------------------------------
# Configurations

output_file = 'list_of_CROSBI_input.json'

# If list empty run over all papers, else run over the ones which are in the list
eprint 		= [] # e.g. '1509.03750'

authors = {
	'N. Godinovic'				: 'Godinovi\xc4\x87, Nikola',
	'D. Lelas' 						: 'Lelas, Damir',
	'I. Puljak' 					: 'Puljak, Ivica',					
	'Z. Antunovic' 				: 'Antunovi\xc4\x87, \xc5\xbdeljko',
	'M. Kovac' 						: 'Kova\xc4\x8d, Marko',
	'V. Brigljevic' 			: 'Brigljevi\xc4\x87, Vuko',
	'K. Kadija' 					: 'Kadija, Kre\xc5\xa1o',
	'J. Luetic' 					: 'Lueti\xc4\x87, Jelena',
	'S. Micanovic' 				: 'Mi\xc4\x87anovi\xc4\x87, Sa\xc5\xa1a',
	'L. Sudic' 						: 'Sudi\xc4\x87, Lucija',
	'T. Susa' 						: '\xc5\xa0u\xc5\xa1a, Tatjana',
	'D. Polic' 						: 'Poli\xc4\x87, Dunja',
	'S. Morovic' 					: 'Morovi\xc4\x87, Sre\xc4\x87ko',
	'L. Tikvica' 					: 'Tikvica, Lucija',
	'D. Mekterovic' 			: 'Mekterovi\xc4\x87, Darko',
	'D. Ferencek'					: 'Feren\xc4\x8dek, Dinko',
	'A. Starodumov' 			: 'Starodumov, Andrey',
	'B. Mesic' 				 		: 'Mesi\xc4\x87, Benjamin',
	'S. Duric' 				 		: 'Duri\xc4\x87, Senka',	
}

first_author = {
	# 'V. Khachatryan' 			: 'Khachatryan, Vardan',
	# 'S. Chatrchyan' 			: 'Khachatryan, Serguei',
	'A.M. Sirunyan' 			: 'Sirunyan, Albert'
}

last_author = {
	'N. Woods' 						: 'Woods, Nate',
	# 'J. Swanson' 					: 'Swanson, Joshua',
	# 'W.H. Smith' 					: 'Smith, Wesley',
}

journals = {
	'JHEP'							: 'Journal of High Energy Physics', 
	'Phys. Rev. Lett.'	: 'Physical Review Letters', 
	'Eur. Phys. J.' 		: 'European physical journal', 
	'JINST' 						: 'Journal of Instrumentation', 
	'Phys. Lett.' 			: 'Physics letters', 										
	'Phys. Rev.' 				: 'Physical Review', 
	'Nature'						: 'Nature Physics'
}

issn = {
	'JHEP' 							: '1029-8479',
	'Phys. Rev. Lett.'	: '0031-9007',
	'Eur. Phys. J. C' 	: '1434-6044',
	'JINST' 						: '1748-0221',
	'Phys. Lett. B' 		: '0370-2693',
	'Nature' 						: '1745-2473',
	'Phys. Rev. C'  		: '0556-2813',
	'Phys. Rev. D'  		: '1550-7998'
}

# --------------------------------------------------

def get_list_of_papers(list_of_papers):

	with open(list_of_papers) as f:
		temp = f.read()

	return bibtexparser.loads(temp)

def get_abstract_and_title(arxiv_name):

	r = urllib2.urlopen('http://arxiv.org/abs/' + arxiv_name).read()

	soup = BeautifulSoup(r, 'html.parser')

	abstract = ''
	title = ''

	for line in soup.find_all('blockquote', {'class':'abstract mathjax'}):
		abstract += line.text[len('Abstract')+3:]

	for line in soup.find_all('h1', {'class':'title mathjax'}):
		title += line.text[len('Title')+2:]

	return [abstract, title.replace('  ', ' ') ]

def get_journal(name, volume):
	
	if name not in journals:
		return '*** dictionary_journals is missing name!! ***', name
	
	else:
		if name == 'Eur. Phys. J.' or name == 'Phys. Lett.' or name =='Phys. Rev.':
			return journals[name] + ' ' + volume[0]
		else:
			return journals[name]

def get_issn(name, volume):
	if name == 'Eur. Phys. J.' or name == 'Phys. Lett.' or name == 'Phys. Rev.':
		return issn[ name + ' ' + volume[0] ]
	else:
		return issn[ name ]

def get_volume(name, volume):
	if name == 'Eur. Phys. J.' or name == 'Phys. Lett.' or name == 'Phys. Rev.':
		return volume[1:]
	else:
		return volume

def get_url(arxiv_name):

	browser = webdriver.Firefox()
	browser.get('http://arxiv.org/abs/' + arxiv_name)

	url = ''

	try:
		browser.find_element_by_partial_link_text('/').click()
		url = browser.current_url
	except:
		pass

	browser.quit()

	return url

def prepare_input_for_CROSBI(list_of_papers, output_file):

	data = {}

	# Loop over all papers which are stored in bib
	for _n, _p in enumerate(list_of_papers.entries):

		# if _n > 0:
		# 	break

		# If eprint list not empty skip all but those in list
		if len(eprint) and _p['eprint'] not in eprint:
			continue

		# 1. Get the arxiv paper id
		_eprint = _p['eprint']

		# 2. Get abstract and title from arxiv since they dont have bibtex syntax
		_abstract, _title = get_abstract_and_title(_eprint)

		# 3. DOI
		_doi = _p['doi']

		# 4. Authors
		# Load pdf
		_pdf 		= 'pdf/' + _p['eprint'] + '.pdf'
		_paper 	= convert_pdf_to_txt(_pdf)

		# First author
		_authors = first_author.values()[0] + '; ...'

		# Cro authors
		for _a, _a_pretty in authors.iteritems():

			if _a in _paper:
				_authors += ' ; ' + _a_pretty

		# Last author
		_authors += ' ; ... ; ' + last_author.values()[0]

		# 5. Year
		_year = _p['year']

		# 6. Journal
		_journal = get_journal( _p['journal'], _p['volume'])

		# 7. ISSN
		_issn = get_issn( _p['journal'], _p['volume'])

		# 8. Volume
		_volume = get_volume( _p['journal'], _p['volume'])

		# 9. Page
		_page = _p['pages']

		# 10. url
		_url = get_url(_p['eprint']).rstrip()

		# Save output
		_temp = {}
		_temp['doi'] 			= _doi
		_temp['autori'] 	= _authors
		try:
			_temp['naslov'] = _title
		except:
			_temp['naslov'] = _p['title']
		_temp['godina'] 	= _year
		_temp['casopis'] 	= _journal
		_temp['issn'] 		= _issn
		_temp['volumen'] 	= _volume
		_temp['stranice'] = _page
		_temp['sazetak'] 	= _abstract
		_temp['url'] 			= _url

		data[_eprint] = _temp

		print '\n'
		print _n
		print _eprint
		print _title
		print _doi
		print _authors
		print _year
		print _journal
		print _issn
		print _volume
		print _page
		print _abstract
		print _url

	# Output file, i.e. input for CROSBI
	with open(output_file, 'w') as outfile:
		json.dump(data, outfile)

def download_pdfs(list_of_papers):

	print 'Downloading pdfs...'

	if not os.path.isdir('pdf'):
		os.mkdir('pdf')

	# Loop over all papers which are stored in bib
	for _n, _p in enumerate(list_of_papers.entries):

		# If eprint list not empty skip all but those in list
		if len(eprint) and _p['eprint'] not in eprint:
			continue

		_pdf = 'pdf/' + _p['eprint'] + '.pdf'

		if os.path.isfile(_pdf):
			print '{0} already exists.'.format(_pdf)
			continue

		pageContent = urllib2.urlopen('http://arxiv.org/' + _pdf)
		file = open( _pdf, 'wb')
		file.write(pageContent.read())
		file.close()

		print 'Downloaded {0}'.format(_pdf)

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text	

# --------------------------------------------------

if __name__ == '__main__':

	# Load list of papers from bib file	
	list_of_papers = get_list_of_papers('list_of_papers.bib')

	# Download pdfs if they don't exist
	download_pdfs(list_of_papers)

	# Create input for CROSBI, name of output hardcoded in the function
	prepare_input_for_CROSBI(list_of_papers, output_file)
