#-*-coding:utf-8-*-
"""
@date: 2021. 02. 06
@auther: Hu Fei
@doc: 帮助文档，方便平时开发
"""

import re
import os
import json

def data_pv(datadict):
    '''
    分析数据在频数指定百分比下，词条占比多少
    :param datadict:
    :return:
    '''
    cibiao = len(datadict)
    print("词表：\t %d" % cibiao)
    values = sorted(list(datadict.values()), reverse=True)
    ciliang = sum(values)
    print("词总量：\t %d" % ciliang)

    baifenbilist = [0.8, 0.85, 0.9, 0.95, 1]
    numb = {} # key 为词频， 值 为词频的频率
    for x in datadict:
        if datadict[x] not in numb:
            numb[datadict[x]] = 1
        else:
            numb[datadict[x]] += 1

    keys = sorted(list(numb.keys()),reverse = True) # 词频
    sum_pinshu = 0
    sum_ci = 0
    index = 0
    for pinshu in keys: # 从高频到低频累加
        sum_pinshu += pinshu * numb[pinshu]
        sum_ci += numb[pinshu]
        if sum_pinshu / ciliang > baifenbilist[index]:
            index += 1
            print("%d\t%f\t%f" % (pinshu,sum_pinshu / ciliang, sum_ci/cibiao))

def get_json_path(path):
    '''
    获取当前文件下的所有json路径
    :param path:
    :return:
    '''
    list = []
    filelist = os.listdir(path)
    for file in filelist:
        if file.endswith(".json"):
            list.append(os.path.join(path, file))
        elif os.path.isdir(os.path.join(path, file)):
            addlist = get_json_path(os.path.join(path, file))
            list += addlist
    return list

def get_txt_path(path):
    '''
    获取当前文件下的所有txt路径
    :param path:
    :return:
    '''
    list = []
    filelist = os.listdir(path)
    for file in filelist:
        if file.endswith(".txt"):
            list.append(os.path.join(path, file))
        elif os.path.isdir(os.path.join(path, file)):
            addlist = get_txt_path(os.path.join(path, file))
            list += addlist
    return list

def is_chinese(char):
    '''
    如果是中文字符，则返回 True
    '''
    pattern_num_comma = r"[\u4E00-\u9FA5]"
    return re.match(pattern_num_comma, char)

def findkey(sString):
    """
    返回字符串中的中文字符串
    :param sString:
    :return:
    """
    key = ""
    for x in sString:
        if is_chinese(x):
            key += x
    return key

def openrfile(filename):
    return open(filename, "r", encoding="utf-8")

def openwfile(filename):
    return open(filename, "w", encoding="utf-8")

def jsondump(data,filepath):
    json.dump(data, openwfile(filepath), ensure_ascii=False, indent=1)

def jsonload(filepath):
    return json.load(openrfile(filepath))

def extract_word_pattern(in_text, word_list, max_gram=9):
    '''
    利用数字模板，输入文本中抽取字符串
    算法分4步

    1 step:原始字符串映射成正则化字符串，并生成对应的序号映射关系，例如
    text:2017年4月15日—>$年$月$日
    text_map:[0,4],4,[5,6],6,[7,9],9

    2 step:text映射关系枚举生成ngram词表

    3 step:text_map, 还原生成原始序号

    4 step:ngram词表hash后与输入模板hash值比较

    :param in_text:
    :param word_list: 数字模板 $小时，约$天等
    :return: [[start, end],[start, end]]
    '''

    find_ys_index_list = []
    text = in_text # "方天画戟"
    text_index_map = list(range(len(text))) # [0,1,2,3]

    index_gram_texts = []
    gram_texts = []
    for gram in range(max_gram, 1, -1): # [9,8,7,…,2]
        if len(text) >= gram: # 只找比输入字符串短的部分
            index_gram_texts.extend([text_index_map[jj: jj + gram] for jj in range(0, len(text_index_map) + 1 - gram)])
            gram_texts.extend([text[jj: jj + gram] for jj in range(0, len(text) + 1 - gram)])

    # index_gram_texts  [[0, 1, 2, 3], [0, 1, 2], [1, 2, 3], [0, 1], [1, 2], [2, 3]]
    # gram_texts  ['方天画戟', '方天画', '天画戟', '方天', '天画', '画戟']
    print(gram_texts)
    # 3 step:text_map, 还原生成原始序号
    gram_text_indexs = []
    for index_gram_text in index_gram_texts:
        start = index_gram_text[0]
        end = index_gram_text[-1] + 1
        gram_text_indexs.append([start, end])
    # gram_text_indexs [[0, 4], [0, 3], [1, 4], [0, 2], [1, 3], [2, 4]]
    if isinstance(in_text, list): # 如果输入是一个 列表 这里可以处理分词不同情况
        for word_index, word in enumerate(in_text):
            if len(word) > 1:
                gram_texts.append([word])
                gram_text_indexs.append([word_index, word_index + 1])

    # 4 step:ngram词表hash后与输入模板hash值比较
    for sub_text_index, gram_text in enumerate(gram_texts):
        gram_text = "".join(gram_text)
        if gram_text in word_list:
            gram_text_index = gram_text_indexs[sub_text_index]
            is_contained = False
            for hold_sub_text_index in find_ys_index_list:
                if is_over(hold_sub_text_index, gram_text_index): # 输出的内容不能有交叉
                    is_contained = True
                    break
            if not is_contained:
                find_ys_index_list.append(gram_text_index)

    find_ys_index_list = sorted(find_ys_index_list, key=lambda x: x[0])
    return find_ys_index_list

