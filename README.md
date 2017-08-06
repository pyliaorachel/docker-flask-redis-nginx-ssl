# docker-flask-redis-nginx-ssl

Docker example running flask app, redis db, and nginx proxy server with ssl.

[Full Tutorial](https://pyliaorachel.github.io/tutorial/devops/docker/2017/08/04/getting-started-with-docker-running-flask-redisdb-and-nginx.html)

#### Init Project

1. Create project named `example` with the structure below. Different services are seperated into different folders, each running a container (or serveral containers, if you want to scale).
    ```shell
    .
    ├── README.md
    └── src
        ├── docker-compose.yml                      # docker compose configuration
        ├── flaskapp                                # Service 1
        │   ├── Dockerfile                            # image configuration
        │   ├── __init__.py
        │   ├── example
        │   │   ├── __init__.py
        │   │   ├── app.py                            # flask app entry
        │   │   ├── db.py                             # APIs to redis db
        │   │   └── wsgi.py                           # WSGI server entry
        │   ├── requirements.txt                      # dependency information (production)
        │   └── setup.py                              # dependency information (development)
        ├── nginx                                   # Service 2
        │   ├── Dockerfile                            # image configuration
        │   ├── __init__.py
        │   └── nginx.conf                            # nginx server configuration
        └── redisdb                                 # Service 3
            ├── Dockerfile                            # image configuration
            ├── __init__.py
            └── redis.conf                            # redis server configuration
    ```
2. Create `virtualenv` for each container. Since only `flaskapp` need a python environment, we only create this one.
    ```shell
    $ cd src/flaskapp
    $ virtualenv venv
    ```
3. Install Packages in `virtualenv`.
    ```shell
    $ cd src/flaskapp
    $ source venv/bin/activate
    (venv) $ pip3 install -e . # dev mode
    (venv) $ deactivate
    ```

Note that `virtualenv` is optional. It can help you test your project in isolated python environment before you deploy it on docker.

#### Create Docker Network

Create a [Docker network](https://docs.docker.com/engine/userguide/networking/) for communication between the 3 containers below. We will name the network `example`, which is the same as our project name.

```shell
$ docker network create example
```

- Test
  ```shell
  $ docker network ls
  > NETWORK ID          NAME                DRIVER              SCOPE
  > ...
  > abcdefghijkl        example             bridge              local
  > ...
  ```

#### Flask App Container 

The following assumes `venv` in `src/flaskapp` is activated.

###### Add Flask App & Gunicorn

See `src/flaskapp/example/app.py` and `src/flaskapp/example/wsgi.py`.

- Test
    ```shell
    (venv) $ cd src/flaskapp
    (venv) $ gunicorn --bind 0.0.0.0:8080 example.wsgi
    
    # Open browser and go to `localhost:8080`. You should see `Hello World!`.
    ```
- Freeze dependencies into `requirements.txt`
    ```shell
    (venv) $ pip3 freeze | grep -v 'exampleflask' > requirements.txt # ignore dependency on itself
    ```

###### [Deploy on Docker](https://www.smartfile.com/blog/dockerizing-a-python-flask-application/)

See `src/flaskapp/Dockerfile`. `venv` is made ignored by adding it in `.dockerignore`.

- Build image with tag `yourusername/exampleflask`
    ```shell
    $ cd src/flaskapp
    $ docker build -t yourusername/exampleflask .
    ```
- Run container on image `yourusername/exampleflask` with name `exampleflask`, publish port `8080`
    ```shell
    $ docker run -d --rm -p 8080:8080 --name exampleflask yourusername/exampleflask
    ```
- Test
    - Open browser and go to `localhost:8080`. You should see `Hello World!`.
    
#### Redis DB Container 

The following assumes `venv` in `src/flaskapp` is activated.

###### Add Redis DB to Flask App

See `src/flaskapp/example/db.py`.

- Test
    - Install [redis-server](https://redis.io/topics/quickstart) on your local machine first for testing
    ```shell
    # Start the server on default port `6397`
    $ redis-server

    # Start the flask app
    (venv) $ cd src/flaskapp
    (venv) $ gunicorn --bind 0.0.0.0:8080 example.wsgi

    # Open browser and go to `localhost:8080/<your-name>`. You should see `Hello <your-name>!`.
    ```

###### [Deploy on Docker](https://docs.docker.com/samples/redis/#start-a-redis-instance)

See `src/redisdb/Dockerfile` and `src/redisdb/redis.conf`.

- Build image with tag `yourusername/exampleredis`
    ```shell
    $ cd redisdb
    $ docker build -t yourusername/exampleredis .
    ```
- Run container on image `yourusername/exampleredis` with name `exampleredis`, publish port `6379`
    ```shell
    $ docker run -d --rm -p 6379:6379 --name exampleredis yourusername/exampleredis
    ```
- Test
    ```shell
    $ redis-cli
    > 127.0.0.1:6379>

    # This is wrong
    > not connected>
    ```
- Stop the containers, now run `flaskapp` and `redisdb` in docker network `example` for communication
    ```shell
    $ docker stop exampleflask exampleredis

    # No need to publish port for redis, 
    # as the port is `EXPOSE`d in `Dockerfile` to other containers in the same docker network
    $ docker run -d --rm --net example --name exampleredis yourusername/exampleredis
    $ docker run -d --rm -p 8080:8080 --net example --name exampleflask yourusername/exampleflask
    ```
- Test
    - Open browser and go to `localhost:8080/<your-name>`. You should see `Hello <your-name>!`.

_Note_ that `Dockerfile` is needed only when you want to use your customized redis server configuration written in `redis.conf`. 
If you don't need a customized configuration, you don't need to build a new image yourself and can simply use the base image of `redis`:

```shell
$ docker run -d --rm --net example --name exampleredis redis redis-server
```

Then modify `docker-compose.yml` accordingly.

```yml
...
  redis:
    image: redis
    container_name: exampleredis
```

_Note_ that `bind 127.0.0.1` in the `redis.conf` file __SHOULD__ be changed into `bind 0.0.0.0` or else other containers still cannot access the redis server.

#### NGINX Container 

###### Setup an NGINX Server

For `HTTP` requests, see `src/nginx/nginx.conf.sample` and follow [this tutorial](https://pyliaorachel.github.io/blog/tech/system/2017/07/07/flask-app-with-gunicorn-on-nginx-server-upon-aws-ec2-linux.html).

For `HTTPS `requests, see `src/nginx/nginx-ssl.conf.sample` and follow [this tutoiral](https://pyliaorachel.github.io/blog/tech/system/2017/07/14/nginx-server-ssl-setup-on-aws-ec2-linux-with-letsencrypt.html). Make sure that you have used [letsencrypt](https://letsencrypt.org/) or other means to retrieve the certificate and keys.

Choose either of them, modify the `<your-domain-name>` (and `your.domain.name` for `HTTPS`) in the `*.sample` file, and name it `nginx.conf`. For HTTPS, if you did not use `letsencrypt`, also change the `ssl_certificate` and `ssl_certificate_key` to the corresponding paths.

###### [Deploy on Docker](https://hub.docker.com/_/nginx/)

See `src/nginx/Dockerfile`.

- Build image with tag `yourusername/examplenginx`
    ```shell
    $ cd src/nginx
    $ docker build -t yourusername/examplenginx .
    ```
- Run container on image `yourusername/examplenginx` with name `examplenginx`, publish port `80` (and `443` for `HTTPS`). (_Note that -p 8080:8080 is not needed anymore in starting the flask app container, as we will not access this port directly from the browser anymore but instead access this nginx proxy server_)
    ```shell
    # HTTP
    $ docker run -d --rm --net example -p 80:80 --name examplenginx yourusername/examplenginx

    # HTTPS, share the directory containing SSL certificate with -v
    $ docker run -d --rm --net example -p 80:80 -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt --name examplenginx yourusername/examplenginx
    ```
- Test
    - `HTTP`
        - Open browser and go to `http://localhost`. You should see `Hello World!`.
    - `HTTPS`
        - Open browser and go to `https://localhost`. You should see `Hello World!`.


#### Wrap up the Project with Docker Compose

After testing individual containers, you can wrap all the commands up into a single `docker-compose.yml` file, and everything can be started in a single command. All the parameters passed in to the commands when you started the containers are now specified in `docker-compose.yml`. 

_Docker network is not needed anymore, as docker compose creates a default network for all its services. But to build up a more complex network topology, you can create your custom networks in the `docker-compose.yml` file as well._

###### [Deploy with Docker Compose](https://runnable.com/docker/docker-compose-networking)

See `src/docker-compose.yml`.

- Start docker compose
    ```shell
    $ cd src
    $ docker-compose up
    ```
- Test
    - `HTTP`
        - Open browser and go to `http://localhost`. You should see `Hello World!`.
    - `HTTPS`
        - Open browser and go to `https://localhost`. You should see `Hello World!`.

> ## Debug Tips
>
> 1. Use `-it` to run containers in interactive mode so that you can test, view logs, curl other containers, etc. under the environment the app is run in
>   ```shell
>   $ docker run -it --rm -p 8080:8080 --net example --name exampleflask yourusername/exampleflask /bin/bash
>   > root@abcdefghijkl:~#
> 
>   # try curl other containers in the same network
>   $ root@abcdefghijkl:~# apt-get -qq update && apt-get -yqq install curl
>   $ root@abcdefghijkl:~# curl <other-container>:<port>
>   > ...
>   
>   # list networks
>   $ root@abcdefghijkl:~# cat /etc/hosts
>   > ...
>   ```
> 2. Print the logs of a container
>   ```shell
>   $ docker logs exampleflask
>   > ...
>   ```
> 3. List the running containers to ensure they didn't encounter errors
>   ```shell
>   $ docker ps
>   CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                    NAMES
>   abcdefghijkl        yourusername/exampleflask   "gunicorn --bind 0..."   some time ago       Up some time        0.0.0.0:8080->8080/tcp   exampleflask
>   mnopqrstuvwx        yourusername/exampleredis   "docker-entrypoint..."   some time ago       Up some time        6379/tcp                 exampleredis
>   ```
> 4. List information of the network to ensure the containers are run within
>   ```shell
>   $ docker network inspect example
>   > [
>       {
>           "Name": "example",
>           "Id": "...",
>           "Created": "...",
>           "Scope": "local",
>           "Driver": "bridge",
>           "EnableIPv6": false,
>           // ...other properties
>           "Containers": {
>               "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx": {
>                   "Name": "exampleredis",
>                   "EndpointID": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
>                   "MacAddress": "aa:bb:cc:dd:ee:ff",
>                   "IPv4Address": "w.x.y.z/a",
>                   "IPv6Address": ""
>               },
>               // ...other container info
>           },
>           // ...other properties
>        }
>    ]
>   ```

## References

- [Official Doc](https://docs.docker.com/)
- [Dockerizing a Python Flask Application](https://www.smartfile.com/blog/dockerizing-a-python-flask-application/)
- [Docker Redis Samples](https://docs.docker.com/samples/redis/)
- [Docker Compose Networking](https://runnable.com/docker/docker-compose-networking)





