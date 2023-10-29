export LD_LIBRARY_PATH=../sdk/libs:$LD_LIBRARY_PATH


# 设置模型文件路径
TEXT_MODEL_PATH=../sdk/models/det_models/textsnake_chs.trt

# 设置测试图片路径
IMAGES_PATH=../img_test/

# 设置配置文件
CONFIG_PATH=../sdk/models/det_models/config.ini

# 设置demo中每次读入图片数，最好和max_batch_size参数一致
BATCH_SIZE=1

# 设置循环次数
RUN_LOOP=1

./performance_testing_GPU $MODEL_PATH $TEXT_MODEL_PATH $IMAGES_PATH $CONFIG_PATH $BATCH_SIZE $RUN_LOOP


