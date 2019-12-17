#!/bin/bash
# This formats a new Amazon AMI 2 instance

# TODO: check for sudo
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

docker info

sudo curl -L https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "alias d-c='docker-compose'" >> /home/ec2-user/.bash_profile
echo "alias docker-clean=' \
    docker container prune -f; \
    docker image prune -f; \
    docker network prune -f; \
    docker volume prune -f'" >> /home/ec2-user/.bash_profile