def is_over(index1, index2):
    '''
    判断两个子句的交叠情况
    :param index1:[nstart1,nend1]
    :param index2:[nstart2,nend2]
    :return: 0:句子完全错开 1:句2包含句1  2:句1包含句2  3:句1先起先止  4:句2先起先止  5:句子完全重合
    '''
    assert len(index1) == 2 and len(index2) == 2
    if index1[0] >= index2[1]:
        return 0

    if index2[0] >= index1[1]:
        return 0

    if index1[0] == index2[0] and index1[1] == index2[1]:
        return 5

    if index1[0] >= index2[0] and index1[1] <= index2[1]:
        return 1

    if index2[0] >= index1[0] and index2[1] <= index1[1]:
        return 2

    if index1[0] <= index2[0] and index1[1] >= index2[0]:
        return 3

    if index2[0] <= index1[0] and index2[1] >= index1[0]:
        return 4

def jsondump_onelinejson(data, filepath, key_name=""):
    '''
    将一个字典中的value存储为一个字符串，单独成行，key 作为一个新元素 key_name 写入value
    '''
    import sys
    wfile = openwfile(filepath)
    for key in data:
        if key_name:
            ondatajson = data[key]
            if key_name in ondatajson:
                print("jsondump_onelinejson 保存关键字 %s 存在于json中，请更换关键字！", key_name)
                sys.exit(0)

            ondatajson[key_name] = key
            onedata = json.dumps(ondatajson, ensure_ascii=False)
        else:
            ondatajson = {}
            ondatajson[key] = data[key]
            onedata = json.dumps(ondatajson, ensure_ascii=False)

        wfile.write(onedata + "\n")
    wfile.close()

def jsonload_onelinejson(filepath, key_name=""):
    '''
    与上一个相反，如果每行元素中存在多个key， 则必须指定 key_name
    '''
    import sys
    rfile = openrfile(filepath)
    line = rfile.readline()
    rejson = {}
    while line:
        linetemp = line.strip()
        onedata = json.loads(linetemp)
        if key_name:
            if onedata[key_name] in rejson:
                print("jsonload_onelinejson 选取关键字 %s 不唯一，不能作为主键，请更换关键字！", key_name)
                sys.exit(0)
            rejson[onedata[key_name]] = onedata
        else:
            for key in onedata:
                rejson[key] = onedata[key]

        line = rfile.readline()
    rfile.close()
    return rejson

def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring

def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += chr(inside_code)
    return rstring

