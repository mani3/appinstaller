# App install

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

### Create my self signed certification

```
$ ./create-crt.sh
```

### Sqlite3 migration

```
// dbのマイグレーションを行うための初期化(実行済み)
$ python manage.py db init

// モデルデータを更新後、実行するとマイグレーションファイルが生成される
$ python manage.py db migrate -m "コメント"

// マイグレーションファイルをdbに反映する
$ python manage.py db upgrade
```
