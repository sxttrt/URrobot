import os
from pydub import AudioSegment

# 指定 MP3 文件所在的文件夹路径
folder_path = "./sound"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith(".mp3"):
        # 获取完整的文件路径
        mp3_path = os.path.join(folder_path, filename)
        
        # 加载 MP3 文件
        audio = AudioSegment.from_mp3(mp3_path)
        
        # 将 .mp3 替换为 .wav 作为输出文件名
        wav_filename = filename.replace(".mp3", ".wav")
        wav_path = os.path.join(folder_path, wav_filename)
        
        # 导出为 WAV 格式
        audio.export(wav_path, format="wav")
        
        print(f"已成功将 {mp3_path} 转换为 {wav_path}")

print("所有 MP3 文件转换完毕！")
