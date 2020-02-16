import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="based_latex",
    version="0.0.23",
    author="Adolfo Rodriguez",
    author_email="adolfo@interoper.io",
    description="Generates properly baselined images and HTML code from LaTeX formulas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wircho/based_latex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'Pillow'
    ]
)