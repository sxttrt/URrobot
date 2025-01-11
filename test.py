import pyaudio
import wave


class AudioRecorder:
    def __init__(self, output_filename="output.wav"):
        """初始化录音参数"""
        self.output_filename = output_filename
        self.chunk_size = 1024  # 每个数据块的大小
        self.sample_format = pyaudio.paInt16  # 音频格式（16位整数）
        self.channels = 1  # 单声道
        self.sample_rate = 44100  # 采样率 44.1kHz
        self.frames = []  # 存储录音数据
        self.p = pyaudio.PyAudio()  # 创建 PyAudio 对象
        self.stream = None  # 音频流

    def start_recording(self):
        """开始录音"""
        print("开始录音...请说话")
        self.frames = []  # 清空之前的录音数据
        self.stream = self.p.open(format=self.sample_format,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)

        # 录音过程
        while True:
            try:
                data = self.stream.read(self.chunk_size)
                self.frames.append(data)
            except KeyboardInterrupt:
                print("停止录音")
                break

    def save_recording(self):
        """保存录音到文件"""
        with wave.open(self.output_filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
        print(f"录音已保存为 {self.output_filename}")

    def stop_recording(self):
        """停止录音"""
        self.stream.stop_stream()
        self.stream.close()


if __name__ == "__main__":
    recorder = AudioRecorder(output_filename="output.wav")

    # 开始录音
    recorder.start_recording()

    # 停止录音并保存
    recorder.stop_recording()
    recorder.save_recording()
