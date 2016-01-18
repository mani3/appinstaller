# App installer

- Mac OSX

## Run

### Flask enviropment

```
$ ./env.sh flask

// active virtualenv 
$ source flask/bin/activate

// deactivate
//$ deactivate
``` 

### gunicorn

- Run standalone app

```
$ gunicorn -b 127.0.0.1:4000 app:app
```

### Sqlite3 migration

```
// dbのマイグレーションを行うための初期化
$ python manage.py db init

// モデルデータを更新後、実行するとマイグレーションファイルが生成される
$ python manage.py db migrate -m "コメント"

// マイグレーションファイルをdbに反映する
$ python manage.py db upgrade
```

### Apache 

- リバースプロキシの設定

```
$ sudo vim /etc/apache2/users/<user name>.conf
```

```
ProxyPass /appinstaller http://localhost:4000/appinstaller nocanon
ProxyPassReverse /appinstaller http://localhost:4000/appinstaller
ProxyRequests Off
AllowEncodedSlashes NoDecode
```

- Self singed certificateが使用できるようにhttpd.confを変更する

```
$ sudo vim /etc/apache2/httpd.conf
```

```
89c89
< LoadModule socache_shmcb_module libexec/apache2/mod_socache_shmcb.so
---
> #LoadModule socache_shmcb_module libexec/apache2/mod_socache_shmcb.so
143c143
< LoadModule ssl_module libexec/apache2/mod_ssl.so
---
> #LoadModule ssl_module libexec/apache2/mod_ssl.so
516c516
< Include /private/etc/apache2/extra/httpd-ssl.conf
---
> #Include /private/etc/apache2/extra/httpd-ssl.conf
```

- 再起動

```
$ sudo apachectl restart
```

### Self-SSL certificate

- 証明書の作成

```
$ ./create-crt.sh
$ tree -L 2 cer
cer
├── myself-server.cer
├── myself-server.key
└── server.crt
```

- 証明書の設定

```
$ sudo cp myself-server.key /private/etc/apache2/server.key
$ sudo cp server.crt /private/etc/apache2/server.crt
```

