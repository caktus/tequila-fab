# Always prefer setuptools over distutils
from setuptools import setup

setup(
    name='tequila-fab',
    version='0.0.6',
    packages=[
        'tequila_fab',
    ],
    url='https://github.com/caktus/tequila-fab',
    author='Caktus Group',
    author_email='',
    description='',
    install_requires=[
        'Fabric3',
        'pyyaml',
    ],
    python_requires='>=2.7',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
    ]
)
