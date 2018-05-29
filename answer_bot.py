"""
HQ Bot forked from https://github.com/sushant10/HQ_Bot

Features:
	Grab screenshots from phone screen (Reflector 3 or QuickTime Player required)
	Multiprocess Google Search System
"""

# answering bot for trivia HQ and Cash Show
import os
import sys
import time
import json
import argparse
from multiprocessing import Pool
from functools import partial

import cv2
from PIL import Image
from PIL import ImageGrab
import urllib.request as urllib2
from bs4 import BeautifulSoup
import numpy as np

from google import google
from halo import Halo
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

#sys.path.append("C:\Program Files\Brainwy\PyVmMonitor 1.1.2\public_api")
#import pyvmmonitor
#pyvmmonitor.connect()

# for terminal colors
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# list of words to clean from the question during google search
remove_words = []

# negative words
negative_words= []

# load sample questions
def load_json(debug=False):
	global remove_words, negative_words
	if debug is False:
		path = "Data/settings.json"
	else:
		path = "../Data/settings.json"

	settings = json.loads(open(path, encoding="utf8").read())

	remove_words = settings["remove_words"]
	negative_words = settings["negative_words"]

# take screenshot of question
def screen_grab(save, location):
	# 31,228 485,620 co-ords of screenshot// left side of screen
	im = ImageGrab.grab(bbox=(20, 260, 520, 700))

	if save:
		im.save(location)

	return np.array(im)

