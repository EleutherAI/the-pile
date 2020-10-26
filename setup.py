import setuptools
import os
from io import open as io_open

src_dir = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

# Build requirements
extras_require = {}
requirements_dev = os.path.join(src_dir, 'requirements-dev.txt')
with io_open(requirements_dev, mode='r') as fd:
    extras_require['dev'] = [i.strip().split('#', 1)[0].strip()
                             for i in fd.read().strip().split('\n')]

setuptools.setup(
    name="the-pile",
    version="0.0.1",
    author="EleutherAI",
    author_email="leogao31@gmail.com",
    description="The Pile is a large, diverse, open source language modelling data set that consists of many smaller datasets combined together.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EleutherAI/the-pile",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.6',
    extras_require=extras_require,
    packages=['the_pile'],
    package_data={'the_pile': ['LICENCE', 'requirements-dev.txt']},
)
