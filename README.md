# 说明
`dataobj` 是一个简易、轻量的 ORM 工具包，提供简单易用的接口，方便执行增删改查等常见的操作。

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


# Reflector 使用说明
使用 Reflector 可以非常轻松地完成对一个表的自动映射，从而快速编写 Model，没必要再做繁杂的转换和敲键盘的工作了。
使用方式非常简单，如下：

    ```python
    from dataobj.reflector import MySQLTableReflector
    
    print(r.reflect('app', 'AppDataObject', introduction='intro'))
   
    # 得到下面的输出：
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
    ```

# 更新日志
## 2017-06-22
1. 更新测试文件和文档。

## 2017-06-21
1. 进行初步重构，主要将数据库配置相关的依赖改为可由外部传入。

## 2017-05-26 
1. 重要更新，在参数验证时添加 `try-except` 语句，并将错误详情 log 输出，便于调试。

## 2017-05-25 V2.3
1. 重要更新，修复 where 条件子句 `isnull` 失败的问题；
2. 改进 `manager` 模块，将在更新时，自动更新值变化的字段，以增加 SQL 执行的速度，改善性能。

## 2017-05-22
1. 修复 Model 初始化时 0 变为 None 的问题；

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