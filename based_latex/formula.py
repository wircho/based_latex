import os
import sys
import math
import json
import shutil
import random
import tempfile
import subprocess
import numpy as np
from PIL import Image

formula_tex = """
% https://tex.stackexchange.com/questions/44486/pixel-perfect-vertical-alignment-of-image-rendered-tex-snippets
\\documentclass[10pt]{article}
\\pagestyle{empty}
\\setlength{\\topskip}{0pt}
\\setlength{\\parindent}{0pt}
\\setlength{\\abovedisplayskip}{0pt}
\\setlength{\\belowdisplayskip}{0pt}

\\usepackage{geometry}
\\usepackage{xstring}

\\usepackage{amsmath}

\\newsavebox{\\snippetbox}
\\newlength{\\snippetwidth}
\\newlength{\\snippetheight}
\\newlength{\\snippetdepth}
\\newlength{\\pagewidth}
\\newlength{\\pageheight}
\\newlength{\\pagemargin}

\\begin{lrbox}{\\snippetbox}
$ {\\formula} $
\\end{lrbox}

\\settowidth{\\snippetwidth}{\\usebox{\\snippetbox}}
\\settoheight{\\snippetheight}{\\usebox{\\snippetbox}}
\\settodepth{\\snippetdepth}{\\usebox{\\snippetbox}}

\\setlength\\pagemargin{4pt}

\\setlength\\pagewidth\\snippetwidth
\\addtolength\\pagewidth\\pagemargin
\\addtolength\\pagewidth\\pagemargin

\\setlength\\pageheight\\snippetheight
\\addtolength{\\pageheight}{\\snippetdepth}
\\addtolength\\pageheight\\pagemargin
\\addtolength\\pageheight\\pagemargin

\\newwrite\\foo
\\immediate\\openout\\foo=\\jobname.json
% https://latex.org/forum/viewtopic.php?t=5180
\\begingroup 
   \\catcode`\\[ = 1\\relax
   \\catcode`\\] = 2\\relax
   \\catcode`\\{ = 12\\relax
   \\catcode`\\} = 12 \\relax 
   \\gdef\\OpenBrace[{]
   \\gdef\\CloseBrace[}]
\\endgroup
  \\immediate\\write\\foo{\\OpenBrace}
  \\immediate\\write\\foo{  "snippetdepth": "\\the\\snippetdepth",}
  \\immediate\\write\\foo{  "snippetheight": "\\the\\snippetheight",}
  \\immediate\\write\\foo{  "snippetwidth": "\\the\\snippetwidth",}
  \\immediate\\write\\foo{  "pagewidth": "\\the\\pagewidth",}
  \\immediate\\write\\foo{  "pageheight": "\\the\\pageheight",}
  \\immediate\\write\\foo{  "pagemargin": "\\the\\pagemargin"}
  \\immediate\\write\\foo{\\CloseBrace}
\\closeout\\foo

\\geometry{paperwidth=\\pagewidth,paperheight=\\pageheight,margin=\\pagemargin}

\\begin{document}
\\usebox{\\snippetbox}
\\end{document}
"""

def find_first_nonzero(l, start = 0, step = 1):
	i = start
	j = 0
	while l[i] == 0:
		j += 1
		i += step # Fails when out of bounds
	return j

