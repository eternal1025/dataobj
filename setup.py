from distutils.core import setup

setup(
    name='dataobj',
    version='0.2',
    packages=['dataobj'],
    url='',
    license='Apache',
    author='Chris',
    author_email='limeng@moviewisdom.cn',
    description='Simple ORM package.',
    requires=['pymysql', 'ys-sqlbuilder']
)
