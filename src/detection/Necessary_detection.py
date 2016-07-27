import json
PATH = './detection/'

class Necessary_detection():
	def __init__(self):
		f = open(PATH+'tops_203_nec_valid.json')
		tops = json.loads(f.read())
		f.close()
		self.nec_dic = {}
		for top in tops:
			self.nec_dic[top['topid']] = [term.lower() for term in top['necessary']]

	def nec_detection(self, text):
		text = text.lower()
		for topid in self.nec_dic.keys():
			necessary = True
			for term in self.nec_dic[topid]:
				if term not in text:
					necessary = False
			if necessary:
				return topid, self.nec_dic[topid]
		return None, None




		