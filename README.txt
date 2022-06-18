安装依赖
pip install -r requirements.txt

确保安装了Chrome浏览器，右键其快捷方式打开文件所在位置，所示第一个文件夹名即为您所安装的Chrome版本
打开下方链接，找到您安装的Chrome对应版本的内核，下载后解压，将chromedriver.exe放到bot/plugins/daily_health/lib文件夹下
http://chromedriver.storage.googleapis.com/index.html

下载go-cqhttp最新release，对应您服务器所在平台，解压后放到bot文件夹下，双击运行
https://github.com/Mrs4s/go-cqhttp
首次配置时选择反向 Websocket 通信，在配置文件config.yml中填写用作bot的qq号和密码，并修改反向通信服务器为本地服务器
account: # 账号相关
  uin: 1145141919810 # QQ账号
  password: '这是字符串' # 密码为空时使用扫码登录
servers:
  - ws-reverse:
      universal: ws://127.0.0.1:8080/ws/
之后保证在运行bot前先运行go-cqhttp

安装anaconda或miniconda，编辑run.bat内容第一行为其activate.bat所在路径和其所在路径
双击run.bat运行bot