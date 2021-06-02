import argparse
import os


def write_sents(name_id,outfile,sents):
	print(name_id)
	for i in range(len(sents)):
		if not len(sents[i])==4:
			return None


	with open(outfile,'a+',encoding='utf-8') as f:
		f.write(name_id.split('_')[-1].split('.')[0])
		f.write('###')
		for i in range(len(sents)):
			f.write(sents[i][2])
			f.write('[EN]')
		f.write('###')
		for i in range(len(sents)):
			f.write(sents[i][3])
			f.write('[CN]')
		f.write('\n')


def process(srcdir,outfile):
	list = os.listdir(srcdir)
	# print(list)
	for i in range(len(list)):
		path = os.path.join(srcdir, list[i])
		# print(list[i])
		# print(path)
		if path.endswith('.srt') :
			print(path)
			PreText = False
			sents = []
			with open(path,'rb') as f:
				sent=[]
				for line in f:
					if len(line.strip()) > 0:
						print(line)
						line=line.strip().replace(b'\xe2\x80\x8b',b'').decode('utf-8').strip()
						print(line)
						sent.append(line)
						PreText=True
					elif PreText:
						# print(sent)
						# assert len(sent)==4
						assert '-->' in sent[1]
						assert len(sent[0].split())==1

						sents.append(sent)
						sent=[]
						PreText=False
					else:
						continue
			print(sents)
			write_sents(list[i], outfile, sents)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--srcdir', default="uploads/file_1")
	parser.add_argument('--tgt', default="uploads/file_1_step1.txt")
	args = parser.parse_args()

	process(args.srcdir,args.tgt)