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


# How to Backup and Restore MySQL database

[this tutorial](https://www.thegeekdiary.com/how-to-backup-and-restore-mysql-database/)