class Formula:
	def __init__(self, expression, density = 512, factor = 1, process_timeout = 2):
		expression = expression.strip("$")
		folder = tempfile.mkdtemp()
		paths = dict((ext, os.path.join(folder, "formula." + ext)) for ext in ["tex", "pdf", "png", "json"])
		with open(paths["tex"], "w") as tex_file: tex_file.write(formula_tex)
		# subprocess.run(["pdflatex", "-output-directory", folder, "\\def\\formula{" + expression + "}\\input{" + paths["tex"] + "}"])
		subprocess.check_output(["pdflatex", "-output-directory", folder, "\\def\\formula{" + expression + "}\\input{" + paths["tex"] + "}"], stderr = subprocess.STDOUT, timeout = process_timeout)
		subprocess.check_output(["convert", "-density", str(density), paths["pdf"], "-quality", "100", paths["png"]], stderr = subprocess.STDOUT, timeout = process_timeout)
		img = Image.open(paths["png"])
		array = np.array(img)[:,:,1]
		row = array.sum(axis=0)
		col = array.sum(axis=1)
		left = find_first_nonzero(row)
		top = find_first_nonzero(col)
		right = find_first_nonzero(row, start = -1, step = -1)
		bottom = find_first_nonzero(col, start = -1, step = -1)
		with open(paths["json"], "r") as file: str_dims = json.load(file)
		dims = {}
		for key, value in str_dims.items(): dims[key] = float(value.replace("pt", ""))
		baseline_perc = (dims["pagemargin"] + dims["snippetdepth"]) / dims["pageheight"]
		top_perc = top / img.size[1]
		bottom_perc = bottom / img.size[1]
		baseline_perc = (baseline_perc - bottom_perc) / (1 - top_perc - bottom_perc)
		img = img.crop((left, top, img.size[0] - right, img.size[1] - bottom))
		self.folder = folder
		self.expression = expression
		self.factor = factor
		self.density = density
		self.image = img
		self.baseline_perc = baseline_perc
		pixel_width = img.size[0]
		pixel_height = img.size[1]
		self.pixel_width = pixel_width
		self.pixel_height = pixel_height
		self.pixel_height_bottom = int(self.pixel_height * baseline_perc + 0.5)
		self.pixel_height_top = self.pixel_height - self.pixel_height_bottom
		self.em_width = self.to_em(self.pixel_width)
		self.em_height = self.to_em(self.pixel_height)
		self.em_height_bottom = self.to_em(self.pixel_height_bottom)
		self.em_height_top = self.to_em(self.pixel_height_top)
		self.em_vertical_align = -baseline_perc * self.em_height

	def to_em(self, pixels):
		return pixels * 8 * self.factor / self.density

	# Naive method. Export cropped image and set height and vertical align.
	def save_image(self, path, class_name = "latex"):
		self.image.save(path)
		class_property = '' if class_name is None else ' class="' + class_name + '"'
		return f'<img{class_property} alt="{self.expression}" style="height:{round(self.em_height, 4)}em;vertical-align:{round(self.em_vertical_align, 4)}em" src="',\
					 '"/>'

	# Bad method. Export two (upper and lower) images.
	def save_split_images(self, path, class_name = "latex"):
		path, ext = os.path.splitext(path)
		path_bottom = path + "-bottom" + ext
		path_top = path + "-top" + ext
		self.image.crop((0, self.pixel_height_top, self.image.size[0], self.image.size[1])).save(path_bottom)
		self.image.crop((0, 0, self.image.size[0], self.pixel_height_top)).save(path_top)
		class_property = '' if class_name is None else ' class="' + class_name + '"'
		return f'<span{class_property} style="position:relative;display:inline-block;width:{round(self.em_width, 4)}em;height:{round(self.em_height_top, 4)}em;margin-bottom:{round(self.em_height_bottom, 4)}em;vertical-align:{round(-self.em_height_bottom, 4)}em;"><img style="position:absolute;top:0;left:0;width:100%;margin:0;padding:0;border-style:none;border:0;height:100%;" src="',\
		       f'"/><img style="position:absolute;top:100%;left:0;width:100%;margin:0;padding:0;border-style:none;border:0;height:{round(self.em_height_bottom, 4)}em;" src="',\
		       '"/></span>'

	# Preferred method. Export image with equal upper and lower heights.
	def save_symmetric_image(self, path, class_name = "latex", include_static_style = True):
		pixel_height_max = max(self.pixel_height_bottom, self.pixel_height_top)
		pixel_bottom_delta = pixel_height_max - self.pixel_height_bottom
		pixel_top_delta = pixel_height_max - self.pixel_height_top
		self.image.crop((0, -pixel_top_delta, self.image.size[0], 2 * pixel_height_max)).save(path)
		em_height = self.to_em(pixel_height_max)
		em_bottom_delta = self.to_em(pixel_bottom_delta)
		class_property = '' if class_name is None else ' class="' + class_name + '"'
		static_style = 'object-fit:cover;object-position:0 0;' if include_static_style else ''
		return f'<img{class_property} style="width:{round(self.em_width, 4)}em;height:{round(em_height, 4)}em;vertical-align:{round(-self.em_height_bottom, 4)}em;{static_style}" src="',\
           '">'

def save_latex_image(expression, path, density = 512, factor = 1, class_name = "latex", include_static_style = True, process_timeout = 2):
	formula = Formula(expression, density = density, factor = factor, process_timeout = process_timeout)
	result = formula.save_symmetric_image(path, class_name = class_name, include_static_style = include_static_style)
	shutil.rmtree(formula.folder)
	return result









