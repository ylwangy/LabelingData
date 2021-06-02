import argparse

def process(srcfile,sentifile,stylefile):
	with open(sentifile,'a+',encoding='utf-8') as ff:
		with open(srcfile,'rb') as f:
			for line in f:
				if len(line.strip())>0:
					l=line.strip().decode('utf-8').split('###')
					assert len(l)==6   #   id ,  en,   cn,   background,    style,  sentiment
					ff.write(l[0])
					ff.write('###')
					ff.write(l[1].replace('[EN]',''))
					ff.write('###')
					ff.write(l[3])
					ff.write('###')
					ff.write(l[5])
					ff.write('\n')

	with open(stylefile,'a+',encoding='utf-8') as ff:
		with open(srcfile,'rb') as f:
			for line in f:
				if len(line.strip())>0:
					l=line.strip().decode('utf-8').split('###')
					assert len(l)==6   #   id ,  en,   cn,   background,    style,  sentiment
					ff.write(l[0])
					ff.write('###')
					ff.write(l[1].replace('[EN]',''))
					ff.write('###')
					ff.write(l[3])
					ff.write('###')
					ff.write(l[4])
					ff.write('\n')

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument('--srcfile', default="uploads/file_1_step2.txt")
	parser.add_argument('--tgt_senti', default="senti.train.txt")
	parser.add_argument('--tgt_style', default="style.train.txt")
	args = parser.parse_args()

	process(args.srcfile,args.tgt_senti,args.tgt_style)