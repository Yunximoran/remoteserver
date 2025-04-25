
try:
    from .basic.connector import Connector
    from .basic.information import Information
    from .dispose.construction import Construction
    from .dispose.formation import FormatPackage
    from .dispose.check import Check
    from ...catch import _CatchDataBase
    
except ImportError:
    from lib.database.mysql.basic.connector import Connector
    from lib.database.mysql.basic.information import Information
    from lib.database.mysql.dispose.construction import Construction
    from lib.database.mysql.dispose.formation import FormatPackage
    from lib.database.mysql.dispose.check import Check
    
    from lib.catch import _CatchDataBase

catch = _CatchDataBase()

class WorkBench(Connector):
    # 是否需要将代码更加基础化
    construction = Construction()
    formattool = FormatPackage()
    check = Check()
    info = Information()

    def init(self, db=None):
        # 重新选择数据库，并初始化
        self.__init__(db)

    def __init__(self, usedb=None):
        self.__db = usedb
        super().__init__(self.__db)

    def drop(self, db):
        # 删除数据库
        self.__execute(self.construction.drop(db))

    def use(self, db):
        # 选择使用的数据库
        self.__db = db
        conn = self.getconn()
        conn.select_db(db)

    def show(self, isDB=True):
        # 枚举当前数据库，或者所有数据
        if self.__db is None and not isDB:
            raise "no database selected"
        self.__execute(self.construction.show(isDB=isDB))
        return self.__getdata()

    def cdb(self, dbn, isExists=False):
        # 创建新的数据库
        self.__execute(self.construction.ndb(dbn, isExists=isExists))

    def ctb(self, tbn, targets, primary=None, unique=None):
        """
            创建新的数据表
        :param tbn: 表名
        :param targets: 字段
        :param primary: 设置主键
        :param unique: 设置唯一键
        """
        self.__execute(self.construction.create(tbn, targets, primary, unique))

    def insert(self, tbn, data, ignore=False):
        """
            执行插入操作
        :param tbn: 表名
        :param data: 需要插入的数据
        :param ignore: 是否忽略重复值
        :return:
        """
        # 如果vals返回空则说明插入单条数据或数据格式错误
        if isinstance(data, dict):  # 根据数据类型，执行对应的格式化操作
            # 格式化字典数据
            vals, keys = self.formattool.formatDict(data)
        else:
            # 格式化矩阵数据
            vals, keys = self.formattool.formatSeries(data)

        if vals:  # 格式化方法返回，vals,keys两个变量
            for val in vals:
                self.__execute(self.construction.insert(tbn, val, keys, ignore=ignore))
        else:  # 如果vals为空，说明数据存在错误
            raise 'DataError'
            # try:
            #     vals = tuple(data.values())
            #     self.__execute(self.SQL.insert(tbn, vals, keys, ignore=ignore))
            # except AttributeError:
            #     vals = tuple(data)
            #     self.__execute(self.SQL.insert(tbn, vals, keys, ignore=ignore))

    def update(self, tbn,
               newData=None,
               **kwargs):
        """
            更新数据
        :param tbn: 表名
        :param newData:
        :param kwargs:
        :return:
        """
        # update 方法应该可以参考insert方法，更新单条数据或者多条数据， 对于update 指定键 和 指定条件 是必须的
        # 要不要做多样化输入数据
        # 指定条件是必须得， 但不是手动输入条件， 给定一条数据， 通过其中某键为索引定位数据更新
        # update方法将以什么形式更新
        # 更新需要换新的整条数据
        # 除了字典也可以是可便利对象，单条数据插入，多数据插入
        # 分开执行，单次更新：字典、元组。 多次更新：字典、元组
        # 尝试参考insert参数，但是update必须有keys索引来构建condition
        if (newData and kwargs) or (not newData and not kwargs):
            return

        if newData:
            vals, keys = self.formattool.formatDict(newData)
        else:
            vals, _ = self.formattool.formatSeries(kwargs['vals'])
            keys = tuple(kwargs['keys'])
        isOnce = self.check.checkInsertOnce(vals)  # 判断是否为单次更新
        if isOnce:
            condition = self.__updateGetCondition(tbn, vals, keys)
            self.__execute(self.construction.update(tbn, vals, keys, condition=condition))
        else:
            for val in vals:
                condition = self.__updateGetCondition(tbn, val, keys)
                self.__execute(self.construction.update(tbn, val, keys, condition=condition))

    def __updateGetCondition(self, tbn, vals, keys):
        # 年少不知元组好
        for key in keys:
            if self.check.is_primary(self.__db, tbn, key):
                pri = key
                index = keys.index(key)
                return f"{pri} = {vals[index]}"
            if self.check.is_unique(self.__db, tbn, key):
                uni = key
                index = keys.index(key)
                return f"{uni} = {vals[index]}"
        return f"{keys[0]} = {vals[0]}"

    def delete(self, tbn, **condition):
        keys = condition.keys()
        vals = condition.values()
        for key, val in zip(keys, vals):
            self.__execute(self.construction.delete(tbn, f"{key} = {val}"))


    def select(self, tbn, findKey="*", condition=None):
        self.__execute(self.construction.select(tbn, findKey, condition))
        return self.__getdata()

    def alter(self, tbn,
              rename=None,
              column=None,
              primary=None,
              unique=None):
        pass

    @catch.mysql
    def __execute(self, SQL):
        self.getcursor().execute(SQL)


    def __rollback(self):
        self.getconn().rollback()

    def __getdata(self):
        results = self.getcursor().fetchall()
        return tuple([row if len(row) > 1 else row[0] for row in results])


    def using(self):
        return self.__db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


"""
`ALTER` 是 MySQL 中用于修改数据库对象（如表、列、索引等）的命令。以下是 `ALTER` 的一些常见用法：

1. 修改表名：

```
ALTER TABLE old_table_name RENAME TO new_table_name;
```

2. 修改表的字符集：

```
ALTER TABLE table_name CONVERT TO CHARACTER SET utf8mb4;
```

3. 修改表的存储引擎：

```
ALTER TABLE table_name ENGINE = InnoDB;
```

4. 添加列：

```
ALTER TABLE table_name ADD COLUMN column_name column_definition;
```

5. 修改列：

```
ALTER TABLE table_name MODIFY COLUMN column_name new_column_definition;
```

6. 重命名列：

```
ALTER TABLE table_name CHANGE COLUMN old_column_name new_column_name new_column_definition;
```

7. 删除列：

```
ALTER TABLE table_name DROP COLUMN column_name;
```

8. 添加主键：

```
ALTER TABLE table_name ADD PRIMARY KEY (column_name);
```

9. 删除主键：

```
ALTER TABLE table_name DROP PRIMARY KEY;
```

10. 添加外键：

```
ALTER TABLE table_name ADD CONSTRAINT constraint_name FOREIGN KEY (column_name) REFERENCES another_table(another_column)
```
"alter table test_db add constraint constraint_name foreign key(id) references another_table()"

11. 删除外键：

```
ALTER TABLE table_name DROP FOREIGN KEY constraint_name;
```

12. 添加索引：

```
ALTER TABLE table_name ADD INDEX index_name (column_name);
```

13. 删除索引：

```
ALTER TABLE table_name DROP INDEX index_name;
```

注意：在使用 `ALTER` 命令时，需要具有对数据库对象足够的权限。


"""
