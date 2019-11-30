FROM nginx

ENV SITE=demo.loveourneighbor.org

RUN rm /etc/nginx/conf.d/default.conf
COPY uwsgi_params /etc/nginx
COPY nginx.conf /etc/nginx/conf.d

VOLUME /var/www/letsencrypt
VOLUME /etc/letsencrypt

RUN apt-get update
RUN apt-get install certbot python-certbot-nginx -y

RUN echo "certbot --nginx --agree-tos -m swe.fig@gmail.com -d $SITE" >> /tmp/enable_ssl.sh
RUN echo -e "\n\n\t************************************************************\n\t* REMEMBER TO EXECUTE:                                     *\n\t*     'docker-compose run nginx bash /tmp/enable_ssl.sh'   *\n\t*    This changes the nginx.conf file                      *\n\t*    It is recommended that you agree to force redirects!  *\n\t************************************************************\n\n"