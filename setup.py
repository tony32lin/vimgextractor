from setuptools import setup, find_packages

setup(
    name='vimgextractor',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'numpy',
        'pandas',
        'tables'
    ],
    entry_points='''
        [console_scripts]
        extractImgFromVEGAS_St2=vimgextractor.script.convert:cli 
    '''
)
