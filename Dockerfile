FROM centos:5
MAINTAINER arunagiriswaran<arunagiriswaran.e@zohocorp.com>
WORKDIR /root/install
RUN rm /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/libselinux.repo
RUN printf "[CentOS5.11]\nname=CentOS-5.11-x86_64\nbaseurl=http://vault.centos.org/5.11/os/x86_64/\nenabled=1\ngpgcheck=1\n\n[CentOS5.11-updates]\nname=CentOS-5.11-updates-x86_64\nbaseurl=http://vault.centos.org/5.11/updates/x86_64/\nenabled=1\ngpgcheck=1">/etc/yum.repos.d/CentOS-Base.repo
#ENV http_proxy=http://192.168.100.100:3128 https_proxy=http://192.168.100.100:3128
RUN yes "yes" | yum update --nogpgcheck
RUN yes "yes" | yum install wget --nogpgcheck
RUN unset http_proxy
RUN unset https_proxy
ENV http_proxy=
ENV https_proxy=
RUN wget 172.22.158.64:7777/epel-release-5-4.noarch.rpm
RUN wget 172.22.158.64:7777/openssl-1.0.1k.tar.gz
RUN wget 172.22.158.64:7777/Python-3.3.1.tgz
RUN wget 172.22.158.64:7777/perl-5.24.1.tar.gz
RUN wget 172.22.158.64:7777/cx_Freeze-5.0.2.tar.gz
RUN wget 172.22.158.64:7777/get-pip.py
RUN rpm -ivh epel-release-5-4.noarch.rpm
#ENV http_proxy=http://192.168.100.100:3128 https_proxy=http://192.168.100.100:3128
RUN yes "yes" | yum update --nogpgcheck
RUN yes "yes" | yum install libffi-devel --nogpgcheck
RUN yes "yes" | yum install make --nogpgcheck
RUN yes "yes" | yum install gcc --nogpgcheck
RUN tar -zxf perl-5.24.1.tar.gz
WORKDIR perl-5.24.1
RUN sh Configure -de
RUN make && make install
WORKDIR /root/install/
RUN tar -zxf openssl-1.0.1k.tar.gz
WORKDIR openssl-1.0.1k
RUN ./config -fPIC
RUN make && make install
RUN ./config shared
RUN make clean
RUN make && make install
RUN printf "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl.conf
RUN ldconfig
RUN yes "yes" | yum install zlib-devel --nogpgcheck
WORKDIR /root/install
RUN tar -zxf Python-3.3.1.tgz
WORKDIR Python-3.3.1
RUN sed -i "/SSL=\/usr\/local\/ssl/c\SSL=/usr/local/ssl" Modules/Setup.dist
RUN sed -i "/_ssl _ssl.c/c\_ssl _ssl.c \\\\" Modules/Setup.dist
RUN sed -i '/-DUSE_SSL/c\       -DUSE_SSL -I\$(SSL)/include -I\$(SSL)/include/openssl \\' Modules/Setup.dist
RUN sed -i '/-L$(SSL)\/lib/c\       -L$(SSL)\/lib -lssl -lcrypto' Modules/Setup.dist
RUN sed -i '/_socket socketmodule.c/c\_socket socketmodule.c' Modules/Setup.dist
RUN sed -i '/_socket socketmodule.c/c\_socket socketmodule.c' Modules/Setup.dist
RUN sed -i '/_md5 md5module.c md5.c/c\_md5 md5module.c md5.c' Modules/Setup.dist
RUN sed -i '/_sha1 sha1module.c.c/c\_sha1 sha1module.c.c' Modules/Setup.dist
RUN sed -i '/_sha256 sha256module.c/c\_sha256 sha256module.c' Modules/Setup.dist
RUN sed -i '/_sha512 sha512module.c/c\_sha512 sha512module.c' Modules/Setup.dist
RUN sed -i '/zlib zlibmodule/c\zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz' Modules/Setup.dist
RUN ./configure
RUN make 
RUN make install
RUN ln /usr/local/lib/libpython3.3m.a /usr/local/lib/libpython3.3.a
WORKDIR /usr/local/ssl/lib
RUN yes "yes" | cp * /usr/lib; exit 0
WORKDIR /root/install/openssl-1.0.1k/include/openssl
RUN yes "yes" | cp * /usr/include
RUN yes "yes" | cp * /usr/local/ssl/include
RUN yes "yes" | cp * /usr/local/ssl/include/openssl
RUN ldconfig
RUN yes "yes" | cp * /usr/local/ssl/include
WORKDIR /root/install/openssl-1.0.1k
RUN yes "yes" | cp lib* /usr/local/ssl/lib/
RUN yes "yes" | cp lib* /usr/lib/
RUN ldconfig
WORKDIR /root/install/openssl-1.0.1k/include/openssl
RUN yes "yes" | cp * /usr/include/
RUN yes "yes" | cp * /usr/local/ssl/include/
RUN yes "yes" | cp * /usr/local/ssl/include/openssl
WORKDIR /root/install/openssl-1.0.1k
RUN yes "yes" | cp libssl.a /usr/local/ssl/lib/
RUN yes "yes" | cp *.a /usr/local/ssl/lib/
RUN yes "yes" | cp *.so* /usr/local/ssl/lib/
WORKDIR include/openssl
RUN mkdir /usr/include/openssl/
RUN yes "yes" | cp * /usr/include/openssl/
RUN yes "yes" | cp * /usr/local/ssl/include/openssl/
RUN ldconfig
WORKDIR /root/install/
RUN python3.3 get-pip.py
RUN python3.3 -m pip install setuptools==35.0.2
RUN python3.3 -m pip install cryptography==1.8.1
RUN python3.3 -m pip install paramiko==2.1.2
RUN python3.3 -m pip install scp
RUN python3.3 -m pip install pyparsing
RUN python3.3 -m pip install psutil
RUN python3.3 -m pip install xmljson
RUN python3.3 -m pip install docker-py
RUN python3.3 -m pip install pycrypto
WORKDIR /root/install/
RUN tar -zxf cx_Freeze-5.0.2.tar.gz
WORKDIR cx_Freeze-5.0.2
RUN python3.3 setup.py build
RUN python3.3 setup.py install
WORKDIR /
