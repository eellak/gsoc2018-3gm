from distutils.core import setup

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

install_reqs = parse_requirements('./requirements.txt')
files = ["src/*"]

setup(name = "3gm",
    version = "1.0",
    description = "Government Gazette text mining, cross linking, and codification in the context of GSoC 2018 by GFOSS",
    author = "Marios Papachristou",
    author_email = "papachristoumarios@gmail.com",
    url = "https://github.com/eellak/gsoc2018-3gm",
    instal_requires=install_reqs
    packages = ['core'],
    package_data = {'core' : files },
    scripts = [],
    )
