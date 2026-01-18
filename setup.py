from setuptools import setup, find_packages

setup(
    name="analog",
    version="0.1.0",
    py_modules=['main','db','watch_item'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts':[
            'analog=main:cli',
        ],
    },
)
