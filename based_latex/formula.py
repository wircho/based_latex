import os
import sys
import math
import json
import shutil
import random
import tempfile
import subprocess
import xml.etree.ElementTree as ET

def get_formula_tex(lmargin, tmargin, rmargin, bmargin):
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
	\\newlength{\\pagelmargin}
	\\newlength{\\pagetmargin}
	\\newlength{\\pagermargin}
	\\newlength{\\pagebmargin}

	\\begin{lrbox}{\\snippetbox}
	$ {\\formula} $
	\\end{lrbox}

	\\settowidth{\\snippetwidth}{\\usebox{\\snippetbox}}
	\\settoheight{\\snippetheight}{\\usebox{\\snippetbox}}
	\\settodepth{\\snippetdepth}{\\usebox{\\snippetbox}}

	\\setlength\\pagelmargin{""" + str(lmargin) + """pt}
	\\setlength\\pagetmargin{""" + str(tmargin) + """pt}
	\\setlength\\pagermargin{""" + str(rmargin) + """pt}
	\\setlength\\pagebmargin{""" + str(bmargin) + """pt}

	\\setlength\\pagewidth\\snippetwidth
	\\addtolength\\pagewidth\\pagelmargin
	\\addtolength\\pagewidth\\pagermargin

	\\setlength\\pageheight\\snippetheight
	\\addtolength{\\pageheight}{\\snippetdepth}
	\\addtolength\\pageheight\\pagetmargin
	\\addtolength\\pageheight\\pagebmargin

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
	  \\immediate\\write\\foo{  "pagelmargin": "\\the\\pagelmargin",}
	  \\immediate\\write\\foo{  "pagermargin": "\\the\\pagermargin",}
	  \\immediate\\write\\foo{  "pagetmargin": "\\the\\pagetmargin",}
	  \\immediate\\write\\foo{  "pagebmargin": "\\the\\pagebmargin"}
	  \\immediate\\write\\foo{\\CloseBrace}
	\\closeout\\foo

	\\geometry{paperwidth=\\pagewidth,paperheight=\\pageheight,lmargin=\\pagelmargin,tmargin=\\pagetmargin,rmargin=\\pagermargin,bmargin=\\pagebmargin}

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
	def __init__(self, expression, margin = 4, process_timeout = 2):
		self.expression = expression.strip("$")
		self.populate(margin, process_timeout)
		

	def populate(self, margin, process_timeout):
		folder = tempfile.mkdtemp()
		paths = dict((ext, os.path.join(folder, "formula." + ext)) for ext in ["tex", "pdf", "png", "json","svg"])
		paths1 = dict((ext, os.path.join(folder, "formula1." + ext)) for ext in ["tex", "pdf", "png", "json","svg"])
		with open(paths["tex"], "w") as tex_file: tex_file.write(get_formula_tex(margin, margin, margin, margin))
		subprocess.check_output(["pdflatex", "-output-directory", folder, "\\def\\formula{" + self.expression + "}\\input{" + paths["tex"] + "}"], stderr = subprocess.STDOUT, timeout = process_timeout)
		subprocess.check_output(["gs", "-o", paths1["pdf"], "-dNoOutputFonts", "-sDEVICE=pdfwrite", paths["pdf"]], stderr = subprocess.STDOUT, timeout = process_timeout)
		subprocess.check_output(["inkscape", "-l", paths["svg"], paths1["pdf"]], stderr = subprocess.STDOUT, timeout = process_timeout)
		with open(paths["json"], "r") as file: str_dims = json.load(file)
		dims = {}
		for key, value in str_dims.items(): dims[key] = float(value.replace("pt", ""))
		self.folder = folder
		self.paths = paths
		self.dimensions = dims
		with open(paths["svg"], "r") as file: self.svg = "\n".join(file.readlines()[1:]) # Ignored first line's <!--<xml...>-->

	def get_svg_data(self):
		return {
			"dimensions": self.dimensions,
			"svg": self.svg
		}

	def clear(self):
		shutil.rmtree(self.folder)


def get_latex_svg_data(expression, margin = 4, process_timeout = 2):
	formula = Formula(expression, margin = margin, process_timeout = process_timeout)
	result = formula.get_svg_data()
	formula.clear()
	del formula
	return result









