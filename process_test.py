import os
import argparse

def process(srcdir,sentifile,stylefile,nerfile):
	list = os.listdir(srcdir)
	# print(list)
	for i in range(len(list)):
		path = os.path.join(srcdir, list[i])
		if path.endswith('.srt'):
			print(path)
			PreText = False
			sents = []
			with open(path, 'rb') as f:
				sent = []
				for line in f:
					if len(line.decode('utf-8').strip()) > 0:
						print(line)
						print(line.decode('utf-8'))
						line = line.strip().replace(b'\xe2\x80\x8b', b'').decode('utf-8').strip()
						sent.append(line)
						PreText = True
					elif PreText:
						# print(sent)
						# assert len(sent)==4
						assert '-->' in sent[1]
						assert len(sent[0].split()) == 1

						sents.append(sent)
						sent = []
						PreText = False
					else:
						continue
			print(sents)

			with open(sentifile,'a+',encoding='utf-8') as ff:
				ff.write(list[i].split('_')[-1].split('.')[0])
				ff.write('###')
				for i in range(len(sents)):
					ff.write(sents[i][2])
				ff.write('\n')
			with open(stylefile,'a+',encoding='utf-8') as ff:
				ff.write(list[i].split('_')[-1].split('.')[0])
				ff.write('###')
				for i in range(len(sents)):
					ff.write(sents[i][2])
				ff.write('\n')
			check_cn_en=True
			if len(sents) >0 :
				for i in range(len(sents)):
					if not len(sents[i])==4:
						check_cn_en = False
			if check_cn_en:
				with open(nerfile,'a+',encoding='utf-8') as ff:
					ff.write('###')
					ff.write(list[i].split('_')[-1].split('.')[0])
					ff.write('\n')
					sent_cn =''
					for i in range(len(sents)):
						sent_cn +=(sents[i][3])
						sent_cn += '。'
					for c in sent_cn:
						ff.write(c)
						ff.write('\n')
					ff.write('\n')


if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument('--srcdir', default="test1000")
	parser.add_argument('--test_senti', default="senti.test.txt")
	parser.add_argument('--test_style', default="style.test.txt")
	parser.add_argument('--test_ner', default="ner.test.txt")
	args = parser.parse_args()

	process(args.srcdir,args.test_senti,args.test_style,args.test_ner)