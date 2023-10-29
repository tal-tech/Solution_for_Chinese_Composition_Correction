1 修改microservice_demo.*文件名
1.1 将文件名microservice_demo.*修改成实际的名字
1.2 microservice_demo.cpp、service_main.cpp中引用的头文件名称进行修改
1.3 将CMakeLists.txt中的microservice_demo.cpp修改成实际的名称

2 修改工程和可执行文件名字
2.1 将CMakeLists中的项目和文件名:MicroserviceDemo修改成实际的名称
2.2 将scripts/build_tar.gz.sh中的项目名称修改成同2.1中的名称

3 错误码定义
3.1 在service_error.h中修改sub_code的值，每个值代表一个服务
3.2 根据实际需求在service_error.h中增加ServiceError、TechnicalError

4 配置修改
4.1 修改用于本地测试的配置文件: config/config.ini
4.2 在本地apollo增加配置项，其中的key名称一定要和apollo_conf.h中的定义一致，新增时也是在apollo_conf.h中增加定义
4.3 在PaaS上部署时，通过环境变量的形式在yaml中需要增加config/config.ini中的配置

5 业务逻辑
5.1 修改service_main.cpp中Listen处理逻辑：增加url和对应的处理逻辑
5.2 具体的业务修改是在1.1的文件中进行

6 修改Dockerfile
6.1 修改工程目录
6.2 修改可执行文件名称

7 修改模型
7.1 将模型放到ai_model目录
7.2 修改ai_model/init_model.sh，修改MODEL_NAME, INSTALL_DIR
