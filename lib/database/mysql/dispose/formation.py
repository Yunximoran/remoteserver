from .check import Check


class FormatPackage:
    def __init__(self):
        self.check = Check()

    # 代码bug，管不管？
    def formatDict(self, data:dict):
        keys = tuple(data.keys())
        vals = tuple(data.values())
        # 校验数据长度是否一致，获取更新次数
        check = self.check.checkLen(vals) 

        # 如果只有一条数据，vals是一维数组，无法被二次遍历
        if check:
            if check == vals:
                return (vals, ), keys
            vals = tuple(self.__formatDict(vals))
        else:
            vals = None
        return vals, keys

    def formatSeries(self, data):
        vals = tuple(data)
        check = self.check.checkLen(vals)
        if check:
            if check == vals:
                return (vals, ), None
            vals = tuple(self.__formatSeries(vals))
        else:
            vals = None
        return vals, None

    @staticmethod
    def __formatSeries(data):
        for val in data:
            yield tuple(val)

    @staticmethod
    def __formatDict(items):
        iters = len(items[0])  # 获取行数
        for i in range(iters):
            yield tuple([item[i] for item in items])
