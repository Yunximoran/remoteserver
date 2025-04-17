import psutil
import struct
import platform
import time


class _NetWorkTools:
    @staticmethod
    def check_speed(interface, interval=1):
        # 获取初始网络统计信息
        stats_before = psutil.net_io_counters(pernic=True).get(interface)
        bytes_before = stats_before.bytes_sent + stats_before.bytes_recv
        
        # 等待一段时间
        time.sleep(interval)
        
        # 获取新的统计信息
        stats_after = psutil.net_io_counters(pernic=True).get(interface)
        bytes_after = stats_after.bytes_sent + stats_after.bytes_recv
        
        # 计算速率（字节/秒 → Mbps）
        bytes_per_sec = (bytes_after - bytes_before) / interval
        mbps = bytes_per_sec * 8 / (1024 ** 2)  # 1 byte = 8 bits, 1 Mbps = 1024^2 bits/s
        return round(mbps, 3)
    
    @staticmethod
    def create_magic_packet(mac) -> bytes:
        """
            通过mac创建唤醒魔术包
        """
        mac = _NetWorkTools.formatmac(mac)
        data = b"FF" * 6 + (mac * 16).encode()
        res = b""
        for i in range(0, len(data), 2):
            res =  res + struct.pack("B", int(data[i: i+2], 16))
        return res
    
    @staticmethod
    def formatmac(mac: str) -> str:
        if len(mac) == 12:
            return mac
        elif len(mac) ==17:
            if mac.count(":") == 5 or mac.count("-") == 5:
                sep = mac[2]
                mac = mac.replace(sep, '')
                return mac
            else:
                raise ValueError("incorrect mac format")
        else:
            raise ValueError("incorrect mac format")
    
class NetWork(_NetWorkTools):
    def __init__(self, bind):
        # 绑定网卡
        self.__all_local_network = self.__checknet()

        self.name = bind
        self.net = self.__all_local_network[bind]
        self.mac = self.net['mac']
        self.IPv4 = self.net["IPv4"]
        self.IPv6 = self.net["IPv6"]
        
        self.info = {
            bind: self.net
        }
    
    def __checknet(self) -> dict:
        """
            获取本地所有网卡配置
        """
        net_if_addrs = psutil.net_if_addrs()
        result = {}

        # linux 和 window 获取 mac 的方法不一样
        if platform.system() == "Windows":
            link = "AF_LINK"
        elif platform.system() == "Linux":
            link = "AF_PACKET"

        for interface_name, interface_addresses in net_if_addrs.items():
            net = {}
            for address in interface_addresses:
                if address.family.name.startswith('AF_INET6'):
                    net["IPv6"] = address.address
                elif address.family.name.startswith('AF_INET'):
                    net["IPv4"] = address.address
                elif address.family.name.startswith(link):
                    net["mac"] = address.address
            result[interface_name] = net
        return result
    

def choosenet(choose: str = None) -> dict:
    """
    choose: 指定工作网卡，None时返回所有网卡参数
    return: 返回网卡数据字典，key为网卡名称，value为包含IPv4/IPv6/MAC地址的字典
    """
    net_if_addrs = psutil.net_if_addrs()
    result = {}

    for interface_name, interface_addresses in net_if_addrs.items():
        if choose is None or choose == interface_name:
            net = {}
            for address in interface_addresses:
                if address.family.name.startswith('AF_INET6'):
                    net["IPv6"] = address.address
                elif address.family.name.startswith('AF_INET'):
                    net["IPv4"] = address.address
                elif address.family.name == 'AF_LINK':
                    net["mac"] = address.address
            result[interface_name] = net
            if choose is not None:  # 如果指定了网卡，直接返回
                return result[interface_name]
    
    return result

def formatmac(mac: str) -> str:
    # 格式化MAC地址，支持12位和17位格式
    if len(mac) == 12:
        pass
    if len(mac) == 17:
        if mac.count(":") == 5 or mac.count("-") == 5:
            sep = mac[2]
            mac = mac.replace(sep, '')
        else:
            raise ValueError("incorrect MAC format")
    else:
        raise ValueError("incorrect MAC format")
    
    return mac   

def create_magic_packet(mac) -> bytes:
    mac = formatmac(mac)
    data = b'FF' * 6 + (mac * 16).encode()
    send_data = b""
    for i in range(0, len(data), 2):
        send_data = send_data + struct.pack("B", int(data[i: i + 2], 16))
    return send_data


if __name__ == "__main__":
    net = NetWork("WLAN")
    print(net.create_magic_packet(net.mac))