import wave
import os
import numpy as np
from struct import unpack
import pyaudio
from DTW.endpointDetection import EndPointDetect

# 全局参数
framerate = 16000  # 采样频率
channels = 1       # 声道数
sampwidth = 2      # 采样字节
CHUNK = 1024       # 录音块大小
RATE = 16000       # 采样频率
RECORD_SECONDS = 2.5  # 录音时长

class VoiceRecognition:
    def __init__(self):
        self.commands = ["锤子", "扳手", "螺丝刀", "钳子", "卷尺"]
        self.mfcc_path = "C:/Users/LCT/Desktop/URrobot/DTW/MFCC-EndPointedVoice/"


    def save_wave_file(self, filename, data):
        """保存语音数据为 WAV 文件"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(framerate)
            wf.writeframes(b"".join(data))

    def getMFCC(self):
        """加载MFCC特征文件"""
        MFCC = []
        for i in range(5):
            MFCC_rows = []
            for j in range(6):
                with open(f"{self.mfcc_path}{i + 1}-{j + 1}.mfc", "rb") as f:
                    nframes = unpack(">i", f.read(4))[0]
                    frate = unpack(">i", f.read(4))[0]
                    nbytes = unpack(">h", f.read(2))[0]
                    feakind = unpack(">h", f.read(2))[0]
                    ndim = nbytes // 4
                    feature = [
                        [unpack(">f", f.read(4))[0] for _ in range(ndim)]
                        for _ in range(nframes)
                    ]
                    MFCC_rows.append(feature)
            MFCC.append(MFCC_rows)
        return MFCC

    def getMFCCModels(self, MFCC):
        """提取模板命令的 MFCC 特征并创建标签"""
        MFCC_models = []
        labels = []
        for i, command in enumerate(self.commands):
            for j in range(6):
                MFCC_models.append(MFCC[i][j])
                labels.append(command)
        return MFCC_models, labels

    def dtw(self, M1, M2):
        """DTW 动态时间规整算法"""
        M1_len, M2_len = len(M1), len(M2)
        cost = [[0] * M2_len for _ in range(M1_len)]
        dis = [[self.distance(M1[i], M2[j]) for j in range(M2_len)] for i in range(M1_len)]

        cost[0][0] = dis[0][0]
        for i in range(1, M1_len):
            cost[i][0] = cost[i - 1][0] + dis[i][0]
        for j in range(1, M2_len):
            cost[0][j] = cost[0][j - 1] + dis[0][j]

        for i in range(1, M1_len):
            for j in range(1, M2_len):
                cost[i][j] = min(
                    cost[i - 1][j] + dis[i][j],
                    cost[i - 1][j - 1] + dis[i][j] * 2,
                    cost[i][j - 1] + dis[i][j]
                )
        return cost[M1_len - 1][M2_len - 1]

    def distance(self, x1, x2):
        """计算两个向量之间的距离"""
        return sum(abs(a - b) for a, b in zip(x1, x2))

    def getMFCCRecorded(self):
        """从文件中读取实时录制的语音 MFCC 特征"""
        with open("C:/Users/LCT/Desktop/URrobot/DTW/MFCC-RealTimeRecordedVoice/recordedVoice.mfc", "rb") as f:
            nframes = unpack(">i", f.read(4))[0]
            frate = unpack(">i", f.read(4))[0]
            nbytes = unpack(">h", f.read(2))[0]
            feakind = unpack(">h", f.read(2))[0]
            ndim = nbytes // 4
            feature = [
                [unpack(">f", f.read(4))[0] for _ in range(ndim)]
                for _ in range(nframes)
            ]
        return feature

    def recognize_command(self):
        """进行语音识别并返回匹配的命令"""
        # 录制语音
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=framerate, input=True,
                         frames_per_buffer=CHUNK)
        print("开始录音,请说话......")
        frames = [stream.read(CHUNK) for _ in range(int(RATE / CHUNK * RECORD_SECONDS))]
        print("录音结束,请停止说话!!!")
        stream.stop_stream()
        stream.close()
        pa.terminate()

        # 保存录音文件
        self.save_wave_file("C:/Users/LCT/Desktop/URrobot/DTW/RecordedVoice-RealTime/recordedVoice_before.wav", frames)

        # 端点检测
        with wave.open("C:/Users/LCT/Desktop/URrobot/DTW/RecordedVoice-RealTime/recordedVoice_before.wav", "rb") as f:
            wave_data = np.frombuffer(f.readframes(f.getnframes()), dtype=np.short)
        end_point_detect = EndPointDetect(wave_data)

        # 存储端点检测后的语音
        N = end_point_detect.wave_data_detected
        for m in range(0, len(N), 2):
            self.save_wave_file("C:/Users/LCT/Desktop/URrobot/DTW/RecordedVoice-RealTime/recordedVoice_after.wav", wave_data[N[m] * 256:N[m + 1] * 256])

        os.chdir("C:\\Users\\LCT\\Desktop\\URrobot\\DTW\\HTK-RealTimeRecordedVoice")
        os.system("hcopy -A -D -T 1 -C tr_wav.cfg -S .\list.scp")
        os.chdir("C:\\Users\\LCT\\Desktop\\URrobot\\DTW")

        # 获取 MFCC 特征并进行识别
        MFCC_recorded = self.getMFCCRecorded()
        MFCC_models, labels = self.getMFCCModels(self.getMFCC())

        # 进行匹配
        distances = {}
        for model, label in zip(MFCC_models, labels):
            dis = self.dtw(MFCC_recorded, model)
            distances[label] = dis

        # 找到最小距离
        matched_label = min(distances, key=distances.get)
        min_distance = distances[matched_label]

        print("匹配距离:")
        for label, distance in distances.items():
            print(f"{label}: {distance}")

        print(f"最终匹配结果: {matched_label}, 最小距离: {min_distance}")

        return matched_label

