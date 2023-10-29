FROM registry.cn-beijing.aliyuncs.com/ailab-paas/cn-comp:v0.0.0.1

RUN  apt-get install -y libglib2.0-dev && \
     apt-get install -y libboost-dev libboost-filesystem-dev libboost-system-dev libboost-log-dev && \
     apt-get install -y libcurl4-openssl-dev

COPY package/ /home/cmp
WORKDIR /home/cmp/bin
RUN  echo '/home/cmp/lib' > /etc/ld.so.conf.d/cmp.conf && ldconfig
RUN chmod 777 -Rf /home/cmp/bin/*

ENV LD_LIBRARY_PATH=/home/cmp/lib:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH=/home/cmp/lib/ubuntu-cuda10:${LD_LIBRARY_PATH}
CMD ["./Evaluation"]
#CMD sleep 100d
