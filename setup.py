import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Toto",
    version="0.0.1",
    author="Remy Zyngfogel",
    author_email="R.zyngfogel@calypso.science",
    description="A toolbox for processing timeseries'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calypso-science/Toto",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)