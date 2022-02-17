from setuptools import setup

setup(
    name='sekube',
    version='0.1.0',
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
