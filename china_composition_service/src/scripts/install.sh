#!/bin/bash
echo "please input your configure path:(default /usr/local), make sure you have permisson:"

read INSTALL_DIR

if [ ! $INSTALL_DIR ]
then
    if [ $UID -ne 0 ]; then 
    echo "need to be root or sudo to install files into /usr/local"
    exit
    fi
    echo "use default install dir: /usr/local"
    cp -Rf ./bin/* /usr/local/bin
    cp -Rf ./lib/* /usr/local/lib
    cp -Rf ./share/* /usr/local/share
    echo "/usr/local/lib" > Godeye.conf
    cp Godeye.conf /etc/ld.so.conf.d/
    ldconfig
    chmod -Rf a+x /usr/local/bin
else
    mkdir -p ${INSTALL_DIR}
    if [ $? -ne 0 ]; then 
    exit
    fi
    cp -Rf ./* $INSTALL_DIR/
    echo "${INSTALL_DIR}/lib" > Godeye-video.conf
	
    chmod -Rf a+x "${INSTALL_DIR}/bin"
    
    echo "YOU should run sudo cp Godeye-video.conf /etc/ld.so.conf.d/  && sudo ldconfig"
fi


