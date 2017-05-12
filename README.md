# 说明
`dataobj` 是一个简易的仿 ORM 的 Python 包，仅支持有限的 SQL 操作子集。详细的使用测试参见 `tests` 目录下的代码。

# 调用过程
1. 上层应用数据层对象 `XDataObject`；
2. `dataobj` 进行字段类型检查、表字段名映射等；
3. 调用 `sqlargs` 包生成定制的 SQL 模板及相应参数；
4. 调用 `some_db_dao` 对象提供的数据库操作方法（要求实现 `execute(sql, args)`, `query(sql, args)` 接口）完成数据库操作。

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
from dataobj import DataObject, IntField, StrField, DatetimeField

class FolderDataObject(DataObject):
    __table__ = 'folder'
    __dao_class__ = TestDao

    folder_id = IntField(db_column='id', primary_key=True)
    name = StrField(default='新建文件夹')
    icon_url = StrField(default='default.png')
    create_at = DatetimeField(default=datetime.datetime.now)
```

1. 接下来进行基本的 CRUD 操作
```python
# 创建对象并写入数据库
folder = FolderDataObject(name='测试文件夹', icon_url='test.png')
folder.dump()

# 读取操作
# 加载指定 ID 的对象
folder = FolderDataObject.load(folder_id=100)

# 过滤操作
folders = FolderDataObject.filter(folder_id=100)

# 获取所有的对象
folders = FolderDataObject.all()

# 更新操作
folder = FolderDataObject.load(folder_id=100)
folder.update(name='更新文件夹')

# 删除操作
folder.delete()
```

1. 更加丰富的过滤操作示例
```python
# 查找指定名称的文件夹
f = FolderDataObject.filter(name='某某文件夹')
f = FolderDataObject.filter(name__eq='某某文件夹')

# 查找包含字符串的文件夹
f = FolderDataObject.filter(name__contains='娱乐')
f = FolderDataObject.filter(name__startswith='测试')
f = FolderDataObject.filter(name__endswith='影视')

# 查找图标为 NULL 的文件夹
f = FolderDataObject.filter(icon_url__isnull=True)

# 查找图标不为 NULL 的文件夹
f = FolderDataObject.filter(icon_url__isnull=False)

# 查找 id 大于或大于等于某个值的文件夹
f = FolderDataObject.filter(folder_id__gt=2)
f = FolderDataObject.filter(folder_id__gte=2)

# 查找 id 小于或小于等于某个值的文件夹
f = FolderDataObject.filter(folder_id__le=2)
f = FolderDataObject.filter(folder_id__lte=2)

# 查找 id 不等于某个值的文件夹
f = FolderDataObject.filter(folder_id__ne=2)
```

# 更新日志
## 2017-05-12 V1.1
1. `sqlargs` 包更新，添加条件对象，用于表示查询的过滤条件，支持多种条件查询的方式（eq, lt, lte, gt, gte, contains, startswith, endswith, isnull)；
1. `sqlargs` 包更新，移除 `params_factory`，目前所有的 SQL 参数组装全部委托给 `pymysql` 库处理，保证 SQL 生成的安全性；
1. `conditon` 模块修复条件语句生成失败的问题；
1. 更新 `dataobj` 包，支持更加丰富的查询条件；
1. 更新测试文件。