def preprocess_img(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	gray = cv2.threshold(gray, 0, 255,
			cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
	return gray

# get OCR text //questions and options
def read_screen():
	spinner = Halo(text='Reading screen', spinner='bouncingBar')
	spinner.start()

	screenshot_file = os.path.join('Screens', 'to_ocr.png')
	image = screen_grab(save=False, location=screenshot_file)
	gray = preprocess_img(image)

	# store grayscale image as a temp file to apply OCR
	'''filename = "Screens/{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)
	print("\nPreprocessing Elapsed Time: {}".format(time.time() - preprocess_time))'''

	# extract_text_time = time.time()
	# load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
	text = pytesseract.image_to_string(Image.fromarray(gray))
	# print('\nExtract Text Elapsed Time: {}'.format(time.time() - extract_text_time))

	spinner.succeed()
	spinner.stop()
	return text

# get questions and options from OCR text
def parse_question():
	text = read_screen()
	lines = text.splitlines()
	question = ""
	options = list()
	flag = False

	for line in lines:
		if not flag:
			question= question + " " + line

		if '?' in line :
			flag=True
			continue

		if flag :
			if line != '' :
				options.append(line)

	return question, options

# simplify question and remove which,what....etc //question is string
def simplify_ques(question, debug=False):
	if debug is True:
		load_json(debug=True)

	neg = False
	qwords = question.lower().split()
	for i in qwords:
		if i in negative_words:
			neg = True
	#if [i for i in qwords if i in negative_words]:
	#	neg=True

	cleanwords = [word for word in qwords if word.lower() not in remove_words]
	temp = ' '.join(cleanwords)

	clean_question=""
	#remove ?
	for ch in temp:
		if ch != "?" or ch != "\"" or ch != "\'":
			clean_question=clean_question+ch

	return clean_question.lower(), neg

# answer by combining two words
def smart_answer(content, qwords):
	zipped= zip(qwords,qwords[1:])
	points=0
	for el in zipped:
		if content.count(el[0]+" "+el[1])!=0 :
			points+=1000
	return points

# split the string
def split_string(source):
	splitlist = ",!-.;/?@ #"
	output = []
	atsplit = True
	for char in source:
		if char in splitlist:
			atsplit = True
		else:
			if atsplit:
				output.append(char)
				atsplit = False
			else:
				output[-1] = output[-1] + char
	return output

# get web page
def get_page(link):
	try:
		if link.find('mailto') != -1:
			return ''
		req = urllib2.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
		html = urllib2.urlopen(req).read()
		return html
	except (urllib2.URLError, urllib2.HTTPError, ValueError) as e:
		return ''

# use google to get wiki page
def google_wiki(sim_ques, options, neg):
	spinner = Halo(text='Googling and searching Wikipedia', spinner='dots2')
	spinner.start()

	num_pages = 1
	points = list()

	content = ""
	maxo = ""

	maxp = -sys.maxsize
	words = split_string(sim_ques)
	for o in options:

		o = o.lower()
		original=o
		o += ' wiki'

		# get google search results for option + 'wiki'
		search_wiki = google.search(o, num_pages)

		link = search_wiki[0].link
		content = get_page(link)
		soup = BeautifulSoup(content,"lxml")
		page = soup.get_text().lower()

		temp = 0

		for word in words:
			temp = temp + page.count(word)

		temp += smart_answer(page, words)

		if neg:
			temp *= -1

		points.append(temp)
		if temp > maxp:
			maxp = temp
			maxo=original

	spinner.succeed()
	spinner.stop()
	return points, maxo

def process_search(option, sim_ques, neg, points):
	option = option.lower()
	original = option
	option += " wiki"

	search_wiki = google.search(option, 1)
	link = search_wiki[0].link

	content = get_page(link)
	soup = BeautifulSoup(content, "lxml")
	page = soup.get_text().lower()

	maxp = -sys.maxsize
	maxo = ""
	temp = 0

	words = split_string(sim_ques)

	for word in words:
		temp = temp + page.count(word)
		#print("TEMP: {}".format(temp))

	temp += smart_answer(page, words)
	#print("Smart Answer TEMP: {}".format(temp))

	if neg:
		temp *= -1
		#print("Negative TEMP: {}".format(temp))

	points.append(temp)
	if temp > maxp:
		maxp = temp
		maxo = original

	#print("MAXO: {}".format(points))
	return [points, maxo]

def google_wiki_faster(sim_ques, options, neg):
	spinner = Halo(text='Googling and searching Wikipedia', spinner='dots2')
	spinner.start()

	num_pages = 1
	points = list()

	content = ""
	maxo = ""

	#words = split_string(sim_ques)
	#options = [o.lower() + ' wiki' for o in options]

	pool = Pool(processes=3)

	process = partial(process_search, sim_ques=sim_ques, neg=neg, points=points)
	points = pool.map(process, options)

	pool.close()
	pool.join()

	maxo = ""
	maxVal = -sys.maxsize
	for option in points:
		val = option[0][0]
		if val > maxVal:
			maxo = option
			maxVal = val

	spinner.succeed()
	spinner.stop()
	return points, maxo

# return points for sample_questions
def get_points_sample():
	simq = ""
	x = 0
	for key in sample_questions:
		x = x + 1
		points = []
		simq, neg = simplify_ques(key)
		options = sample_questions[key]
		simq = simq.lower()
		maxo = ""
		points, maxo = google_wiki(simq, options, neg)
		print("\n" + str(x) + ". " + bcolors.UNDERLINE + key + bcolors.ENDC + "\n")
		for point, option in zip(points, options):
			if maxo == option.lower():
				option=bcolors.OKGREEN + option + bcolors.ENDC
			print(option + " { points: " + bcolors.BOLD + str(point) + bcolors.ENDC + " }\n")

def get_points_live():
	start_time = time.time()

	neg = False

	parse_question_time = time.time()
	question, options = parse_question()
	print('Parse Question Elapsed Time: {} seconds'.format(time.time() - parse_question_time))

	simq = ""
	points = []

	#simplify_ques_time = time.time()
	simq, neg = simplify_ques(question)
	#print('Simplify Question Elapsed Time: {} seconds'.format(time.time() - simplify_ques_time))

	maxo=""
	m = 1
	if neg:
		m =- 1

	google_start_time = time.time()
	try:
		points, maxo = google_wiki(simq, options, neg)
	except IndexError as e:
		print("Sorry nothing could be searched")

	print("Points: {}".format(points))
	print('Google Search Elapsed Time: {} seconds'.format(time.time() - google_start_time))

	print("\n" + bcolors.UNDERLINE + question + bcolors.ENDC + "\n")
	for point, option in zip(points, options):
		if maxo == option.lower():
			option = bcolors.OKGREEN+option+bcolors.ENDC
		print(option + " { points: " + bcolors.BOLD + str(point * m) + bcolors.ENDC + " } \n")

	print('Total Elapsed Time: {}'.format(time.time() - start_time))

# return points for live game // by screenshot
def get_points_live_v2():
	start_time = time.time()

	neg = False

	parse_question_time = time.time()
	question, options = parse_question()
	print('Parse Question Elapsed Time: {} seconds'.format(time.time() - parse_question_time))

	simq = ""
	points = []

	simq, neg = simplify_ques(question)

	maxo = ""
	m = 1
	if neg:
		m =- 1

	google_start_time = time.time()
	#points, maxo = google_wiki(simq, options, neg)
	try:
		points, maxo = google_wiki_faster(simq, options, neg)
	except IndexError as e:
		print("Sorry nothing could be searched")

	print('Google Search Elapsed Time: {} seconds'.format(time.time() - google_start_time))

	print("\n" + bcolors.UNDERLINE + question + bcolors.ENDC + "\n")
	for point, option in zip(points, options):
		if maxo[1] == option.lower():
			option = bcolors.OKGREEN + option + bcolors.ENDC
		else:
			option = bcolors.FAIL + option + bcolors.ENDC
		print(option + " { points: " + bcolors.BOLD + str(point[0][0] * m) + bcolors.ENDC + " } \n")

	print('Total Elapsed Time: {}'.format(time.time() - start_time))


if __name__ == "__main__":
	load_json()

	while(1):
		keypressed = input('Press s to screenshot live game or q to quit:\n')
		if keypressed == 's':
			#p.apply_async(get_points_live(), ())
			get_points_live_v2()
		elif keypressed == 'o':
			get_points_live()
		elif keypressed == 'q':
			break
		else:
			print(bcolors.FAIL + "\nUnknown input" + bcolors.ENDC)


