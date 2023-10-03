# FandomGrabImages.py - FandomGrabImages by ChainSwordCS
# Python 3.8+

import os
import locale
locale.setlocale(locale.LC_ALL, '')
_locale_thousands_sep = locale.localeconv()['thousands_sep'] # hard-code to '.' or ',' if you have issues



# spitoutdata
#
# output will be borked if...
# 1. columns are out of order in the input file. columns will be out of order, and data meant for a given row may leak into the previous or next row.
# 2. any column is unexpectedly completely missing. data meant for a given column may shift unexpectedly within its row.
# 3. a data point in the table spans multiple lines (it will only output whatever happens to be in the first line, and ignore the rest) Note: this is only known to occur with thumbnails for "videos"
#
# i can't be bothered writing this in a less stupid way. -C
#
def spitoutdata(input_str, outcsv, find_str_1, find_str_2, find_str_end):
	start = input_str.find(find_str_1)
	if start == -1:
		return
	start += len(find_str_1)

	if find_str_2 != '':
		r = input_str[start:].find(find_str_2)
		if r != -1:
			start += len(find_str_2) + r

	# this value declaration only comes into play if find_str_end is empty or isn't found.
	# the `-1` here omits the last character, which is (almost) always '\n' in that situation.
	end = len(input_str) - 1

	if find_str_end != '':
		r = input_str[start:].find(find_str_end)
		if r != -1:
			end = start + r

	outstring = input_str[start:end]

	if outstring == ' ':
		outstring = ''

	output_csv.write('\"' + outstring + '\";')
	return



# spitoutdata_size
#
# kinda ugly
#
def spitoutdata_size(input_str, outcsv, find_str_1):

	# gets number (still in the form of a string)
	start = input_str.find(find_str_1)
	if start == -1:
		return 0
	start += len(find_str_1)

	end = input_str[start:].find(' ')
	if end == -1:
		return 0
	end += start

	numstr = input_str[start:end]
	numstr = numstr.replace(_locale_thousands_sep, '') # take care of thousands-separator (:
	num = locale.atof(numstr)


	# determines the unit
	start = end + 1
	end = start + 2
	if end > len(input_str):
		return 0
	unitstr = input_str[start:end]

	mult = 0.001

	if unitstr == 'KB':
		mult = 0.001
	elif unitstr == 'MB':
		mult = 1
	elif unitstr == 'GB':
		mult = 1000


	# do the thing
	size = num * mult
	return size



# thing
#
# expected format of input url:
# https://static.wikia.nocookie.net/khonjin-house/images/d/d9/Original_62.jpg/revision/latest?cb=20230922085712
#
def thing(url):
	url = url + '&format=original'
	return url



outpath = 'out'
if not os.path.exists(outpath):
    os.makedirs(outpath)

#i = 1
#while True:
#	if os.path.isfile('out' + str(i) + '.csv'):
#		i=i+1
#	else:
#		output_csv = open('out' + str(i) + '.csv','w+')
#		break

output_csv = open(os.path.join(outpath,'files.csv'),'w+')


# column headers
output_csv.write('\"Date\";')
output_csv.write('\"File (no spaces)\";')
output_csv.write('\"File Title\";')
output_csv.write('\"URL (1)\";')
output_csv.write('\"Size\";')
output_csv.write('\"User\";')
output_csv.write('\"Description\";')

#output_csv.write('\"SHA-1\"')
output_csv.write('\n')


totalimagesize = 0 # MB
totalrows = 0
start = 0
midrow = 0

with open ('in.html', 'rt') as inhtml:
	for line in inhtml:
		if start == 1:

			#if '</table>' in line:
			#	start = 0

			if midrow == 0:
				if '<tr>' in line:
					totalrows += 1
					midrow = 1
			else:

				# not efficient.
				#
				# unexpected behavior will happen if:
				# 1. any of the tags being searched for occur more than once in a single line of in.html
				#   (either because multiple rows are packed in a single line, or because fandom is doing something ungodly stupid.)
				#   (this should probably never occur.)

				spitoutdata(line, output_csv, '<td class="TablePager_col_img_timestamp">', '', '</td>')
				spitoutdata(line, output_csv, '<td class="TablePager_col_img_name">', '<a href="/wiki/File:', '"')
				spitoutdata(line, output_csv, '<td class="TablePager_col_img_name">', 'title="File:', '"')
				spitoutdata(line, output_csv, '<td class="TablePager_col_thumb">', '<a href="', '"')
				spitoutdata(line, output_csv, '<td class="TablePager_col_img_size">', '', '</td>')
				spitoutdata(line, output_csv, '<td class="TablePager_col_img_actor">', '<a href="/wiki/User:', '"')
				spitoutdata(line, output_csv, '<td class="TablePager_col_img_description">', '', '</td>')

				totalimagesize += spitoutdata_size(line, output_csv, '<td class="TablePager_col_img_size">')

				if ('<td class="TablePager_col_img_description">' in line) or ('</tr>' in line):
					output_csv.write('\n')
					midrow = 0


		else:
			if '<table class="mw-datatable listfiles">' in line:
				start = 1


inhtml.close
output_csv.close

print('Combined filesize of all files (images) = ' + f"{totalimagesize:.2f}" + ' MB')
print('Finished parsing table with ' + str(totalrows) + ' rows')
