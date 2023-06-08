# Pkgmgr
包管理

### 用法:
先运行startserver.bat:
```shell
python ./pkgm.py install test
python ./pkgm.py list
test
python ./pkgm.py uninstall test
```
命令行输入test检测是否安装成功

指定版本,服务器:
```shell
python ./pkgm.py install test --version 1.0a --i http://114514.com
python ./pkgm.py install list
python ./pkgm.py uninstall test --version 1.0a --i http://114514.com
```
