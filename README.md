# 项目审批系统

相关截图(文末还有)

![all_apply](https://cos.rmboot.com/approval-system/all_apply.png)

![my_apply_id](https://cos.rmboot.com/approval-system/my_apply_id.png)

## 安装相关库
```
$ git clone https://github.com/rmboot/approvalsystem
$ cd approvalsystem
$ pipenv install
$ pipenv shell
```
## 初始化数据库
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```
## 初始化role,status,dept表
在数据库控制台执行[init.sql](init.sql)的语句
## 初始化users表
###### 1.取消[user.py](./approval_system/blueprints/user.py)文件视图函数index的注释，执行
```
$ flask run
* Running on http://127.0.0.1:5000/
```
###### 2.访问 http://127.0.0.1:5000/ 会生成相应用户，并打印提示信息
###### 3.Press CTRL+C 关闭Flask，将取消的注释再次注释

## 所有配置完成，再次执行，然后去登录吧
```
$ flask run
* Running on http://127.0.0.1:5000/
```



Pipenv 下载速度太慢可以选择指定源
```
$ pipenv install --pypi-mirror https://pypi.tuna.tsinghua.edu.cn/simple
```
或者去看一下[Pipenv借助系统环境变量设置国内源](https://zhuanlan.zhihu.com/p/58758752)

![pending_approval](https://cos.rmboot.com/approval-system/pending_approval.png)

![apply](https://cos.rmboot.com/approval-system/apply.png)

![pending_approval_id](https://cos.rmboot.com/approval-system/pending_approval_id.png)

## License

This project is licensed under the MIT License (see the[LICENSE](LICENSE) file for details).
