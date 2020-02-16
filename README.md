# based_latex

Generates properly baselined images and HTML code from LaTeX formulas.

## Installation

```
pip install based_latex
```

## Requirements

This package requires a [LaTeX distribution](https://www.latex-project.org/), as well as [Inkscape](https://inkscape.org/) and the [ImageMagick package](https://imagemagick.org/) (this last requirement may be soon removed).

## Usage

Use the function `based_latex.save_latex_image(expression, path)` to save a LaTeX image of the formula in `expression` at `path`. This function also returns two variables `prefix` and `suffix` with which you can construct the proper HTML code to embed the image, by simply concatenating `prefix + image_url + suffix`

```python
import based_latex
prefix, suffix = based_latex.save_latex_image("\\frac{n^2+1}{n!}", "formula.png")
# Image is now saved at formula.png
print(prefix + "formula.png" + suffix)
# <span class="latex" style="position:relative;display:inline-block;vertical-align:0;width:2.125em;height:1.1406em;margin-bottom:0.4062em;"><img style="position:absolute;top:0;left:0;width:100%;height:200%;margin:0;padding:0;border-style:none;border:0;" src="formula.png"/></span>
```

Some optional parameters of `based_latex.save_latex_image`, with their respective default elements, are:

### `density = 512`
This parameter is used by ImageMagick's `convert` command, and is proportional to the generated image's resolution.

### `factor = 1`
HTML code is normally generated to match the element's font, multiplied by `factor`.

### `class_name = "latex"`
The wrapping `<span>` element has this css class.

### `include_static_style = True`
(Documentation coming soon)

### `process_timeout = 2`
This is the timeout of the `pdflatex` and `convert` (from ImageMagick) commands. After this timeout, the function will raise an exception if, for example, your formula happens to have a syntax error.