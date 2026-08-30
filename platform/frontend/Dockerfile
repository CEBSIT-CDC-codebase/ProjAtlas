FROM nginx:stable-alpine
LABEL Name=projectome-atlas Version=0.0.1
COPY dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
