from ..basic.information import Information


class Check:
    info = Information()

    @staticmethod
    def checkLen(items):
        # 字典中可以获取到行数，数组中可以获取到列数
        # print(items)
        # 检查预处理
        iNum = None
        for item in items:
            if not isinstance(item, (list, tuple)) and iNum is None:
                # 验证单次插入，iNum必须在初始化状态下进行
                return items
            lens = len(item)
            if iNum is None:
                iNum = lens
            else:
                if iNum != lens:
                    return False
                else:
                    iNum = lens
        return True

    @staticmethod
    def checkInsertOnce(items):
        # 检查是否是单条数据插入
        # [t1, t2, t3] | [[],[],[]]
        # 这里只能校验格式化后的数据格式化后的数据
        for item in items:
            # 变量容器
            if isinstance(item, (list, tuple)):
                return False
        return True

    def checkUniformity(self, vals):
        # 校验数据是否一致
        # 单条数据不需要检查
        checkDataType = []
        if self.checkInsertOnce(vals):
            return True
        for items in vals:
            if not checkDataType:
                for item in items:
                    checkDataType.append(type(item))
                continue
            for i in range(len(checkDataType)):
                if not isinstance(items[i], checkDataType[i]):
                    return False
        return True

    def checkKeyValNumEquality(self, db, tb, itemNum):
        # 检验键值是否对应
        # 也是只能校验格式化后的数据
        _, keyNum = self.info.get_fetchs(db, tb)
        print(keyNum)
        return True if keyNum == itemNum else False

    def is_primary(self, db, tb, keyName):
        # 检查是否是主键
        res = self.info.primary(db, tb)
        if keyName in res:
            return True
        else:
            return False

    def is_unique(self, db, tb, keyName):
        # 检查是否是联合键
        res = self.info.unique(db, tb)
        if keyName in res:
            return True
        else:
            return False

