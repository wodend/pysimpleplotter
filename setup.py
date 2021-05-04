import setuptools

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''


setuptools.setup(
    name="PySimplePlotter",
    version="beta",
    description="GUI plotting front-end to basic Matplotlib and Pandas features.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="GUI UI wrapper simple matplotlib pandas plotter plot",
    url="https://github.com/wodend/pysimpleplotter",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
        "Framework :: Matplotlib",
    ),
    entry_points={
        "console_scripts": [
            "pysimpleplotter=pysimpleplotter:main",
        ]
    },
)
