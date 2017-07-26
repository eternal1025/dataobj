关于 dataobj 包
----------------------
![travis_status](https://travis-ci.org/0xE8551CCB/dataobj.svg?branch=master)

[dataobj](https://github.com/0xE8551CCB/dataobj) 是一个简易、轻量的 ORM 工具包，提供简单易用的接口，方便执行增删改查等常见的操作。

# 功能
1. 提供了 `Model` 和 `Field` 对象，对数据层包装并数据的合法性校验；
1. 提供了一些灵活的连接器配置方法；
1. 可以轻松地接入到任何 Python 项目中；
1. 查询支持简单的链式调用方法，返回结果为一个可迭代对象，采用懒加载模式生成查询结果。

# 结构说明
1. `manager`：实现数据库相关的查询、更新、删除、插入等操作；
2. `model`：一个数据层对象的抽象；
3. `fields`：提供了用于映射的字段类型，提供字段校验等机制；
4. `converters`：一些常用的类型转换工具；
5. `reflector`：用于自动映射数据库表到 Model 的工具；
6. `utils`：常用的工具函数；
7. `exceptions`：异常集合；
8. `validators`：集成了一些公共的字段检验插件。

# 使用说明

## 定义 Model

定义 Model 的方式比较简单，继承自 `dataobj.Model` 并添加一系列字段即可：

```python
import datetime
from dataobj import Model, IntField, StrField, DatetimeField
    
class User(Model):
    # 每个 Model 和数据库表关联，必须要指定一个唯一的 field 作为主键
    id = IntField(primary_key=True)
    name = StrField(not_null=True)
    age = IntField()
    # 当然也设定默认值
    email = StrField(default='example@hostname')
    # 可以给字段加别名，db_column 就是在数据库中的名称
    address = StrField(db_column='addr')
    # 默认值也可以是一个 callable 对象
    register_at = DatetimeField(default=datetime.datetime.now)
        
    class Meta:
        # 在此指定关联的表名，如果没有指定，则默认为 `User` 类名
        table_name = 'user'
        # 此处指定数据库连接器配置，关于该配置，参见后面一节的说明
        connection = 'some_connection'
    
```

## 配置数据库连接

数据库连接器配置提供了若干种方法，但总体依赖底层数据库工具包：[dbutil]()，使用前必须安装该工具包。关于数据库连接配置，可以像上面那样在定义 Model 时在 Meta 中添加连接配置，
也可以在执行具体操作时，如 `User.objects.get(id=1, conn=new_connection)`，传入连接对象。关于连接对象 `connection` 可以是如下几种之一：
1. 一个字典格式的配置，示例如下：

    ```python
    db_config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': 3306,
        'database': 'db_name'
    }
    
    # 使用时传递给 connection 即可，示例如下
    class Meta:
        connection = db_config
    ```

1. URL 格式的连接配置，示例如下：

    ```python
    db_config = 'mysql://username:password@host:port/db_name?charset=utf8'
    ```

1. 可以是一个实现了 `dbutil.connections.base.IDatabaseConnection` 部分接口的连接器对象实例 (instance)，具体要求如下：
    1. 该连接器对象至少实现了类似 `execute(self, table, **kwargs)` 接口，并且在内部完成 SQL 组建，返回结果为一个元组：`(affected_rows, lastrowid)`；
    1. 该连接器对象至少实现了类似 `query(self, table, **kwargs)` 接口，返回结果为一个可迭代对象，每个元素是表中的每一行的数据，并且以字典格式呈现；
    1. 可选择性实现 `open(self)` 方法，如果实现了，则会在开始执行 SQL 前被调用；
    1. 可选择性实现 `close(self)` 方法，如果实现，则会在结束执行 SQL 后被调用。

## 数据库操作

1. 新增

    ```python
    usr = User(name="Chris", age=20, address="Beijing")
    user.dump()
    
    # 或者使用新的连接对象，下面各种方法与此类似，不再赘述
    # user.dump(new_connection)
    ```

1. 查询：各种查询条件支持都由 [dbutil.sqlargs]() 工具包具体实现：

    ```python
    # 按照指定条件查询得到一个对象
    user = User.objects.get(id=1)
    user = User.objects.get(age=30)
    
    # 得到所有对象
    for user in User.objects.all():
        print(user)
        
    # 得到过滤后的结果
    # 条件：< 和 <=
    users = User.objects.filter(id__lt=10)
    users = User.objects.filter(id__lte=10)
    
    # 条件：> 和 >=
    users = User.objects.filter(id__gt=10)
    users = User.objects.filter(id__gte=10)
    
    # 条件：!=
    users = User.objects.filter(id__ne=10)
    
    # 条件：LIKE
    users = User.objects.filter(name__contains='Chris')
    users = User.objects.filter(name__startswith="Chris")
    users = User.objects.filter(name__endswith="Chris")
    
    # 条件：IS NULL 和 IS NOT NULL
    users = User.objects.filter(name__isnull=True)
    users = User.objects.filter(name__isnull=False)
    
    # 查询条件可以组合，如下：
    users = User.objects.filter(id__gt=10, name__isnull=False)
    
    # 链式调用查询
    # order by
    users = User.objects.all().order_by('name', descending=False)
    
    # limit
    users = User.objects.all().limit(10, offset=10)
    
    # first
    user = User.objects.all().first()
    
    # last
    user = User.objects.all().last()
    
    # 组合链式查询
    users = User.objects.all().order_by('id', descending=True).limit(10)
 
    # 切片，所有的查询结果都支持切片
    for user in User.objects.filter(name__isnull=False)[:10]:
       print(user)
    ```

1. 更新

    ```python
    user = User.objects.get(id=1)
    # 一种方式，直接传入更新的字段
    user.update(name='new name')
    
    # 另一种方式，对属性更新完在调用 update
    user.name = 'new name'
    user.update()
    ```
    
1. 删除

    ```python
    # 删除最后一条记录
    user = User.objects.all().order_by('id', descending=True).limit(1).first()
    user.delete()
    ```

# License

[dataobj](https://github.com/0xE8551CCB/dataobj) is under the MIT license.