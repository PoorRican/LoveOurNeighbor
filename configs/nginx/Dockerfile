FROM nginx

ENV SITE=demo.loveourneighbor.org

VOLUME /etc/letsencrypt

RUN apt-get update
RUN apt-get install certbot python-certbot-nginx -y

RUN nginx
RUN certbot run --nginx --agree-tos -m swe.fig@gmail.com -d $SITE --non-interactive; exit 0;
RUN ps -C "nginx" -o pid= | head -1 | xargs kill -9; exit 0;

# Copy config with SSL capabilities
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
