from setuptools import setup
import os

long_description = """Something"""

install_requires = []

setup(
    name="hyrepl",
    version="0.0.1",
    install_requires=install_requires,
    scripts=[
        "bin/hyrepl"    
    ],
    packages=[
        'hyrepl'
    ],
    author="Paul Tagliamonte",
    author_email="tag@pault.ag",
    long_description=long_description,
    description='Something',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Lisp",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
    ]
)
