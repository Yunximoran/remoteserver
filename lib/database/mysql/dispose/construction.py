from ..basic._variable import SHOW, DROP, CREATE, INSERT, UPDATE, DELETE, SELECT
from pymysql import err
import copy


class BASIC:
    # 构筑SQL语句
    # 通用操作
    @staticmethod
    def drop(ObjName, isDB=True, isExists=False):
        """
            构造DROP语句
        :param ObjName: 对象名
        :param isDB: 是否为数据库
        :param isExists: 对象是否已存在
        :return:
        """
        drop = copy.deepcopy(DROP)
        if isDB:
            drop += " database"
        else:
            drop += " table"
        if isExists:
            drop += " if exists"
        return drop + " " + ObjName

    @staticmethod
    def show(isDB=True):
        """
            构造SHOW语句
        :param isDB: 是否为数据库
        :return:
        """
        show = copy.deepcopy(SHOW)
        if isDB:
            return show + " " + "databases"
        else:
            return show + " " + "tables"



class DBC:
    # 库操作
    @staticmethod
    def ndb(dbn, isExists=False):
        """
            创建数据库
        :param dbn: 数据库名
        :param isExists: 数据库是否已存在
        :return:
        """
        create = copy.deepcopy(CREATE)
        create[0] += " database"
        if isExists:
            create[0] += " if not exists"

        create = create[:1]
        create.append(dbn)

        return " ".join(create)

    @staticmethod
    def use(dbn):
        return f"use {dbn}"


class TBC:
    # 表操作
    @staticmethod
    def create(tbn, targets, primary=None, unique=None):
        """
            构造CREATE语句
            创建表
        :param unique:  指定唯一键
        :param primary: 指定主键
        :param tbn:    表名
        :type  tbn:    str
        :param targets: 列
        :type  targets: dict[str, str]
        :return:
        """
        columns = []

        for tag in targets.keys():
            columns.append(tag + " " + targets[tag])

        if primary is not None:
            if primary not in targets.keys():
                raise "primary must is targets key"
            else:
                columns.append(f"primary key({primary})")

        if unique is not None:
            if unique not in targets.keys():
                raise "unique must is targets key"
            else:
                columns.append(f"unique ({unique})")

        create = copy.deepcopy(CREATE)
        create[0] += " table if not exists"
        create.insert(1, tbn)
        create.insert(-1, ','.join(columns))
        return " ".join(create)

    @staticmethod
    def select(tbn, fondKey="*", condition=None):
        """
            构造SELECT语句
        :param tbn: 表名
        :param fondKey: 指定查找键
        :param condition: 设置条件
        :return: SELECT SQL
        """

        select = copy.deepcopy(SELECT)
        select.append(tbn)
        if isinstance(fondKey, tuple):
            keys = [key for key in fondKey]
            fondKey = " ".join(keys)
        elif not isinstance(fondKey, str):
            # 如果fondKey 不合法要怎么办， 对于不合法的SQL应该在哪里进行异常处理
            pass
        select.insert(1, fondKey)
        if condition:
            return " ".join(select) + " where " + condition
        return " ".join(select)

    @staticmethod
    def insert(tbn, vals, keys=None, ignore=False):
        """
            构造INSERT语句
        :param tbn: 表名
        :param vals: 需要插入的数据
        :param keys: 是否为键值插入
        :param ignore: 是否忽略重复数据
        :return: INSERT SQL
        """
        insert = copy.deepcopy(INSERT)
        insert.append(tbn)
        if ignore:
            insert.insert(1, "ignore")
        # 数据格式增多后可能无法使用推导式构造sql语句，因为对于特殊的数据类型需要使用特殊格式格式化
        value_format = "values(" + ", ".join([f"'{val}'" if isinstance(val, str) else f"{val}" for val in vals]) + ")"
        if keys:
            key_format = "(" + ", ".join(key for key in keys) + ")"
            insert.append(key_format + value_format)
        else:
            insert.append(value_format)
        return " ".join(insert)

    @staticmethod
    def update(tbn, vals, keys, condition):
        """
            构造UPDATE语句
        :param tbn: 表名
        :param vals: 更新数据
        :param keys: 更新条目索引
        :param condition: 设置更新条件
        :return: UPDATE SQL
        """
        update = copy.deepcopy(UPDATE)
        replace = []
        for key, val in zip(keys, vals):
            if isinstance(val, str):
                val = f"'{val}'"
            replace.append(f"{key} = {val}")
        update[1] += " " + ", ".join(replace)

        update.insert(1, tbn)
        update.append(condition)
        return " ".join(update)

    @staticmethod
    def delete(tbn, condition):
        """
            构造DELETE语句
        :param tbn: 表名
        :param condition: 指定条件
        :return: DELETE SQL
        """
        delete = copy.deepcopy(DELETE)
        delete.append(tbn)
        delete.append("where " + condition)
        return " ".join(delete)


class Construction(BASIC, DBC, TBC):
    # 构筑SQL语句
    pass
