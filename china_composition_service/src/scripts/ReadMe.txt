1. 解压后，在当前目录下执行 sudo sh requirments.sh
2. 执行  sh install.sh(默认安装到/usr/local),例如安装目录写为/home/user/Godeye
  执行  sudo cp Godeye.conf /etc/ld.so.conf.d/  && sudo ldconfig
3. 进入您指定的安装目录(例如 /home/user/Godeye)，编辑/home/user/Godeye/bin/config/config.ini，文件如下所示，
  注意：1.下面没有涉及的变量不允许更改
        2.不要在里面使用任何包括注释在内的多余内容。
        3.如果安装在默认的目录（/usr/local）,请注意修改DumpDir、DownloadDir、LogDir、AnalyzeDataDir、AliResultDir、AliASRJar、PythonParam的目录位置例如修改为（/home/user）
          如果是自定义的安装目录，可以选择默认。
		
  
所有需要配置路径的设置请注意路径的权限，允许程序在当前目录下创建目录和文件 
 
C++端监听的端口
CppListenGrpcHost=10.1.12.102:9000

Java监听的端口
JavaListenGrpcHost=10.1.12.245:9001

生成Dump的文件目录 
DumpDir=./   

下载视频的目录
DownloadDir=./video

日志生成的目录，注意加上文件名
LogDir=./log/Godeye-main.log

下载单个文件的下载速度
DownloadSpeed=1000k

下载断线重连的次数
DownloadTryTimes=3

注意：建议设置为下载视频目录的子目录
AnalyzeDataDir=./video/data

注意：建议设置为下载视频目录的子目录
AliResultDir=./video/alires

音频转文本的javaSDK，默认在bin目录下
AliASRJar=./asrV1.1.jar

注意：建议设置为下载视频目录的子目录
PythonParam=./video/pythonParam



不要以root用户执行该命令，运行程序的命令如下
cd /home/user/Godeye/bin && ./Godeye --setting=config/config.ini
查看/home/user/Godeye/bin/log/Godeye-main.log文件
