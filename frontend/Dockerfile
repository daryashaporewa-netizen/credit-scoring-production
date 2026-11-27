FROM busybox:1.37 AS assets

WORKDIR /site

COPY index.html ./index.html


FROM nginx:alpine AS runtime

COPY --from=assets /site/index.html /usr/share/nginx/html/index.html

EXPOSE 80
