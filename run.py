import sys
import os
import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

# 添加 DTW 目录到 Python 的模块搜索路径
sys.path.append(r"C:\Users\LCT\Desktop\URrobot\DTW")
sys.path.append(os.path.join(os.getcwd(), "YOLOV8", "yolov8", "demo"))
sys.path.append(r"C:\Users\LCT\Desktop\URrobot\GRCNN")

from DTW.VoiceRecognition import VoiceRecognition
from picture_cut import YOLO_Detector
from real.realsenseD415 import Camera
from plane_grasp_real import  PlaneGraspClass

class GUI:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("语音识别与图像识别")
        self.root.geometry('500x350')  # 设置窗口大小

        # 创建画布
        self.canvas = tkinter.Canvas(self.root, height=180, width=450)

        # 创建默认图像
        self.image_file = None
        self.image = None
        self.image_path = None

        # 创建默认图像
        self.image_file = None
        self.image = None

        self.canvas.pack(side='top')  # 放置画布（为上端）

        # 创建文本框和按钮组件
        self.label_result = tkinter.Label(self.root, text='检测结果: ', font=('Arial', 12))
        self.output_result = tkinter.Entry(self.root, width=30, font=('Arial', 12))

        self.input_button = tkinter.Button(self.root, command=self.recognize_voice, text="录入语音", width=15,
                                           font=('Arial', 12))
        # self.image_button = tkinter.Button(self.root, command=self.detect_image, text="识别图像", width=15,
        #                                    font=('Arial', 12))

        # 初始化语音识别器
        self.voice_recognizer = VoiceRecognition()

        # YOLO 图像识别相关
        self.model_path = "C:/Users/LCT/Desktop/URrobot/YOLOV8/yolov8/runs/detect/train25/weights/best.pt"
        self.save_dir = "C:/Users/LCT/Desktop/URrobot/YOLOV8/yolov8-42/demo/images/cut_picture/"
        self.detector = YOLO_Detector(self.model_path)

        # 创建 RealSense 摄像头对象
        # self.camera = Camera()

    def recognize_voice(self):
        """调用语音识别功能"""
        matched_label = self.voice_recognizer.recognize_command()  # 获取语音识别结果
        if matched_label:
            self.output_result.delete(0, tkinter.END)  # 清空文本框
            self.output_result.insert(0, matched_label)  # 在文本框中显示识别结果
        else:
            self.output_result.delete(0, tkinter.END)
            self.output_result.insert(0, "未识别")

    # def detect_image(self):
    #     """调用图像识别功能，图像来自 RealSense 摄像头"""
    #     color_image, _ = self.camera.get_data()  # 只需要 RGB 图像
    #
    #     # 执行图像识别和裁剪
    #     self.detector.detect_and_crop_objects(color_image, self.save_dir)
    #     print("图像识别完成，裁剪的图像已保存到:", self.save_dir)
    #
    #     # 在画布上更新图像显示
    #     self.update_image_on_canvas(color_image)


    # def update_image_on_canvas(self, image):
    #     """将识别后的图像更新到 GUI 画布上"""
    #     try:
    #         # 将 OpenCV 图像转换为 PIL 图像
    #         pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #         pil_image.thumbnail((500, 180), Image.Resampling.LANCZOS)  # 按比例缩放图片
    #         self.image_file = ImageTk.PhotoImage(pil_image)  # 转换为 Tkinter 可用格式
    #         self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)  # 将图片置于画布上
    #     except Exception as e:
    #         messagebox.showerror("错误", f"无法更新图像：{e}")

    def gui_arrange(self):
        """完成界面布局"""
        # 调整控件位置，增加间距
        self.label_result.place(x=60, y=180)
        self.output_result.place(x=135, y=180)
        self.input_button.place(x=80, y=235)
        # self.image_button.place(x=240, y=235)

    def run(self):
        """启动 GUI"""
        self.gui_arrange()
        # # 自动进行图像识别和裁剪
        # self.detect_image()
        # 启动主循环
        self.root.mainloop()


# 运行GUI
if __name__ == "__main__":
    gui = GUI()
    gui.run()
