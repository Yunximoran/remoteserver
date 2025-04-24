import sys, json
from lib import Resolver
from lib.init.resolver import __resolver
from lib.sys import NetWork


args = sys.argv 

config = args[1]
with open(config, 'r', encoding="utf-8") as f:
    conf = json.load(f)
    print(conf)
    conf_default = conf['default']
    conf_server = conf['server']
    conf_client = conf['client']

BROADCAST = conf_default['broadcast']

CORS = conf_server['cors']
NET = NetWork(conf_server['usenet'])
DATABASE = conf_server['redis']



resolver = Resolver()

# 初始化数据库配置
def set_database():
    conf = __resolver("database", "redis")
    if "host" in DATABASE:
        conf.search("host").settext(DATABASE["host"])
    else:
        raise Exception("no host")
    if "port" in DATABASE:
        conf.search("port").settext(DATABASE["port"])
    else:
        raise Exception("no port")
        
    if DATABASE["password"]:
        conf.setattrib("password", DATABASE["password"])
    else:
        if "password" in conf.attrib:
            conf.delattrib("password")   
        
    if DATABASE["user"]:
        conf.setattrib("user", DATABASE["user"])
    else:
        if "user" in conf.attrib:
            conf.delattrib("user")
        
    if "usedb" in DATABASE:
        conf.search("db").settext(DATABASE["usedb"])
    else:
        conf.search('db').settext(0)
   
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
    with open(config, "w", encoding='utf-8') as f:
        conf['client']['ip_server'] = NET.IPv4
        json.dump(conf, f, ensure_ascii=False, indent=4)

    resolver.save()
    __resolver.save()

def init():
    set_server()
    set_network()
    set_database()
    close() 

if __name__ == "__main__":
    init()
    
    


