# Windows 平台安装与配置 MongoDB

## MongoDB 下载

MongoDB 提供了可用于 32 位和 64 位系统的预编译二进制包，你可以从MongoDB官网下载安装，MongoDB 预编译二进制包下载地址：https://www.mongodb.com/download-center/community

![image-20220529184127844](C:\Users\shilong\AppData\Roaming\Typora\typora-user-images\image-20220529184127844.png)

下载 .msi 文件，下载后双击该文件，按操作提示安装即可。



安装过程中，你可以通过点击 "Custom(自定义)" 按钮来设置你的安装目录。

![img](https://www.runoob.com/wp-content/uploads/2013/10/win-install1.jpg)

![img](https://www.runoob.com/wp-content/uploads/2013/10/win-install2.jpg)

修改路径为mongodb，目的是统一路径，方便修改

![mon0](./figs/mon0.png)

![mon1](./figs/mon1.png)

下一步安装 **"install mongoDB compass"** 不勾选（当然你也可以选择安装它，可能需要更久的安装时间），MongoDB Compass 是一个图形界面管理工具，我们可以在后面自己到官网下载安装，下载地址：https://www.mongodb.com/download-center/compass。

![img](https://www.runoob.com/wp-content/uploads/2013/10/8F7AF133-BE49-4BAB-9F93-88A9D666F6C0.jpg)





------

## 配置 MongoDB 服务器

**更改端口号**

找到MongoDB安装bin目录下的mongd.cfg文件，用文本编辑器打开。
<img src="./figs/mongodb1.png" alt="image-20220529184708658" style="zoom:50%;" />

<img src="https://img-blog.csdnimg.cn/20200429003544501.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzE4NTQ3MzQx,size_16,color_FFFFFF,t_70" alt="在这里插入图片描述" style="zoom:100%;" />

注：这里的port 改为 9999，bindip改为0.0.0.0，默认127.0.0.1只能本地访问，改为0.0.0.0后可以远程访问。

改完后，可以通过任务管理器，重新启动MongoDB服务

![mon2](./figs/mon2.png)