from distutils.core import setup

setup(
    name='dataobj',
    version='2.2',
    packages=['dataobj', 'dataobj.sqlargs', 'dataobj.validators'],
    url='',
    license='Apache',
    author='Christopher Lee',
    author_email='',
    description='Simple ORM package',
    requires=['pandas']
)
