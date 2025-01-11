import pyaudio
import wave

# 音频参数
FORMAT = pyaudio.paInt16  # 16位采样
CHANNELS = 1              # 单声道
RATE = 16000              # 采样率 16000 Hz
CHUNK = 1024              # 每次录制的帧数
RECORD_SECONDS = 2        # 录音时长为2秒
OUTPUT_FILENAME = "5-6.wav"  # 输出文件名

# 初始化pyaudio
audio = pyaudio.PyAudio()

# 开始录音
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

print("开始录音...")

frames = []

# 录制2秒的音频
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("录音结束.")

# 停止录音
stream.stop_stream()
stream.close()
audio.terminate()

# 保存为WAV文件
wf = wave.open(OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"音频已保存为 {OUTPUT_FILENAME}")
