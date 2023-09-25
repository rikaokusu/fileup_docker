FROM python:3.7.9
# ENV PYTHONPATH "${PYTHONPATH}:/training"
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
# RUN apt-get update && apt-get install -y wkhtmltopdf && apt-get clean;
# RUN wget https://moji.or.jp/wp-content/ipafont/IPAexfont/IPAexfont00401.zip \
    # && unzip IPAexfont00401.zip \
    # && mv IPAexfont00401 /usr/share/fonts \
    # && fc-cache -f
# ADD ./src/training/requirements.txt /code/
ADD ./src/requirements.txt /code/
RUN pip install -r requirements.txt
# RUN sodo apt-get install zlib1g-dev
RUN apt-get install -y zlib1g-dev
ADD . /code/