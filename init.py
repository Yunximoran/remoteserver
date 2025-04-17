from lib import Resolver
from lib.init.resolver import __resolver
from lib.sys import NetWork


# 网络配置选项
NET = NetWork("WLAN")           # 指定服务端网卡
BROADCAST = "192.168.31.255"    # 广播域

# 服务器配置选项
CORS = [    # 跨域资源
    "https://127.0.0.1:8080",
    "http://127.0.0.1:8080"
]

# 数据库配置选项
DATABASE = {
    "redis": {
        "host": "localhost",
        "port": 6379,
        # "password": "123456", # 设置redis密码， 如果没有设置密码则
        "usedb": 0
    },
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "ranxi",
        "usedb": "test"
    }
}


resolver = Resolver()

# 初始化数据库配置
def set_database():
    for database in DATABASE:
        data = DATABASE[database]
        conf = __resolver("database", database)
        if "host" in data:
            conf.search("host").settext(data["host"])
        if "port" in data:
            conf.search("port").settext(data["port"])
            
        if "password" in data:
            conf.setattrib("password", data["password"])
            
        if "user" in data:
            conf.setattrib("user", data["user"])
            
        if "usedb" in data:
            conf.search("db").settext(data["usedb"])
   
# 初始化网络配置
def set_network():
    net = resolver("network")  
    sock = resolver("sock") 
    ip = net.search("ip")
    mac = net.search("mac")
    
    if not ip:
        net.addelement("ip", text=NET.IPv4)
    else:
        ip.settext(NET.IPv4)
        
    if not mac:
        net.addelement("mac", text=NET.mac)
    else:
        mac.settext(NET.mac)
        
    # 设置广播域
    sock.search("ip-broad").settext(BROADCAST)

# 初始化服务器配置
def set_server():
    server = resolver("server")
    cors = server.search('cors')
    if cors:
        for item in CORS:
            try:
                cors.push(item)
            except Exception:
                continue
            
# 保存更改
def close():
    resolver.save()
    __resolver.save()

def init():
    set_server()
    set_network()
    set_database()
    close() 

if __name__ == "__main__":
    init()
    
    


