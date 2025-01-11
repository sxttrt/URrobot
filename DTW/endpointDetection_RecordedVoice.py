# -*- coding: utf-8 -*-
import wave
import os
import numpy as np
from endpointDetection import EndPointDetect

# 存储成 wav 文件的参数
framerate = 16000  # 采样频率 8000 or 16000
channels = 1       # 声道数
sampwidth = 2      # 采样字节 1 or 2

# 检查和创建目录
output_dir = "./RecordedVoice-EndPointed/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# 将语音文件存储成 wav 格式
def save_wave_file(filename, data):
    try:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)   # 声道
        wf.setsampwidth(sampwidth)  # 采样字节 1 or 2
        wf.setframerate(framerate)  # 采样频率 8000 or 16000
        wf.writeframes(b"".join(data))
        wf.close()
      #  print(f"File saved: {filename}")
    except Exception as e:
        print(f"Error saving file {filename}: {e}")

# 处理多个音频文件
for i in range(5):
    for j in range(6):
        try:
            # 打开输入文件
            input_filename = f"./RecordedVoice/{i + 1}-{j + 1}.wav"
            f = wave.open(input_filename, "rb")
           # print(f"Processing file: {input_filename}")
            
            # 获取音频文件参数
            params = f.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            
            # 读取音频数据
            str_data = f.readframes(nframes)
            f.close()
            
            # 根据采样字节数确定数据类型
            if sampwidth == 1:
                dtype = np.uint8  # 8位音频
            elif sampwidth == 2:
                dtype = np.int16  # 16位音频
            else:
                raise ValueError("Unsupported sample width")
            
            # 将二进制数据转换为 numpy 数组
            wave_data = np.frombuffer(str_data, dtype=dtype)
            print(f"采样点数目：{len(wave_data)}")
            
            # 端点检测
            end_point_detect = EndPointDetect(wave_data)
            N = end_point_detect.wave_data_detected
            
            # 调试输出 N 的值，确保合理
            print(f"N values for file {i + 1}-{j + 1}: {N}")
            
            # 保存端点检测后的音频片段
            m = 0
            while m < len(N) - 1:
                output_filename = f"{output_dir}{i + 1}-{j + 1}.wav"
                save_wave_file(output_filename, wave_data[N[m] * 256: (N[m+1] + 5) * 256])
                m = m + 2
        
        except wave.Error as e:
            print(f"Error processing file {i + 1}-{j + 1}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {i + 1}-{j + 1}: {e}")

# 利用 HCopy 工具对录取的语音进行 MFCC 特征提取
try:
    os.chdir("C:\\Users\\LCT\\Desktop\\URrobot\\DTW\\HTK-EndPointedVoice")
    os.system("hcopy -A -D -T 1 -C tr_wav.cfg -S .\\list.scp")
    os.chdir("C:\\Users\\LCT\\Desktop\\Language-Recognition-System-master\\DTW")
except Exception as e:
    print(f"Error during HCopy execution: {e}")
