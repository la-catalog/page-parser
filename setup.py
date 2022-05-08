from pathlib import Path

from setuptools import find_packages, setup

long_description = Path("README.md").read_text()

setup(
    name="page-parser",
    version="0.0.1",
    description="Collect the page information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiagola92/page-parser",
    author="thiagola92",
    author_email="thiagola92@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords="parse, html",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "structlog==21.5.0",
        "parsel==1.6.0",
        "page-sku==0.0.1",
        "la-catch==0.0.3",
    ],
    python_requires=">=3.10",
)
