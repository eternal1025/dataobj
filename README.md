# 说明
`dataobj` 是一个简易的仿 ORM 的 Python 包，仅支持有限的 MySQL SQL 操作子集。详细的使用测试参见 `tests` 目录下的代码。

# 调用过程
1. 上层应用数据层对象 `XDataObject`；
2. `dataobj` 进行字段类型检查、表字段名映射等；
3. 调用 `sqlargs` 包生成定制的 SQL 模板及相应参数；
4. 调用 `some_db_dao` 对象提供的数据库操作方法（要求实现 `execute(sql, args)`, `query(sql, args)` 接口）完成数据库操作。

# 结构说明
1. `manager`：实现数据库相关的查询、更新、删除、插入等操作；
2. `model`：一个数据层对象的抽象；
3. `fields`：提供了用于映射的字段类型，提供字段校验等机制；
4. `converters`：一些常用的类型转换工具；
5. `reflector`：用于自动映射数据库表到 Model 的工具；
6. `utils`：常用的工具函数；
7. `exceptions`：异常集合；
8. `validators`：集成了一些公共的字段检验模块；
9. `sqlargs`：用于生成 SQL 的工具包。

# 使用示例
1. 首先实现一个 DAO 层对象，提供基本的数据库操作接口

```python
class TestDao(object):
    @staticmethod
    def execute(sql, args):
        print(sql, args)

    @staticmethod
    def query(sql, args):
        print(sql, args)
```


1. 其次，定制一个数据层对象

```python
import datetime
from dataobj import Model, IntField, StrField, DatetimeField

class Folder(Model):
    folder_id = IntField(db_column='id', primary_key=True, auto_increment=True)
    name = StrField(default='新建文件夹')
    icon_url = StrField(not_null=True)
    
    # default 还可以是一个 `callable` 的对象
    create_at = DatetimeField(default=datetime.datetime.now)
    
    class Meta:
        # 如果不定义表名，则默认为 Model 的 Class 名称的 `camel` 格式
        table_name = 'folder'
        
        # 需要指定 dao_class 用于和数据库交互
        dao_class = TestDao
```

1. 接下来进行基本的 CRUD 操作

```python
# 创建对象并写入数据库
folder = Folder(name='测试文件夹', icon_url='test.png')
folder.dump()

# 读取操作
# 加载指定 ID 的对象
folder = Folder.objects.get(folder_id=100)

# 过滤操作
folders = list(Folder.objects.filter(folder_id=100))

# 获取所有的对象
folders = list(Folder.objects.all())

# 更新操作
folder = Folder.objects.get(folder_id=100)
folder.update(name='更新文件夹')

# 删除操作
folder.delete()
```

1. 更加丰富的过滤操作示例（详细的最新示例参见：`tests/test_crud.py` 文件）

```python
# 查找指定名称的文件夹
f = Folder.objects.get(name='某某文件夹')
f = Folder.objects.get(name__eq='某某文件夹')

# 查找包含字符串的文件夹
f = Folder.objects.filter(name__contains='娱乐')
f = Folder.objects.filter(name__startswith='测试').order_by('folder_id')
f = Folder.objects.filter(name__endswith='影视')

# 查找图标为 NULL 的文件夹
f = Folder.objects.filter(icon_url__isnull=True)

# 查找图标不为 NULL 的文件夹
f = Folder.objects.filter(icon_url__isnull=False)

# 查找 id 大于或大于等于某个值的文件夹
f = Folder.objects.filter(folder_id__gt=2)
f = Folder.objects.filter(folder_id__gte=2)

# 查找 id 小于或小于等于某个值的文件夹
f = Folder.objects.filter(folder_id__le=2)
f = Folder.objects.filter(folder_id__lte=2)

# 查找 id 不等于某个值的文件夹
f = Folder.objects.filter(folder_id__ne=2)
```

# Reflector 使用说明
使用 Reflector 可以非常轻松地完成对一个表的自动映射，从而快速编写 Model，没必要再做繁杂的转换和敲键盘的工作了。
使用方式非常简单，如下：

```python
from dataobj.reflector import MySQLTableReflector

print(r.reflect('app', 'AppDataObject', introduction='intro'))
```

输出结果如下：

```python
class AppDataObject(Model):
    id = IntField(auto_increment=True, max_length=11, not_null=True, primary_key=True)
    name = StrField(max_length=255)
    introduction = StrField(db_column='intro')
    icon_url = StrField(max_length=255)
    width = IntField(max_length=11)
    height = IntField(max_length=11)
    type = StrField(max_length=255)
    is_resizeable = IntField(max_length=1)
    has_toolbar = IntField(max_length=1)
    is_flash = IntField(max_length=1)
    usage_number = IntField(max_length=11)
    create_at = DatetimeField()
    category = StrField(max_length=255)
    developer = StrField(max_length=255)
    score = IntField(max_length=11)
    scoring_at = DatetimeField()
    app_url = StrField(max_length=255)
    access_level = IntField(max_length=4)

    class Meta:
        table_name = 'app'
        # 修改成实际的 DaoClass 即可
        dao_class = DaoClass
```

# 更新日志
## 2017-05-19 V2.2
1. 新增工具 `reflector` 模块，可以方便地对一个表中的字段反向映射成 Model；
2. `utils` 工具更新；
3. `sqlargs` 更新，支持 limit (m, n) 查询；
4. `sqlargs` 安全更新，为条件语句生成的 field 加盐，防止字段名与用户定义的名称重复，避免覆盖。

## 2017-05-18 V2.1
1. `validators` 中存在的一些问题修复；
2. 移除旧版 `dataobj` 存在的一些冗余字段，采用新的方式，附属信息放置于 `class Meta` 中；
3. `manager` 中一些小问题修复；


## 2017-05-17 V2.0
1. 新增模块 `model`, `fields`, `manager`, `converters`, `validators`；
2. 完善 Model 的基本操作，支持类似字典的操作；增加参数赋值前自动校验；
3. 完善 DataObjectsManager 的基本操作，支持简单的链式调用查询；
4. 修复缓存的 query 影响链式调用问题，需要保证每次链式返回时缓存的 query 都不对之前的对象有影响；
6. 提供新的接口用于过滤指定的字段，并能够返回原始的字典数据，同样支持链式调用；
7. 更新相关文档和测试代码。

## 2017-05-12 V1.1
1. `sqlargs` 包更新，添加条件对象，用于表示查询的过滤条件，支持多种条件查询的方式（eq, lt, lte, gt, gte, contains, startswith, endswith, isnull)；
1. `sqlargs` 包更新，移除 `params_factory`，目前所有的 SQL 参数组装全部委托给 `pymysql` 库处理，保证 SQL 生成的安全性；
1. `conditon` 模块修复条件语句生成失败的问题；
1. 更新 `dataobj` 包，支持更加丰富的查询条件；
1. 更新测试文件。