安装依赖
pip install -r requirements.txt

确保安装了Chrome浏览器，右键其快捷方式打开文件所在位置，所示第一个文件夹名即为您所安装的Chrome版本
打开下方链接，找到您安装的Chrome对应版本的内核，下载后解压，将chromedriver.exe放到lib文件夹下
http://chromedriver.storage.googleapis.com/index.html

修改配置：将config_sample.json重命名为config.json
{
  "userId": "你的学号",
  "password": "你的密码",
  "form_content": {
    每一个键值对应网页端填报的一个键值，如下，default为是否有默认值，option为要选的str，多选为list
    若程序运行抛出异常，请先检查网页端填报内容是否有变动，并根据变动修改配置
    "今日所在省份": {"default": "False", "option": "江苏省"}
  }
}

安装anaconda或miniconda，编辑run.bat内容第一行为其activate.bat所在路径和其所在路径
双击run.bat运行程序