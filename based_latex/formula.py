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
	\\usepackage{amsfonts}

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

def get_latex_svg_data(formula, margin = 4):
	# Trims dollar signs from formula
	formula = formula.strip("$")
	# Created new temporary folder
	folder = tempfile.mkdtemp()
	# Defines all paths to be used
	paths = dict((ext, os.path.join(folder, "formula." + ext)) for ext in [".tex", ".pdf", "_outlines.pdf", ".json",".svg"])
	# Writes TEX file
	with open(paths[".tex"], "w") as tex_file: tex_file.write(get_formula_tex(margin, margin, margin, margin))
	# Generates PDF from TEX file
	subprocess.run(["pdflatex", "-output-directory", folder, "-halt-on-error", "\\def\\formula{" + formula + "}\\input{" + paths[".tex"] + "}"])
	# Converts fonts to outlines and generates new PDF file
	subprocess.run(["gs", "-o", paths["_outlines.pdf"], "-dNoOutputFonts", "-sDEVICE=pdfwrite", paths[".pdf"]])
	# Generates SVG from PDF
	subprocess.run(["inkscape", "-l", paths[".svg"], paths["_outlines.pdf"]])
	# Loads JSON file parameters generated during TEX compilation
	with open(paths[".json"], "r") as file: str_dimensions = json.load(file)
	dimensions = {}
	for key, value in str_dimensions.items(): dimensions[key] = float(value.replace("pt", ""))
	# Reads SVG code (minus first line <!--<xml...>-->)
	with open(paths[".svg"], "r") as file: svg = "\n".join(file.readlines()[1:])
	# Removes temporary folder
	shutil.rmtree(folder)
	# Returns dimensions dictionary and SVG code in a JSON dictionary
	return {
		"dimensions": dimensions,
		"svg": svg
	}




