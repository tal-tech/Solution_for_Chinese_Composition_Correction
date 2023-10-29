export LD_LIBRARY_PATH=../sdk/libs:$LD_LIBRARY_PATH

# 设置模型文件路径
MODEL_PATH=../sdk/models/rec_models/rec_chn_rec_v2.0.0.trt

# 设置测试图片路径
IMAGES_PATH=../img_test/

# 设置字典文件
DICT_PATH=../sdk/models/rec_models/zidian_new_5883.txt

# 设置配置文件
CONFIG_PATH=../sdk/models/rec_models/config.ini

# 设置demo中每次读入图片数，最好和max_batch_size参数一致
BATCH_SIZE=24

# 设置循环次数
RUN_LOOP=1

./performance_testing_GPU $MODEL_PATH $IMAGES_PATH $CONFIG_PATH $DICT_PATH $BATCH_SIZE $RUN_LOOP


