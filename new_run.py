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
from plane_grasp_real import PlaneGraspClass

class GUI:

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("语音识别与图像识别")
        self.root.geometry('500x350')  # 设置窗口大小

        # 创建画布
        self.canvas = tkinter.Canvas(self.root, height=300, width=450)

        # 创建默认图像
        self.image_file = None
        self.image = None
        self.image_path = None

        self.plane_grasp = PlaneGraspClass(
            saved_model_path="C:/Users/LCT/Desktop/URrobot/GRCNN/trained-models/jacquard-rgbd-grconvnet3-drop0-ch32/epoch_48_iou_0.93",
            visualize=True,
            include_rgb=True,
            include_depth=True,
            output_width=640,
            output_height=480,
            pos = []
        )

        self.canvas.pack(side='top')  # 放置画布（为上端）

        # 创建文本框和按钮组件
        self.label_result = tkinter.Label(self.root, text='检测结果: ', font=('Arial', 12))
        self.output_result = tkinter.Entry(self.root, width=30, font=('Arial', 12))

        self.input_button = tkinter.Button(self.root, command=self.recognize_voice, text="录入语音", width=15,
                                           font=('Arial', 12))
        self.image_button = tkinter.Button(self.root, command=self.detect_image, text="识别图像", width=15,
                                           font=('Arial', 12))

        # 创建按钮来触发按标签过滤图像识别
        self.filter_button = tkinter.Button(self.root, command=self.recognize_and_detect, text="按标签筛选",
                                            width=15,
                                            font=('Arial', 12))

        # 创建新按钮，用于语音识别并执行抓取
        self.grasp_button = tkinter.Button(self.root, command=self.recognize_and_grasp, text="语音抓取", width=15,
                                           font=('Arial', 12))

        # 初始化语音识别器
        self.voice_recognizer = VoiceRecognition()

        # YOLO 图像识别相关
        self.model_path = "C:/Users/LCT/Desktop/URrobot/YOLOV8/yolov8/demo/runs/detect/train16/weights/best.pt"
        self.save_dir = "C:/Users/LCT/Desktop/URrobot/images/cut_picture"
        self.detector = YOLO_Detector(self.model_path)

        # 创建 RealSense 摄像头对象
        self.camera = Camera()

        self.label_mapping = {
            "锤子": "hammer",
            "扳手": "wrench",
            "钳子": "plier",
            "螺丝刀": "screwdriver",
            "卷尺": "tape_measure"
        }

        # 存储语音识别后的标签
        self.detected_tag = None

    def recognize_voice(self):
        """调用语音识别功能"""
        matched_label = self.voice_recognizer.recognize_command()  # 获取语音识别结果
        if matched_label:
            self.detected_tag = matched_label  # 存储识别出的标签
            self.output_result.delete(0, tkinter.END)  # 清空文本框
            self.output_result.insert(0, matched_label)  # 在文本框中显示识别结果
        else:
            self.detected_tag = None
            self.output_result.delete(0, tkinter.END)
            self.output_result.insert(0, "未识别")

    def detect_image(self):
        """调用图像识别功能，图像来自 RealSense 摄像头"""
        # 从 RealSense 获取 RGB 和深度图像
        color_image, _ = self.camera.get_data()  # 只需要 RGB 图像

        # 执行图像识别和裁剪
        self.detector.detect_and_crop_objects(color_image, self.save_dir)
        print("图像识别完成，裁剪的图像已保存到:", self.save_dir)

        # 在画布上更新图像显示
        self.update_image_on_canvas(color_image)

    def recognize_and_detect(self):
        """先进行语音识别，再进行图像识别和裁剪"""
        # 步骤1: 调用语音识别功能获取标签
        matched_label = self.voice_recognizer.recognize_command()  # 获取语音识别结果
        #matched_label = "钳子" # "锤子" "扳手" "螺丝刀" "钳子" "卷尺"
        if matched_label:
            self.detected_tag = matched_label  # 存储识别出的标签
            self.output_result.delete(0, tkinter.END)  # 清空文本框
            self.output_result.insert(0, matched_label)  # 在文本框中显示识别结果
            self.detected_tag = self.label_mapping.get(matched_label, None)
            print(self.detected_tag)
            # 步骤2: 获取RGB图像进行识别和裁剪
            color_image, _ = self.camera.get_data()  # 获取RealSense摄像头的RGB图像

            # 执行物体识别
            results = self.detector.detect_objects(color_image)

            # 步骤3: 使用crop_and_filter_objects筛选物体并裁剪
            crops, positions, sizes, labels_and_confs = self.detector.crop_and_filter_objects(color_image, results)

            # 步骤4: 打印检测到的物体信息
            for i, label_and_conf in enumerate(labels_and_confs):
                label, confidence = label_and_conf
                if label == self.detected_tag:
                    x1, y1, x2, y2 = positions[i]
                    # 打印检测信息
                    print(f"检测到物体: {label}, 置信度: {confidence:.2f}")
                    print(f"位置: {x1, y1, x2, y2}")
                    print(f"尺寸: {sizes[i][0]}x{sizes[i][1]} (宽度: {sizes[i][0]}, 高度: {sizes[i][1]})")

                    cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 红色框 (0, 0, 255)

            # 步骤5: 使用 OpenCV 显示图像
            cv2.imshow("Detected Image", color_image)  # 显示图像

            # 步骤6: 等待用户按下任意键关闭窗口
            cv2.waitKey(0)  # 按下任意键关闭窗口
            cv2.destroyAllWindows()  # 关闭所有 OpenCV 窗口
            # 步骤5: 更新画布上显示的图像
            self.update_image_on_canvas(color_image)


    def recognize_and_grasp(self):
        try:
           # matched_label = self.voice_recognizer.recognize_command()  # 获取语音识别结果
            matched_label = "螺丝刀"  # "锤子" "扳手" "螺丝刀" "钳子" "卷尺"
            if matched_label:
                self.detected_tag = matched_label
                self.output_result.delete(0, tkinter.END)
                self.output_result.insert(0, matched_label)
                self.detected_tag = self.label_mapping.get(matched_label, None)
                print(self.detected_tag)

                if self.detected_tag == "hammer":
                   close_position = 11000
                   force = 100
                   more_size_x = 20
                   more_size_y = 0
                elif self.detected_tag == "wrench":
                    close_position = 10500
                    force = 70
                    more_size_x = 20
                    more_size_y = 0
                elif self.detected_tag == "plier":
                    close_position = 11000
                    force = 70
                    more_size_x = 20
                    more_size_y = 0
                elif self.detected_tag == "screwdriver":
                    close_position = 12000
                    force = 40
                    more_size_x = 20
                    more_size_y = 0
                elif self.detected_tag == "tape_measure":
                    close_position = 6000
                    force = 30
                    more_size_x = 30
                    more_size_y =30
                else:
                    print("Unknown tag")
                    close_position = 0
                    force = 0
                    more_size_x = 20
                    more_size_y = 0

                color_image, depth_img = self.camera.get_data()  # 获取RealSense摄像头的RGB图像
                # 执行物体识别
                results = self.detector.detect_objects(color_image)

                crops, positions, sizes, labels_and_confs = self.detector.crop_and_filter_objects(color_image, results)

                pos = self.plane_grasp.pos

                # 步骤4: 打印检测到的物体信息
                for i, label_and_conf in enumerate(labels_and_confs):
                    label, confidence = label_and_conf
                    if label == self.detected_tag:
                        pos= positions[i]
                if pos:
                    print(f"匹配的抓取区域: {pos}")
                    self.plane_grasp.flag = 1
                    self.plane_grasp.pos = pos

                    result = self.plane_grasp.generate(color_image,depth_img,close_position,force,more_size_x,more_size_y)
                    if result:
                        messagebox.showinfo("成功", "抓取成功！")
                    else:
                        raise Exception("抓取失败，生成的抓取点无效！")
                else:
                    raise Exception(f"未找到匹配标签 {matched_label} 的物体框！")

        except Exception as e:
            messagebox.showerror("错误", str(e))
            print(f"抓取过程出错: {e}")

    def update_image_on_canvas(self, image):
        """将识别后的图像更新到 GUI 画布上"""
        try:
            # 将 OpenCV 图像转换为 PIL 图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            pil_image.thumbnail((400, 180), Image.Resampling.LANCZOS)  # 按比例缩放图片
            self.image_file = ImageTk.PhotoImage(pil_image)  # 转换为 Tkinter 可用格式
            self.image = self.canvas.create_image(100, 0, anchor='nw', image=self.image_file)  # 将图片置于画布上
        except Exception as e:
            messagebox.showerror("错误", f"无法更新图像：{e}")
    def gui_arrange(self):
        """完成界面布局"""
        # 调整控件位置，增加间距
        self.label_result.place(x=60, y=180)
        self.output_result.place(x=135, y=180)
        self.input_button.place(x=80, y=235)
        self.image_button.place(x=240, y=235)
        self.filter_button.place(x=80, y=270)
        self.grasp_button.place(x=240, y=270)

    def run(self):
        """启动 GUI"""
        self.gui_arrange()
        # 自动进行图像识别和裁剪
        self.detect_image()
        # 启动主循环
        self.root.mainloop()


# 运行GUI
if __name__ == "__main__":
    gui = GUI()
    gui.run()