class NerTest(object):
    '''
    用于 NER 功能测试，包含两种指标：BIO SPAN
    '''
    def __init__(self):
        self.BIO = [0, 0, 0]
        self.SPAN = [0, 0, 0]
        self.BIO_label = {}
        self.SPAN_label = {}

    def clear(self):
        self.BIO = [0, 0, 0]
        self.SPAN = [0, 0, 0]
        self.BIO_label = {}
        self.SPAN_label = {}

    def add(self, b1, b2):
        b1[0] += b2[0]
        b1[1] += b2[1]
        b1[2] += b2[2]

    def get_SPAN_prf(self, yslist_bz, yslist_yc):
        '''
        :param yslist_bz: 准确列表 [[[0, 4], "BW"], [[4, 6], "ZXC"]]
        :param yslist2: 预测列表 [[[0, 4], "BW"], [[4, 6], "ZXC"]]
        :return: 按标签返回的：标注、预测、击中  的数量 {"BW":[[bz,pr,hit]], "ZXC":[[bz,pr,hit]]}
        '''

        SPAN_bz = self.get_label_SPAN(yslist_bz)
        SPAN_yc = self.get_label_SPAN(yslist_yc)
        redict = self.compare_SPAN(SPAN_bz, SPAN_yc)
        for label in redict:
            if label not in self.SPAN_label:
                self.SPAN_label[label] = [0,0,0]
            self.add(self.SPAN, redict[label])
            self.add(self.SPAN_label[label], redict[label])

        return redict

    def compare_SPAN(self,SPAN_bz, SPAN_yc):
        '''
        输入的格式为：{"BW":[[2,5],[7,9],……]}
        '''
        redict = {}
        for label in SPAN_bz:
            if label not in redict:
                redict[label] = [0,0,0]
            redict[label][0] += len(SPAN_bz[label])
            if label in SPAN_yc:
                redict[label][1] += len(SPAN_yc[label])

                for ys in SPAN_bz[label]:
                    if ys in SPAN_yc[label]:
                        redict[label][2] += 1

        for label in SPAN_yc:
            if label not in SPAN_bz:
                if label not in redict:
                    redict[label] = [0,0,0]
                redict[label][1] += len(SPAN_yc[label])

        return redict

    def get_label_SPAN(self, yslist):
        '''
        返回：{"BW":[[0，3]，[5,8],...], "ZXC":[]}
        '''
        redata = {}
        for ys in yslist:
            if ys[1] not in redata:
                redata[ys[1]] = []
            redata[ys[1]].append(ys[0])
        return redata

    def get_BIO_prf(self, yslist_bz, yslist_yc):
        '''
        :param yslist_bz: 准确列表 [[[0, 4], "BW"], [[4, 6], "ZXC"]]
        :param yslist2: 预测列表 [[[0, 4], "BW"], [[4, 6], "ZXC"]]
        :return: 按标签返回的：标注、预测、击中  的数量 {"BW":[[bz,pr,hit]], "ZXC":[[bz,pr,hit]]}
        '''

        yslist = yslist_bz + yslist_yc
        redict = {}
        indexs = [x[0][1] for x in yslist]
        if not indexs:
            return redict

        maxindex = max(indexs)
        labels = set([x[1] for x in yslist])

        for label in labels:
            redict[label] = self.compare_2list(self.get_label_BIO(yslist_bz, label, maxindex), self.get_label_BIO(yslist_yc, label, maxindex))
            if label not in self.BIO_label:
                self.BIO_label[label] = [0,0,0]
            self.add(self.BIO, redict[label])
            self.add(self.BIO_label[label], redict[label])
        return redict

    def get_label_BIO(self, yslist, label, maxindex):
        '''
        :param yslist: entities 格式 [[[0，5],label], [[8，9],label], [[12，56],label], …]
        :param label: 在yslist里提取指定的标签
        :return: 返回 BIO 形式
        '''
        relist = ["O"] * maxindex
        labelyslist = []
        for ys in yslist:
            if ys[1] == label:
                labelyslist.append(ys[0])
        self.list2BIO(relist, labelyslist)
        return relist

    def list2BIO(self, indexflag, yslist):
        '''
        将 【【0，5】，【8，9】，【12，56】...】 转换为 【‘B’，‘I’，‘I’，‘I’，‘I’，‘O’，‘O’，‘B’，‘I’，...】
        '''
        for scop in yslist:
            if indexflag[scop[0]] == 'O':
                indexflag[scop[0]] = 'B'

            for i in range(scop[0] + 1, scop[1]):
                if indexflag[i] == 'O':
                    indexflag[i] = 'I'

    def compare_2list(self, indexflag_bz, indexflag_yc):
        '''
        比较两个BIO列表
        :param indexflag_bz: 标注
        :param indexflag_yb: 预测
        :return: bz,pr,hit
        '''
        bz = 0
        pr = 0
        hit = 0
        assert len(indexflag_bz) == len(indexflag_yc)

        for i in range(len(indexflag_bz)):
            if indexflag_bz[i] != "O":
                bz += 1

            if indexflag_yc[i] != "O":
                pr += 1

                if indexflag_bz[i] == indexflag_yc[i]:
                    hit += 1

        return [bz,pr,hit]

    def show_BIO(self):
        '''
        展示预测性能
        '''
        for label in self.BIO_label:
            print(label, end="")
            self.calculate_pcf(self.BIO_label[label])
        self.calculate_pcf(self.BIO)

    def show_SPAN(self):
        '''
        展示预测性能
        '''
        for label in self.SPAN_label:
            print(label, end="")
            self.calculate_pcf(self.SPAN_label[label])
        self.calculate_pcf(self.SPAN)

    def calculate_pcf(self, bzprhit):
        bz = bzprhit[0]
        pr = bzprhit[1]
        hit= bzprhit[2]
        pre = 0
        cal = 0
        f1 = 0
        if bz != 0:
            cal = hit * 1.0 / bz

        if pr != 0:
            pre = hit * 1.0 / pr

        if cal + pre != 0:
            f1 = 2 * cal * pre / (cal + pre)
        print(
            "\t标注数：\t", bz,
            "\t预测数：\t", pr,
            "\t重合数：\t", hit,
            "\t准确率：\t", pre,
            "\t召回率：\t", cal,
            "\tf1值：\t", f1
        )
        return pre, cal, f1

