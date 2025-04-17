# 匹配URL地址
NET_HTTP = r"^https?://"

# 匹配IP地址
NET_IP = r"^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"

# 匹配mac地址
NET_MAC = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"


if __name__ == "__main__":
    import re
    print(re.match(NET_IP, "192.168.31.176"))