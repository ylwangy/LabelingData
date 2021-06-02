import argparse

def process(srcfile,nerfile):
	with open(nerfile,'a+',encoding='utf-8') as ff:
		with open(srcfile,'rb') as f:
			for line in f:
				if len(line.strip())>0:
					l=line.strip().decode('utf-8').split('###')
					assert len(l)==6   #   id ,  en,   cn,   background,    style,  sentiment
					ff.write('###')
					ff.write(l[0])
					ff.write('###')
					ff.write(l[3])
					ff.write('\n')
					sent_cn = l[2].replace('[CN]','。')
					for c in sent_cn:
						ff.write(c)
						ff.write('\n')
					ff.write('\n')


if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument('--srcfile', default="uploads/file_1_step2.txt")
	parser.add_argument('--tgt_ner', default="ner.train.txt")
	args = parser.parse_args()

	process(args.srcfile,args.tgt_ner)