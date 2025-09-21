# pull official base image
FROM python:3.13-alpine

EXPOSE 5001

RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools \
    # pillow dependencies
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    # fonts
    font-noto font-noto-emoji


RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
