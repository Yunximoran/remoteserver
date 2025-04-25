import psutil
import struct
import platform
import time

net_if_addrs = psutil.net_if_addrs()
net_if_stats = psutil.net_if_stats()

# linux 和 window 获取 mac 的方法不一样
if platform.system() == "Windows":
    link = "AF_LINK"
elif platform.system() == "Linux":
    link = "AF_PACKET"


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
        
    @staticmethod
    def checkallnet():
        results = {}
        for interface_name, interface_addresses in net_if_addrs.items():
            net = {}
            for address in interface_addresses:
                if address.family.name.startswith('AF_INET6'):
                    net["IPv6"] = address.address
                elif address.family.name.startswith('AF_INET'):
                    net["IPv4"] = address.address
                elif address.family.name.startswith(link):
                    net["mac"] = address.address
            results[interface_name] = net
        return results
    
    @staticmethod
    def decimalcidrblock(ipv4:str):
        if ipv4 == "localhost":
            ipv4 = "127.0.0.1"
        decimal = 0
        blocks = [int(block) for block in ipv4.split(".") if int(block) <= 255 and int(block) >= 0]
        if len(blocks) != 4:
            raise Exception(f"Inviad IP {ipv4}")
        
        for i, block in enumerate(blocks[::-1]):
            decimal += block * (255 ** i)
        return decimal
    
    def cidrblock(decimal):
        """
        :0.0.0.0    : 0
        :127.0.0.1  : 2105834626
        A: 165813750 : 182460405 <--> 10.0.0.0 : 10.255.255.255
        B: 2853036900 : 2854077555 <--> 172.16.0.0 : 176.31.255.255
        C: 3194548200 : 3194613480 <--> 198.168.0.0 : 192.168.255.255
        """
        if decimal == 0 or decimal == 2105834626: pass
        elif decimal <= 182460405 and decimal >= 165813750: pass
        elif decimal <= 2854077555 and decimal >= 2853036900: pass
        elif decimal <= 3194613480 and decimal >= 3194548200: pass
        else:
            raise Exception("Inviad Net")
        blocks = ["0"] * 4
        index = 3
        while decimal > 0:
            blocks[index] = str(decimal % 255)
            decimal //= 255
            index -= 1

        return ".".join(blocks)
    
    

    
class NetWork(_NetWorkTools):

    def __init__(self, bind=None):
        # 绑定网卡
        """
            获取本地所有网卡配置
        """
        if bind not in net_if_addrs:
            raise Exception(f"not found net: {bind}")
        self.name = bind
        for info in net_if_addrs[bind]:
            if info.family.name.startswith("AF_INET6"): self.IPv6 = info.address
            elif info.family.name.startswith("AF_INET"):
                self.IPv4 = info.address
                self.netmask = info.netmask
            elif info.family.name.startswith(link): self.mac = info.address
        stat = net_if_stats[bind]
        if stat.isup:
            self.speed = net_if_stats[bind].speed
            self.mtu = net_if_stats[bind].mtu


if __name__ == "__main__":
    L = NetWork.decimalcidrblock("127.0.0.1")
    print(L)