FROM nginx

RUN apt-get update
RUN apt-get install certbot python-certbot-nginx cron git vim -y

# vim should be the default editor
# for the uniniated, this can be changed to nano by executing
#   export EDITOR=nano
ENV EDITOR=vim

# Setup maintenance mode stuff
COPY maintenance.html /root/maintenance.html
COPY maintenance.sh /root/maintenance.sh
RUN chmod +x /root/maintenance.sh
RUN ln -s /root/maintenance.sh /usr/bin/maintenance
RUN mkdir /var/www
RUN chmod 777 /var/www

# Setup letsencrypt
ENV SITE="-d demo.loveourneighbor.org -d loveourneighbor.org -d www.loveourneighbor.org"

VOLUME /etc/letsencrypt

# this is a hueristic attempt to get letsencrypt to config at startup
# RUN nginx
# RUN certbot run --nginx --agree-tos -m swe.fig@gmail.com $SITE --non-interactive; exit 0;
# RUN ps -C "nginx" -o pid= | head -1 | xargs kill -9; exit 0;

# Copy config with SSL capabilities
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
