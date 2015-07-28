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