def BIO2list(labellist):
    '''
    BIO 形式转换为 entities 形式
    :param labellist: [label-B ， label-I， ……]
    :return: 返回 entities 格式 [[[0，5],label], [[8，9],label], [[12，56],label], …]
    '''
    slabel = ""
    nstart = -1
    relist = []
    for i in range(len(labellist)):
        if labellist[i].endswith("B"):
            if slabel != "":
                relist.append([[nstart, i], slabel])
            nstart = i
            slabel = labellist[i][:-2]


        elif labellist[i].endswith("I"):
            if slabel == "":
                nstart = i
                slabel = labellist[i][:-2]
            continue

        else:
            if slabel != "":
                relist.append([[nstart, i], slabel])
                nstart = -1
                slabel = ""

    if slabel != "":
        relist.append([[nstart, len(labellist)], slabel])

    return relist

def calculate_pcf(bz,pr,hit):
    pre = 0
    cal = 0
    f1 = 0
    if bz != 0:
        cal = hit * 1.0 / bz

    if pr != 0:
        pre = hit * 1.0 / pr

    if cal + pre != 0:
        f1 = 2 * cal * pre / ( cal + pre )

    return pre,cal,f1

def testNER(rfilename, nertool):
    rfile = openrfile(rfilename)
    lines = rfile.readlines()
    rfile.close()

    datas = {}
    ss = []
    layer1 = []
    layer2 = []
    for line in lines:
        linetemp = line[:-1]
        if linetemp:
            chars = re.split("\t", linetemp)
            ss.append(chars[0])
            layer1.append(chars[1])
            layer2.append(chars[2])

        else:
            datas["".join(ss)] = BIO2list(layer1) + BIO2list(layer2)
            ss = []
            layer1 = []
            layer2 = []

    print(len(datas))
    testTEST = NerTest()
    bz0 = 0
    pr0 = 0
    hit0 = 0
    from tqdm import tqdm
    for ss in tqdm(datas):
        pre = nertool.parser(ss)['entities']
        bz = datas[ss]
        jieguo = testTEST.get_BIO_prf(pre, bz)
        for label in jieguo:
            bz0 += jieguo[label][0]
            pr0 += jieguo[label][1]
            hit0 += jieguo[label][2]
    print(calculate_pcf(bz0, pr0, hit0))

def do_gws(gewei_string):
   """ 个位数 """
   gewei2numb = {
      "一": 1,
      "二": 2,
      "三": 3,
      "四": 4,
      "五": 5,
      "六": 6,
      "七": 7,
      "八": 8,
      "九": 9,
      "十": 10
   }
   if gewei_string in gewei2numb:
      return gewei2numb[gewei_string]
   else:
      return gewei_string

def do_sws(sws_string):
   """ 十位数 """
   if sws_string[0] == "十" and sws_string[1] != "十":
      gws = do_gws(sws_string[1])
      return 10 + gws

   elif sws_string[0] != "十" and sws_string[1] == "十":
      sws = do_gws(sws_string[0])
      return sws * 10

   else:
      gws = do_gws(sws_string[1])
      sws = do_gws(sws_string[0])
      if abs(gws - sws) > 1:
         return sws_string
      else:
         return str(sws) + "-" + str(gws)

