
#CAFFE_LIBRARY =  ./lib
#OPENCV_INC =  /usr/local/include/
#SYSTEM_LIB = /usr/lib/x86_64-linux-gnu

LIBDIR = -Wl,--start-group -lpthread -lm -lstdc++ -L../../sdk/libs  -ldet_chn_comp -ldet_timu_yolov5 -lrec_chn_comp  -lopencv_core -lopencv_imgcodecs  -lopencv_imgproc -lboost_filesystem -lboost_log -lboost_log_setup -lboost_regex -lboost_system -lboost_thread -Wl,--end-group\
	 -Wl,-rpath,../../sdk/libs\


#CPPFLAGS = -Wall -Winline -pipe -ffast-math -D_LINUX_64_ -DNO_DLL -mavx -mavx2 -msse -Wshadow  -DCUDNN -DGPU -DYOLOCUDNN -DYOLOGPU
CPPFLAGS = -Wall -Winline -pipe -ffast-math -D_LINUX_64_ -DNO_DLL -mavx -mavx2 -msse -Wshadow -DOPENCV -DOPENMP -Wno-unused-result -Wno-unknown-pragmas -fPIC -DBOOST_LOG_DYN_LINK
INCLUDEDIR =  -I../../sdk/include
define mkObjDir
    @ test -d $(1) || mkdir -p $(1)
endef

define mkGitInfo
	@echo `git log | head -3` > output/version.txt
	@echo "------" >> output/version.txt
	@echo `git diff` >> output/version.txt
endef

GCC = g++ -std=c++11 -w  -fopenmp

OBJDIR = obj

TARGET1 =performance_testing_GPU 
TARGET2 =performance_testing_GPU_debug

        #src/tool/LIST.o
#COREOBJ = \
        src/tool/json.o\
        src/tool/Tools.o\
   	src/textline/MemPool.o \
    	src/DNN/tiny_dnn/util/util.o \
    	src/bdthread/asr_lock.o\
    	src/bdthread/asr_log.o\
    	src/bdthread/asr_thread.o\
        src/RaiseHand/RaiseHand.o\
        src/openpose_hand/Det_api.o\
        src/openpose_hand/detectHand.o
	#src/openpose_hand/Det_api.o
	#src/reg/comReg.o \
    	#src/DNN/tiny_dnn/api/DNN_face_smile_mouth.o \
    	#src/DNN/tiny_dnn/api/DNN_recognition.o \
    	#src/DNN/tiny_dnn/api/lstm_demo.o \
    	#src/DNN/tiny_dnn/api/DNN_face_occlusion.o 

COREOBJ_DEBUG = $(patsubst %.o,%_debug.o,$(COREOBJ))

OBJ1 = $(addprefix $(OBJDIR)/, $(COREOBJ) performance_testing.o)
OBJ2 = $(addprefix $(OBJDIR)/, $(COREOBJ_DEBUG) performance_testing_debug.o)

all: $(TARGET1) $(TARGET2)
	rm -rf output
	mkdir -p output
#	mv ${TARGET1}  output/
#	mv ${TARGET2}  output/

$(TARGET1) : $(OBJ1)
	$(GCC) -O2 -o $@ $^ $(LIBDIR) $(INCLUDEDIR)
$(TARGET2) : $(OBJ2)
	$(GCC) -g -o $@ $^ $(LIBDIR) $(INCLUDEDIR)

$(OBJDIR)/%.o : %.cpp
	@ test -d $(OBJDIR) || mkdir -p $(OBJDIR)
	$(call mkObjDir,$(dir $@))
	$(GCC) -O2 $(CPPFLAGS) -c $< -o $@ $(INCLUDEDIR)

$(OBJDIR)/%_debug.o : %.cpp
	@ test -d $(OBJDIR) || mkdir -p $(OBJDIR)
	$(call mkObjDir,$(dir $@))
	$(GCC) $(CPPFLAGS) -g -c $< -o $@ $(INCLUDEDIR)

clean:
	rm -rf ./obj
	rm -rf ./output
	rm ${TARGET1}
	rm ${TARGET2}
