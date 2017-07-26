# Install dependency: `pymysqlpool`
git clone --branch=master https://github.com:0xE8551CCB/pymysqlpool.git
python pymysqlpool/setup.py install

# Install dependency: `dbutil`
git clone --branch=master https://github.com/0xE8551CCB/dbutil.git
python dbutil/setup.py install

# Install other dependencies
pip install pandas
pip install pymysql
