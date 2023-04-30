from PIL import Image, ImageDraw, ImageFont
from barcode.writer import ImageWriter
from loguru import logger
from io import BytesIO
from datetime import datetime
import os
import barcode

class Sticker:
	def __init__(self, content, options):
		
		self.article = content['article']
		self.title = content['title']
		self.base_price = content['base_price']
		self.discount = content['discount']
		self.new_price = content['new_price']
		self.code = content['code']
		self.description = content['description']
		self.other = content['other']

		self.base_file = options['base_file']
		self.font_style = options['font_style']
		self.font_color = options['font_color']
		self.out_format = options['out_format']
		self.out_name = options['out_name']

	def OpenBaseFile(self):
		try:
			file = Image.open(self.base_file)
			return file
		except FileNotFoundError:
			logger.error(f'No such base file in: {os.getcwd()}')
		except Exception:
			logger.error(f'Base file opening error')

	def font(self, size):
		return ImageFont.truetype(
			self.font_style, 
			size=size
			)

	@staticmethod
	def TextWrap(file, text, font_size):
		size = 0
		result = ''
		list_of_strings = text.split(' ')
		for x in range(len(list_of_strings)):
			if size >= file.size[0]-30:
				list_of_strings[x] = list_of_strings[x] + '\n'
				size = 0
			else:
				size = size + len(list_of_strings[x]) * font_size
			result += list_of_strings[x] + ' '
		return result

	def draw(self, raw, pos, font, text):
		raw.text((pos[0], pos[1]), text, font=font, fill=self.font_color)

	def DrawText(self):
		file = self.OpenBaseFile()
		raw = ImageDraw.Draw(file)

		if self.article:
			self.draw(raw,(20, 5), self.font(30), self.article)
			self.draw(raw,(410, 5),self.font(24), f'{datetime.now().date()}')

		if self.title:
			font_size = file.size[0]//25
			self.draw(raw,(20, file.size[1]//8),self.font(font_size), self.TextWrap(file, self.title, font_size))

		if self.description:
			self.draw(raw,(20, file.size[1]//3),self.font(20), self.TextWrap(file, self.description, font_size))

		if self.other:
			text = ' | '.join(self.other)
			self.draw(raw, (20, file.size[1]-240), self.font(21), self.TextWrap(file, text, 21))
		if self.base_price:
			pos = (20, file.size[1]-190)
			self.draw(raw, pos, self.font(32), f'Цена: {self.base_price}')
			if self.discount:
				self.draw(raw, (pos[0]+(5+len(self.base_price))*25, pos[1]), self.font(32), f'sale {self.discount}% = {self.new_price}')

		if self.code:
			fp = BytesIO()
			EAN = barcode.get_barcode_class('ean13')
			EAN(self.code, writer=ImageWriter()).write(fp)
			file.paste(Image.open(fp).resize(
				(file.size[0]-80,file.size[1]//4)), # code size
				(30,file.size[1]-140) # code position
				)

		file.save(self.out_name+self.out_format)

options = {
	'base_file': '', # path to blank 600x600 file
	'font_style': 'sfns-display-bold.ttf', # path to font file
	'font_color': '#000000',
	'out_format': '.png', #.jpg , .png , .pdf ...
	'out_name': 'sticker'
}

content = {
	'article': 'f43L1PqDv67',
	'title': 'Название товара',
	'base_price': '200000',
	'discount': '50',     #---\
	'new_price': '100000',#---/
	'code': '123456789012',
	'description': 'Описание товара',
	'other': ('China', 'Black', 'Metall', 'XXL', '45-46')
}

Sticker(content, options).DrawText()

