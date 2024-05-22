FROM planr-planr_app as app




FROM nginx:alpine


COPY --from=app /static /static/

RUN chown -R 101:101 /static

COPY ./nginx-default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-nginx.conf /etc/nginx/nginx.conf

CMD exec nginx -g 'daemon off;'
