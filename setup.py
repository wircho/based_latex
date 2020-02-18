import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "0.0.48"

if __name__ == "__main__":
    setuptools.setup(
        name="based_latex",
        version=version,
        author="Adolfo Rodriguez",
        author_email="adolfo@interoper.io",
        description="Generates properly baselined images and HTML code from LaTeX formulas.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/wircho/based_latex",
        packages=["based_latex"],
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