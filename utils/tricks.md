The following are small tricks and hacks that have been used in the development of the LON website that might prove
useful in the future.

# Getting local server accessible from WAN facing server

This was used to test out payeezy gateway since there callback URLs needed to be publicly accessible.

## On the Local End

To forward a local port to a remote server:
Please note that on the server, `/etc/ssh/sshd_config` must have the option `GatewayPorts yes` enabled for this to work.

```bash
ssh -R 8000:localhost:8000 ubuntu@repo.loveourneighbor.org -i LON-home.pem -N
```

## On the Server

To redirect port 8000 to port 80 (a privileged port, since a login to root wasn't an option):

```bash
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8000
```


# Renewing Certbot Certificates:

Because auto-renew is not setup in docker image (yet):

    1. Shutdown nginx service:
        ```bash
        docker-compose stop nginx
        ```

    2. Startup temporary container:
        ```bash
        docker run --volumes-from lon_nginx_1 -p 80:80 -i --tty nginx bash
        ```

    3. Then in the temporary container:
        ```bash
        apt-get update
        apt-get install -y certbot python-certbot-nginx -y
        certbot renew
        ```

    4. Exit temporary container via Ctrl-D:

    5. Restart nginx service:
        ```bash
        docker-compose up -d nginx
        ```

The commands to run on the temp container could be bundled in step 2.

Ideally, this should be run without stopping the nginx service.
