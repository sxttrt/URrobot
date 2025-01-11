# -*- coding: utf-8 -*-

# 这是系统界面
import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk  # 使用 Pillow 加载和调整图片


class Login(object):
    def __init__(self):
        # 创建主窗口,用于容纳其它组件
        self.root = tkinter.Tk()
        # 给主窗口设置标题内容
        self.root.title("语音识别")
        self.root.geometry('450x300')  # 设置窗口大小

        # 创建画布
        self.canvas = tkinter.Canvas(self.root, height=200, width=500)

        # 使用 Pillow 加载 JPG 图片并调整大小
        try:
            image = Image.open('C:/Users/LCT/Desktop/URrobot/DTW/GIF.jpg')  # 加载 JPG 文件

            # 调整图片大小以适应画布
            max_width, max_height = 450, 180  # 设置最大宽度和高度
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # 按比例缩放图片

            self.image_file = ImageTk.PhotoImage(image)  # 转换为 Tkinter 可用格式
            self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)  # 将图片置于画布上
        except Exception as e:
            # 如果图片加载失败，显示提示信息
            messagebox.showerror("错误", f"无法加载图片：{e}")
            self.image_file = None

        self.canvas.pack(side='top')  # 放置画布（为上端）

        # 创建一个 `label` 名为 `检测结果: `
        self.label_result = tkinter.Label(self.root, text='检测结果: ')
        # 创建一个账号输入框,并设置尺寸
        self.output_result = tkinter.Entry(self.root, width=30)
        # 创建一个登录系统的按钮
        self.input_button = tkinter.Button(self.root, command=self.output_fu, text="录入语音", width=10)

    # 完成布局
    def gui_arrang(self):
        self.label_result.place(x=60, y=170)
        self.output_result.place(x=135, y=170)
        self.input_button.place(x=190, y=235)



def main():
    # 初始化对象
    L = Login()
    # 进行布局
    L.gui_arrang()
    # 主程序执行
    L.root.mainloop()  # 启动 Tkinter 主循环


if __name__ == '__main__':
    main()
