# based_latex

Generates SVG image code from LaTeX formulas.

## Installation

```
pip install based_latex
```

## Requirements

This package requires a [LaTeX distribution](https://www.latex-project.org/), as well as [Ghostscript](https://www.ghostscript.com/) and [Inkscape](https://inkscape.org/).

## Usage

Use the function `based_latex.get_latex_svg_data(expression)` to get a dictionary of the form

```
{
	dimensions: # Some dimension parameters (useful for HTML embedding)
	svg: # The SVG code.
}
```