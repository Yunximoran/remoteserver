from urllib.parse import quote, unquote
import base64

name = "ranxi"
utf_name=quote(name, encoding="gbk")
print(utf_name)

bn = base64.b64encode(name.encode())
print(bn)
print(name.encode())
print(list(map(ord, name)))