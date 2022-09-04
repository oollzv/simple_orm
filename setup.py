import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='simple_orm',
    version='1.0.0',
    author='zlqm',
    description='small mysql tool',
    install_requires=['pymysql'],
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)