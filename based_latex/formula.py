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
import xml.etree.ElementTree as ET

def get_formula_tex(margin):
	return """
	% https://tex.stackexchange.com/questions/44486/pixel-perfect-vertical-alignment-of-image-rendered-tex-snippets
	\\documentclass[10pt]{article}
	\\pagestyle{empty}
	\\setlength{\\topskip}{0pt}
	\\setlength{\\parindent}{0pt}
	\\setlength{\\abovedisplayskip}{0pt}
	\\setlength{\\belowdisplayskip}{0pt}

	\\usepackage[T1]{fontenc}

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

	\\setlength\\pagemargin{""" + str(margin) + """pt}

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
	def __init__(self, expression, process_timeout = 3):
		self.expression = expression.strip("$")
		margin = 4
		self.populate(margin, process_timeout = process_timeout)
		tree = ET.parse(self.paths["svg"])
		svg = tree.getroot()
		svg_height = float(svg.get("height"))
		print("Got height: " + str(svg_height))
		new_pageheight = self.dimensions["pageheight"] * math.ceil(svg_height) / svg_height
		new_margin = margin + (new_pageheight - self.dimensions["pageheight"]) / 2
		self.clear()
		self.populate(new_margin, process_timeout = process_timeout)
		

	def populate(self, margin, process_timeout = 3):
		folder = tempfile.mkdtemp()
		paths = dict((ext, os.path.join(folder, "formula." + ext)) for ext in ["tex", "pdf", "png", "json","svg"])
		paths1 = dict((ext, os.path.join(folder, "formula1." + ext)) for ext in ["tex", "pdf", "png", "json","svg"])
		with open(paths["tex"], "w") as tex_file: tex_file.write(get_formula_tex(margin))
		subprocess.check_output(["pdflatex", "-output-directory", folder, "\\def\\formula{" + self.expression + "}\\input{" + paths["tex"] + "}"], stderr = subprocess.STDOUT, timeout = process_timeout)
		subprocess.check_output(["gs", "-o", paths1["pdf"], "-dNoOutputFonts", "-sDEVICE=pdfwrite", paths["pdf"]], stderr = subprocess.STDOUT, timeout = process_timeout)
		subprocess.check_output(["inkscape", "-l", paths["svg"], paths1["pdf"]], stderr = subprocess.STDOUT, timeout = process_timeout)
		with open(paths["json"], "r") as file: str_dims = json.load(file)
		dims = {}
		for key, value in str_dims.items(): dims[key] = float(value.replace("pt", ""))
		self.folder = folder
		self.paths = paths
		self.dimensions = dims

	def save_svg(self, path):
		shutil.copyfile(self.paths["svg"], path)
		return {
			"dimensions": self.dimensions
		}

	def clear(self):
		shutil.rmtree(self.folder)


def save_latex_image(expression, path, process_timeout = 2):
	formula = Formula(expression, process_timeout = process_timeout)
	result = formula.save_svg(path)
	formula.clear()
	return result









