FROM ubuntu:22.04
LABEL MAINTAINER bharath<bharth.santhakumar@zohocorp.com>
#setting zoho proxies
ENV http_proxy=http://192.168.100.100:3128 https_proxy=http://192.168.100.100:3128
#required apt installations
RUN apt update -y
RUN apt install wget -y
RUN apt install make -y
RUN apt install libssl-dev -y
RUN apt install gcc -y
RUN apt install zlib1g-dev -y
RUN apt install libffi-dev -y
#unsetting zoho proxies
ENV http_proxy=
ENV https_proxy=
#Download of required packages
WORKDIR /root/install/
RUN wget 10.51.51.235:7777/openssl-3.1.0.tar.gz
RUN wget 10.51.51.235:7777/perl-5.36.0.tar.gz
RUN wget 10.51.51.235:7777/Python-3.10.10.tgz
RUN wget 10.51.51.235:7777/get-pip.py
RUN wget 10.51.51.235:7777/cx_Freeze-5.0.2.tar.gz
RUN wget 10.51.51.235:7777/cx_Freeze-6.13.0.tar.gz
RUN wget 10.51.51.235:7777/requirements.txt
#extraction of required packages
RUN tar -zxf openssl-3.1.0.tar.gz
RUN tar -zxf perl-5.36.0.tar.gz
RUN tar -zxf Python-3.10.10.tgz
RUN tar -zxf cx_Freeze-6.13.0.tar.gz
#perl installation
WORKDIR /root/install/perl-5.36.0/
RUN ./Configure -des
RUN make && make install
RUN make clean
RUN ldconfig
#openssl installation
WORKDIR /root/install/openssl-3.1.0/
RUN ./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib -fPIC
RUN make 
RUN make install
RUN printf "/usr/local/ssl/lib64" > /etc/ld.so.conf.d/openssl.conf
RUN ldconfig
#python installation
WORKDIR /root/install/Python-3.10.10/
RUN ./configure --with-openssl=/usr/bin/openssl
RUN make 
RUN make install
RUN ldconfig
#test
WORKDIR /usr/local/ssl/lib64/
RUN  cp -r * /usr/lib
WORKDIR /root/install/openssl-3.1.0/include/openssl
RUN  cp -r * /usr/include
RUN  cp -r * /usr/local/ssl/include
RUN  cp -r * /usr/local/ssl/include/openssl
RUN ldconfig
RUN  cp -r * /usr/local/ssl/include
WORKDIR /root/install/openssl-3.1.0
RUN  cp -r lib* /usr/local/ssl/lib64/
RUN  cp -r lib* /usr/lib/
RUN ldconfig
WORKDIR /root/install/openssl-3.1.0/include/openssl
RUN  cp -r * /usr/include/
RUN  cp -r * /usr/local/ssl/include/
RUN  cp -r * /usr/local/ssl/include/openssl
WORKDIR /root/install/openssl-3.1.0/
RUN  cp -r libssl.a /usr/local/ssl/lib64/
RUN  cp -r *.a /usr/local/ssl/lib64/
RUN  cp -r *.so* /usr/local/ssl/lib64/
WORKDIR include/openssl/
RUN mkdir -p /usr/include/openssl/
RUN  cp -r * /usr/include/openssl/
RUN  cp -r * /usr/local/ssl/include/openssl/
RUN ldconfig
#pip module installation
WORKDIR /root/install/
RUN python3.10 get-pip.py
RUN python3.10 -m pip install -r requirements.txt
#cx-freeze
# RUN tar -zxf cx_Freeze-5.0.2.tar.gz
# WORKDIR /root/install/cx_Freeze-5.0.2
# RUN python3.10 setup.py build
# RUN python3.10 setup.py teinstall
RUN tar -zxf cx_Freeze-6.13.0.tar.gz
WORKDIR /root/install/cx_Freeze-6.13.0
RUN python3.10 -m pip install .
# ENV http_proxy=http://192.168.100.100:3128 https_proxy=http://192.168.100.100:3128
# RUN apt install patchelf
WORKDIR /