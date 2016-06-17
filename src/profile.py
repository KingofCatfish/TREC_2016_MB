import xml.dom.minidom
from config import PROFILE_2015_PATH, PROFILE_2014_PATH, PROFILE_2013_PATH, PROFILE_2012_PATH, PROFILE_2011_PATH

class profile:
	'This class is for profile of interested topic'
	def __init__(self, index, title, desc, narr):
		self.index = index
		self.title = title
		self.description = desc
		self.narritive = narr

	def __str__(self):
		str = 'Index : ' + self.index + '\n'
		str += 'Title : ' + self.title + '\n'
		str += 'Description : ' + self.description + '\n'
		str += 'Narrtive : ' + self.narritive
		return str

def xml_data(element, name):
	'Extract the data from the first child in a given xml element'
	try:
		return element.getElementsByTagName(name)[0].firstChild.data
	except IndexError:
		return ''

def load_profile_data(file_path):
	'''
	Load TREC Microblog Track Profile Data
	
	Smaple Usage:
		data = load_profile_data(PROFILE_2015_PATH)
		print(data[0])

	'''
	dom = xml.dom.minidom.parse(file_path).documentElement
	return [profile(xml_data(item, 'num'), xml_data(item, 'title'), xml_data(item, 'desc'), xml_data(item, 'narr')) for item in dom.getElementsByTagName('top')]

if __name__ == '__main__':
	data = load_profile_data(PROFILE_2011_PATH)
	print(data[5])
