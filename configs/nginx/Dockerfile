FROM nginx

RUN apt-get update
RUN apt-get install certbot python-certbot-nginx cron git vim -y

# vim should be the default editor
# for the uniniated, this can be changed to nano by executing
#   export EDITOR=nano
ENV EDITOR=vim

# Install nginx-maintenance-mode
ENV PREV=$(pwd)

ENV DIR="/root/nginx-maintenance-mode"
RUN git clone https://github.com/tmiland/Nginx-Maintenance-Mode.git $DIR
RUN cd $DIR
RUN cp -rp ./maintenance-page.conf /etc/nginx/snippets/
RUN git clone https://github.com/tmiland/server-error-pages.git /etc/nginx/html/server-error-pages
RUN cp -rp /etc/nginx/html/server-error-pages/_site/maintenance-page.html /etc/nginx/html/server-error-pages/_site/maintenance-page_off.html
RUN chmod +x maintenance.sh
RUN ln -s $DIR/maintenance.sh /usr/bin/maintenance

RUN cd $PREV

# Setup letsencrypt
ENV SITE="-d demo.loveourneighbor.org -d loveourneighbor.org -d www.loveourneighbor.org"

VOLUME /etc/letsencrypt

RUN nginx
RUN certbot run --nginx --agree-tos -m swe.fig@gmail.com $SITE --non-interactive; exit 0;
RUN ps -C "nginx" -o pid= | head -1 | xargs kill -9; exit 0;

# Copy config with SSL capabilities
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
