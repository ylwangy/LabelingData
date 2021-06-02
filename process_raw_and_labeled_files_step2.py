import xlrd
import argparse
import itertools

moviestyles={'文学类':0,'演讲类':1,'影视类':2,'生活类':3,'':4}
sentitypes={'厌恶':0,'失望':0,'愤怒':0,'恐惧':0,'悲痛':0,'邪恶':0,'惊恐':0,'担忧':0,'悲伤':0,'焦急':0,
			'兴奋':1,'好奇':1,'平静':1,'神秘':1,'紧张':1,'嚣张':1,'惊讶':1,
			'激动':2,'温情':2,'可爱':2,'深情':2,'喜悦':2,'惊喜':2,'关爱':2,
			'':3}

id2_sent_style_background={}

def process(labelfile,srcfile,tgt):
	xl_workbook = xlrd.open_workbook(labelfile)
	xl_sheet = xl_workbook.sheet_by_index(0)

	### need change
	for i in itertools.count(9):
		vals = []
		try:
			row = xl_sheet.row(i)  #  row
		except:
			print(i)
			break
		for idx, cell_obj in enumerate(row):

			if idx >=10:
				break
			if idx==0:
				if not (cell_obj.value):
					break
				print('id:')
				print((cell_obj.value))
				print(int(cell_obj.value))
				vals.append(int(cell_obj.value))
			if idx==4:
				# print('background:')
				print(cell_obj.value)
				if len(cell_obj.value.strip())>0:
					vals.append(cell_obj.value.strip())
				else:
					vals.append(' ')
				# aa = input()
			if idx==5:
				# print('Styles')
				print(moviestyles[cell_obj.value])
				vals.append(moviestyles[cell_obj.value])
				# aa = input()
			if idx==9:
				# print('Senti')
				if '、' in cell_obj.value:
					print(sentitypes[cell_obj.value.strip().split('、')[0]])
					vals.append(sentitypes[cell_obj.value.strip().split('、')[0]])
				else:
					print(sentitypes[cell_obj.value.strip()])
					vals.append(sentitypes[cell_obj.value.strip()])
		print(vals)

		if len(vals)>0:
			id2_sent_style_background.update ({vals[0]:[vals[1],vals[2],vals[3]] })

	with open(tgt,'a+',encoding='utf-8') as ff:
		with open(srcfile,'rb') as f:
			for line in f:
				ids = line.strip().decode('utf-8').split('###')[0]
				ff.write(line.strip().decode('utf-8'))
				ff.write('###')
				ff.write(id2_sent_style_background[int(ids)][0])
				ff.write('###')
				ff.write(str(id2_sent_style_background[int(ids)][1]))
				ff.write('###')
				ff.write(str(id2_sent_style_background[int(ids)][2]))
				ff.write('\n')

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--labeledfile', default="label_data_raw_v1.xls")
	parser.add_argument('--srcfile', default="uploads/file_1_step1.txt")
	parser.add_argument('--tgt', default="uploads/file_1_step2.txt")
	args = parser.parse_args()

	process(args.labeledfile,args.srcfile,args.tgt)