def do_sgs(sgs_string):
   """ 三个数 """
   if sgs_string[0] == "十":
      gws = do_gws(sgs_string[2])
      sws = do_gws(sgs_string[1])
      if abs(gws - sws) > 1:
         return sgs_string
      else:
         return str(10 + sws) + "-" + str(10 + gws)

   elif sgs_string[2] == "十":
      gws = do_gws(sgs_string[1])
      sws = do_gws(sgs_string[0])
      if abs(gws - sws) > 1:
         return sgs_string
      else:
         return str(10 * sws) + "-" + str(10 * gws)
   elif sgs_string[1] == "十":
      gws = do_gws(sgs_string[2])
      sws = do_gws(sgs_string[0])
      return 10 * sws + gws
   else:
         return sgs_string

def numb_pretreatment(numb_string):
   try:
      if len(numb_string) == 1:
         return str(do_gws(numb_string))
      elif len(numb_string) == 2:
         return str(do_sws(numb_string))
      elif len(numb_string) == 3:
         return str(do_sgs(numb_string))
      else:
         return numb_string
   except:
      return numb_string

def do_numb_pretreatment(report):
   """ 对句子当中的中文数字字符转换为阿拉伯字符  """
   ss = re.finditer("[一二三四五六七八九十]+", report)
   replace = []
   for x in ss:
      replace.append(((x.span()), numb_pretreatment(x.group())))

   reporttemp = ""
   indexend = 0
   for x in replace:
      reporttemp += report[indexend:x[0][0]] + x[1]
      indexend = x[0][1]

   reporttemp += report[indexend:len(report)]
   return reporttemp

def get_cpu_gpu_info(gpu_id: int, output_file: str) -> None:
    import pynvml
    import psutil
    import time
    import pandas as pd
    pynvml.nvmlInit() # 初始化
    # 获取GPU句柄
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
    # 获取GPU名称
    name=pynvml.nvmlDeviceGetName(handle)
    print('Device name: ', name, 'Gpu_id: ', gpu_id)
    while True:
        # 获取GPU运行进程信息
        process_list = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        # 当前GPU卡有运行进程
        if process_list:
            print('Find running process.')
            break
    output_data = {'time':[], 'cpu_mem_rss':[], 'cpu_mem':[], 'cpu_occupy':[],'gpu_men':[],'gpu_percent':[]}
    while True:
        print('Start watching')
        try:
            pid = process_list[0].pid
            # 捕捉Pid
            p = psutil.Process(pid)
            # CPU使用率
            cpu_percent = p.cpu_percent(None)
            time.sleep(1)
            # 记录时间
            output_data['time'].append(time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()))
            # 记录一秒间隔内的CPU使用率
            cpu_percent = p.cpu_percent(None)
            print('cpu_occupy: ', str(cpu_percent)+'%')
            output_data['cpu_occupy'].append(cpu_percent)
            
            # 内存使用
            cpu_mem_rss = p.memory_info().rss
            print('cpu_mem_rss: ', str(cpu_mem_rss))
            output_data['cpu_mem_rss'].append(cpu_mem_rss)

            # 获取内存使用率
            mem_percent = p.memory_percent()
            print('cpu_mem: ', str(round(mem_percent,4))+'%')
            output_data['cpu_mem'].append(round(mem_percent,4))
            
            # 获取GPU内存信息
            GPU_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            print('GPU显存占用率： ', str(round(GPU_info.used/GPU_info.total*100,4))+'%')
            output_data['gpu_percent'].append(round(GPU_info.used/GPU_info.total*100,4))
            print('GPU显存占用大小： ', str(round(GPU_info.used/1024**2, 4))+'MB')
            output_data['gpu_men'].append(round(GPU_info.used/1024**2, 4))
        except:
            print('Process finish')
            try:
                output_data_frame = pd.DataFrame(output_data)
                output_data_frame.to_csv(output_file, index=False)
            except:
                # 处理进程突然中止时，column长度不一致的情况
                min_len = min([len(output_data['time']), len(output_data['cpu_mem']),len(output_data['cpu_occupy']),len(output_data['gpu_men']),len(output_data['gpu_percent'])])
                output_data['time'] = output_data['time'][:min_len]
                output_data['cpu_mem'] = output_data['cpu_mem'][:min_len]
                output_data['cpu_mem_rss'] = output_data['cpu_mem_rss'][:min_len]
                output_data['cpu_occupy'] = output_data['cpu_occupy'][:min_len]
                output_data['gpu_men'] = output_data['gpu_men'][:min_len]
                output_data['gpu_percent'] = output_data['gpu_percent'][:min_len]
                output_data_frame = pd.DataFrame(output_data)
                output_data_frame.to_csv(output_file, index=False)
                # output_data_frame.to_excel('watch.xlsx', index=False)
            break
    print('Shutting down')
    pynvml.nvmlShutdown() # 最后要关闭管理工具
