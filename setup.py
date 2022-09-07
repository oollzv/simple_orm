import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='sql_records',
    version='1.0.0',
    author='zlqm',
    description='small mysql tool',
    install_requires=['pymysql', 'tablib'],
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)