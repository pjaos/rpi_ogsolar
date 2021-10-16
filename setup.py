from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ogsolar",                                  # The python module name.
    version="4.3",                                   # The version of the module.
    author="Paul Austen",                            # The name of the module author.
    author_email="pausten.os@gmail.com",             # The email address of the author.
    description="A Raspberry PI application for controlling EPEver Tracer off grid solar installations.", # A short description of the module.
    long_description="",                             # The long description is contained in the README.md file.
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",                           # The License that the module is distributed under
    url="https://github.com/pjaos/rpi_ogsolar",      # The home page for the module
    install_requires=[
        ['p3lib>=1.1.23','tornado>=6.1','pymodbus>=2.5.2'],            # A python list of required module dependencies (optionally including versions)
    ],
    scripts=['scripts/ogsolar','scripts/tracer'],    # A list of command line startup scripts to be installed.
)
