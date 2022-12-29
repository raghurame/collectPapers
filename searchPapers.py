import requests
from bs4 import BeautifulSoup
from time import sleep
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_paperinfo (paper_url):
	response = requests.get(url, headers = headers)
	if response.status_code != 200:
		print('Status code:', response.status_code)
		raise Exception('Failed to fetch web page ')

	paper_doc = BeautifulSoup (response.text,'html.parser')

	return paper_doc

def getLinks (keyWords):
	headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
	links = []

	for startNumber in range (0, 100, 10):
		print ("Collecting {} to {}".format (startNumber, startNumber+10))
		searchURL = ("https://scholar.google.com/scholar?start={}&q={}".format (startNumber, keyWords))
		success = 0
		response = requests.get (searchURL, headers = headers, timeout = None)

		sleep (1)
		responseHTML = BeautifulSoup (response.text, 'html.parser')
		linksTemp = responseHTML.select ('a')

		for linkTemp in linksTemp:
			if linkTemp.get('href') != None:
				if 'https://' in linkTemp.get('href'):
					if ("google" not in linkTemp.get('href') and ".pdf" not in linkTemp.get('href') and "/pdf/" not in linkTemp.get('href')):
						links.append (linkTemp.get('href'))

	return links

def findNth (haystack, needle, n):
	start = haystack.find (needle)
	while (start >= 0 and n > 1):
		start = haystack.find(needle, start + len(needle))
		n -= 1

	return start

def findImportance (link, keyWords, strongKeyWords):
	options = Options()
	options.headless = True

	try:
		options.add_experimental_option ("prefs", {"profile.managed_default_content_settings.images": 2})
		driver = webdriver.Chrome (options = options)
		driver.implicitly_wait(5)
		driver.get (link)
	except:
		pass
	sleep (10)

	pageSource = driver.page_source

	if (pageSource.count ("Abstract:") == 1):
		startIndex = pageSource.find ("Abstract:")
		pageSource = pageSource[startIndex:]

		if (pageSource.count ("</div>") > 0):
			endIndex = pageSource.find ("</div>")
			nthFind = 1
			endIndexCheck = 0

			while (endIndexCheck == 0):
				if ((int (pageSource[:endIndex].count ("</p>")) + int (pageSource[:endIndex].count ("<p>"))) >= 1):
					endIndexCheck = 1
				else:
					nthFind += 1
					endIndex = findNth (pageSource, "</div>", nthFind)

			pageSource = pageSource[:endIndex]

		# Format specifically for openscience.ub.uni-mainz.de
		elif (pageSource.count ("</div") == 0 and pageSource.count ("</td></tr>") > 0):
			endIndex = pageSource.find ("</td></tr>")
			pageSource = pageSource[:endIndex]

	elif (pageSource.count (">Abstract") == 1):
		startIndex = pageSource.find (">Abstract")
		pageSource = pageSource[startIndex:]
		endIndex = pageSource.find ("</div>")

		nthFind = 1

		endIndexCheck = 0

		while (endIndexCheck == 0):
			if ((int (pageSource[:endIndex].count ("</p>")) + int (pageSource[:endIndex].count ("<p>"))) >= 1):
				endIndexCheck = 1
			else:
				nthFind += 1
				endIndex = findNth (pageSource, "</div>", nthFind)

		pageSource = pageSource[:endIndex]

	else:
		if (pageSource.count (">Abstract</") == 1):
			startIndex = pageSource.find (">Abstract</")
			pageSource = pageSource[startIndex:]
			endIndex = pageSource.find ("</div>")

			nthFind = 1

			endIndexCheck = 0

			while (endIndexCheck == 0):
				if ((int (pageSource[:endIndex].count ("</p>")) + int (pageSource[:endIndex].count ("<p>"))) >= 1):
					endIndexCheck = 1
				else:
					nthFind += 1
					endIndex = findNth (pageSource, "</div>", nthFind)

			pageSource = pageSource[:endIndex]

		elif (pageSource.count (">Abstract</h") == 1):
			startIndex = pageSource.find (">Abstract</h")
			pageSource = pageSource[startIndex:]
			endIndex = pageSource.find ("</div>")

			nthFind = 1

			endIndexCheck = 0

			while (endIndexCheck == 0):
				if ((int (pageSource[:endIndex].count ("</p>")) + int (pageSource[:endIndex].count ("<p>"))) >= 1):
					endIndexCheck = 1
				else:
					nthFind += 1
					endIndex = findNth (pageSource, "</div>", nthFind)

			pageSource = pageSource[:endIndex]

		elif (pageSource.count (">Abstract</b") == 1):
			startIndex = pageSource.find (">Abstract</b")
			pageSource = pageSource[startIndex:]
			endIndex = pageSource.find ("</div>")

			nthFind = 1

			endIndexCheck = 0

			while (endIndexCheck == 0):
				if ((int (pageSource[:endIndex].count ("</p>")) + int (pageSource[:endIndex].count ("<p>"))) >= 1):
					endIndexCheck = 1
				else:
					nthFind += 1
					endIndex = findNth (pageSource, "</div>", nthFind)

			pageSource = pageSource[:endIndex]

	nKeyword = int (keyWords.count ("+")) + 1 + int (strongKeyWords.count ("+")) + 1
	keywordsFound = 0

	keyWords = keyWords.split ("+")
	strongKeyWords = strongKeyWords.split ("+")

	for keyWord in keyWords:
		if (keyWord in pageSource):
			keywordsFound += 1

	for strongKeyWord in strongKeyWords:
		if (strongKeyWord in pageSource):
			keywordsFound += 1

	driver.quit ()

	return (float (keywordsFound) / float (nKeyword))

def main (keyWords, strongKeyWords, outputFilename):
	keyWords = keyWords.replace (" ", "+")

	links = []
	links = getLinks (keyWords)

	totalLinks = len (links)

	print ("Number of links collected: {}\n".format (totalLinks))

	outputFile = open (outputFilename, "w")
	currentLinkNumber = totalLinks

	for link in links:
		print ("loading {}".format (link))
		relevance = findImportance (link, keyWords, strongKeyWords)
		outputFile.write ("{}, {}, {}\n".format ((float (currentLinkNumber) / float (totalLinks)), link, relevance))
		currentLinkNumber -= 1
		print ("relevance: {}\n".format (relevance))

	outputFile.close ()

if __name__ == '__main__':
	if (len (sys.argv) != 4):
		print ("ERROR:\n~~~~~~\n\nNot enough arguments passed. Required arguments are\n\n{~} argv[0] = program\n{~} argv[1] = keywords that carry normal weightage\n{~} argv[2] = Keywords that carry more weightage (must be already defined as normal keywords)\n{~} argv[3] = output file name\n\nNOTE:\n~~~~~\n\nDescribe the materials used, and methods in the search string. Use '+' instead of empty spaces. All words in the search string carry equal weightage.")
		exit (1)
	else:
		main(sys.argv[1], sys.argv[2], sys.argv[3])