from distutils.core import setup

setup(
    name='dataobj',
    version='2.4',
    packages=['dataobj', 'dataobj.validators'],
    url='',
    license='Apache',
    author='Christopher Lee',
    author_email='',
    description='Simple ORM package',
    requires=['pandas', 'dbutil']
)
