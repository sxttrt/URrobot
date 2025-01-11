import tkinter as tk
from tkinter import messagebox
from DTW.VoiceRecognition import VoiceRecognition  # 确保 VoiceRecognition 类的路径正确

class VoiceRecognitionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("语音识别")
        self.root.geometry('400x200')  # 设置窗口大小

        # 创建标签显示语音识别结果
        self.label_result = tk.Label(self.root, text='检测结果: ', font=('Arial', 12))
        self.label_result.pack(pady=20)

        # 创建文本框来显示识别的文本
        self.output_result = tk.Entry(self.root, width=30, font=('Arial', 12))
        self.output_result.pack()

        # 创建按钮来触发语音识别
        self.recognize_button = tk.Button(self.root, text="开始语音识别", command=self.recognize_voice, width=20, font=('Arial', 12))
        self.recognize_button.pack(pady=20)

        # 初始化语音识别器
        self.voice_recognizer = VoiceRecognition()

    def recognize_voice(self):
        """调用语音识别功能"""
        try:
            matched_label = self.voice_recognizer.recognize_command()  # 获取语音识别结果
            if matched_label:
                self.output_result.delete(0, tk.END)  # 清空文本框
                self.output_result.insert(0, matched_label)  # 显示识别结果
            else:
                self.output_result.delete(0, tk.END)
                self.output_result.insert(0, "未识别")  # 如果未识别到任何内容
        except Exception as e:
            messagebox.showerror("错误", f"语音识别出错: {e}")

    def run(self):
        """启动 GUI"""
        self.root.mainloop()

# 运行 GUI
if __name__ == "__main__":
    gui = VoiceRecognitionGUI()
    gui.run()
