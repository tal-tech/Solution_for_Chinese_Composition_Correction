export LD_LIBRARY_PATH=../sdk/libs:$LD_LIBRARY_PATH

# Set head pose model
MODEL=../sdk/models/yolo_models/yolov5l.engine

# Set test data
IMAGES_PATH=../img_test/

# Set test data
CONFIG_PATH=../sdk/models/yolo_models/config.ini


./performance_testing_GPU $MODEL $IMAGES_PATH $CONFIG_PATH 1




