from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='sekube',
    version='0.1.5',
    description='Incredibly naivé program to read secrets from a kubernettes cluster',
    long_description=readme,
    author='Simon Albinsson',
    author_email='pipmon@zinob.se',
    url='https://github.com/zinob/sekube/',
    license='MIT',
    py_modules=['sekube'],
    install_requires=[
        'Click',
        'kubernetes',
        'editdistance'
    ],
    entry_points={
        'console_scripts': [
            'sekube = sekube:cli',
        ],
    },
)
