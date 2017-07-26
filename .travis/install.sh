# Install dependency: `pymysqlpool`
git clone --depth=50 --branch=master https://github.com/0xE8551CCB/pymysqlpool.git dependencies/pymysqlpool
python dependencies/pymysqlpool/setup.py install

# Install dependency: `dbutil`
git clone --depth=50 --branch=master https://github.com/0xE8551CCB/dbutil.git dependencies/dbutil
python dependencies/dbutil/setup.py install

# Install other dependencies
pip install pandas
pip install pymysql
