from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="git2sqlite",
    version="0.0.1",
    description="Tool for importing AZDO Git repositories into SQLite",
    author="Stephen L. McMahon",
    author_email="stephen@slmcmahon.com",
    license="MIT",
    py_modules = ['git2sqlite', 'app'],
    packages=find_packages(),
    install_requires = [requirements],
    long_description = long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        git2sqlite=git2sqlite:main
    '''
)