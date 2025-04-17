# 远程控制系统服务端部署说明

## 项目依赖
- anaconda3  
- python3.11.10  
- redis  

## 下载项目
```bash
git clone https://github.com/Yunximoran/remotecontrolsystem.git
```

## 运行前准备
### 安装anaconda3
[https://www.anaconda.com/download/success](https://www.anaconda.com/download/success)

#### Linux:
```bash
bash /path/to/anaconda3-xxxxx-Linux-x86_64.sh
sudo vim ~/.bashrc  # 最后一行输入: export PATH:/path/to/anaconda3:$PATH
source ~/.bashrc
```

#### Windows:
运行 `/path/to/anaconda3-xxxxx-Windows-x86_64.exe`

### 创建虚拟环境
```bash
conda create --n remotecontrol python=3.11.10
```

## 修改Init.py文件
### 网络配置选项
```python
NET = NetWork("WLAN")  # 指定服务端网卡
BROADCAST = "192.168.31.255"  # 广播域
```

### 服务器配置选项
```python
CORS = [ 
    "https://127.0.0.1:8080",
    "http://127.0.0.1:8080"
]
```

### 数据库配置选项
```python
DATABASE = {
    "redis": {
        "host": "localhost",
        "port": 6379,
        # "password": "123456",  # 设置redis密码，如果没有设置密码则注释
        "usedb": 0
    },
    "mysql": {    # 设置mysql，可忽略
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "ranxi",
        "usedb": "test"
    }
}
```


***



## 初始化项目
### 激活虚拟环境
```bash
conda activate remotecontrol
conda install -r requirements.txt
```

### 终端运行
```bash
python init.py  # 初次部署时运行
python start.py
```
