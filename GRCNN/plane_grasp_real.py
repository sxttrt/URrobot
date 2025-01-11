import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import time

import matplotlib.pyplot as plt
import numpy as np
import torch
import  cv2
from UR_Robot import UR_Robot
from inference.post_process import post_process_output
from utils.data.camera_data import CameraData
from utils.dataset_processing.grasp import detect_grasps
from utils.visualisation.plot import plot_grasp
import cv2
from PIL import Image
import torchvision.transforms as transforms


class PlaneGraspClass:
    def __init__(self, saved_model_path=None,use_cuda=True,visualize=False,include_rgb=True,include_depth=True,output_width=400,output_height=400,flag =True,pos =[]):
        if saved_model_path==None:
            saved_model_path = "C:/Users/LCT/Desktop/URrobot/GRCNN/trained-models/jacquard-rgbd-grconvnet3-drop0-ch32/epoch_48_iou_0.93"
        self.model = torch.load(saved_model_path)
        self.device = "cuda:0" if use_cuda else "cpu"
        self.visualize = visualize
        self.flag = flag
        self.pos = pos
        self.output_width = output_width
        self.output_height = output_height

        self.cam_data = CameraData(include_rgb=include_rgb,include_depth=include_depth,output_width=output_width,output_height=output_height)

        self.ur_robot = UR_Robot(robot_ip="192.168.1.35", gripper_port ='COM6', gripper_baudrate=115200, gripper_address=1,
                            workspace_limits=None, is_use_robot=True, is_use_camera=True)
        self.cam_pose = self.ur_robot.cam_pose
        self.intrinsic = self.ur_robot.cam_intrinsics
        self.cam_depth_scale = self.ur_robot.cam_depth_scale
        if self.visualize:
            self.fig = plt.figure(figsize=(6, 6))
        else:
            self.fig = None

    def generate(self,rgb,depth,close_position,force,more_size_x,more_size_y):
        #Get RGB-D image from camera
        # rgb, depth= self.ur_robot.get_camera_data() # meter
        save_rgb =rgb
        depth = depth *self.cam_depth_scale
        depth[depth >1.2]=0 # distance > 1.2m ,remove it

        ## if you don't have realsense camera, use me
        # num =4 # change me num=[1:6],and you can see the result in '/result' file
        # rgb_path = f"./cmp{num}.png"
        # depth_path = f"./hmp{num}.png"
        # rgb = np.array(Image.open(rgb_path))
        # depth = np.array(Image.open(depth_path)).astype(np.float32)
        # depth = depth * self.cam_depth_scale
        # depth[depth > 1.2] = 0  # distance > 1.2m ,remove it

        depth= np.expand_dims(depth, axis=2)
        x, depth_img, rgb_img = self.cam_data.get_data(rgb=rgb, depth=depth)
        rgb = cv2.cvtColor(rgb,cv2.COLOR_BGR2RGB)

        with torch.no_grad():
            xc = x.to(self.device)
            pred = self.model.predict(xc)
        q_img, ang_img, width_img = post_process_output(pred['pos'], pred['cos'], pred['sin'], pred['width'])

        self.pos = self.transform_pos_to_cropped(self.pos, self.cam_data.top_left, self.output_width,
                                                 self.output_height)
        print("pos:")
        print(self.pos)

        # rgb_img_cropped = save_rgb[self.pos[1]-20:self.pos[3]+20, self.pos[0]-20:self.pos[2]+20]  # 从RGB图像中裁剪指定区域
        # cv2.imshow('Cropped Image', rgb_img_cropped)  # 显示裁剪后的图像
        # cv2.waitKey(0)  # 等待按键事件，按任意键关闭图像窗口
        # cv2.destroyAllWindows()
        print('flag:' + str(self.flag))
        grasps = detect_grasps(q_img = q_img, ang_img = ang_img, width_img =width_img,flag=self.flag,pos=self.pos,more_size_x= more_size_x,more_size_y=more_size_y)
        print(("x y"))
        print(grasps[0].center[1])
        print(grasps[0].center[0])
        # print(len(grasps))
        if len(grasps) ==0:
            print("Detect 0 grasp pose!")
            if self.visualize:
                plot_grasp(fig=self.fig, rgb_img=self.cam_data.get_rgb(rgb, False), grasps=grasps, save=True)
            return False
        ## For real UR robot
        # Get grasp position from model output
        pos_z = depth[grasps[0].center[0] + self.cam_data.top_left[0], grasps[0].center[1] + self.cam_data.top_left[1]]
        pos_x = np.multiply(grasps[0].center[1] + self.cam_data.top_left[1] - self.intrinsic[0][2]  + self.pos[0],
                             pos_z / self.intrinsic[0][0])
        pos_y = np.multiply(grasps[0].center[0] + self.cam_data.top_left[0] - self.intrinsic[1][2] + self.pos[1],
                             pos_z / self.intrinsic[1][1])
        # if pos_z == 0:
        #         #      print("False")
        #         #      return False
        #
        target = np.asarray([pos_x, pos_y, pos_z])
        target.shape = (3, 1)
        #
        # # Convert camera to robot coordinates
        camera2robot = self.cam_pose
        target_position = np.dot(camera2robot[0:3, 0:3], target) + camera2robot[0:3, 3:]
        target_position = target_position[0:3, 0]
        
        # Convert camera to robot angle
        angle = np.asarray([0, 0, grasps[0].angle])
        angle.shape = (3, 1)
        target_angle = np.dot(camera2robot[0:3, 0:3], angle)
        
        print("target_angle:",target_angle[2][0])
        rx,ry = self.ur_robot.angle_to_cartesian( target_angle[2][0])

        # compute gripper width
        width = grasps[0].length # mm
        max_grasp_width = 12000 
        max_width = 120 # mm 
  
        grasp_width =max_grasp_width - (width/10 - 0.0485)/0.00105
        grasp_width = int(grasp_width)
        
        #z_drop = (-1.6883e-8 * (12000-grasp_width)**2 - 6.004e-5 * (12000-grasp_width )+ 3.2505) * 0.01
        
        print("grasp_width:",width)

        # if width < 25:    # detect error
        #     width = 70
        # elif width <40:
        #     width =45
        # elif width > 85:
        #     width = 85
        
        # Concatenate grasp pose with grasp angle
        grasp_pose = np.append(target_position, target_angle[2])
        print(grasp_pose[2])
        # grasp_pose[2]  = grasp_pose[2] + z_drop
        grasp_pose[2] = 0.003
        print('grasp_pose: ', grasp_pose)
        print('grasp_width: ',grasps[0].length)
   

        #调用抓取
        # self.ur_robot.grasp([grasp_pose[0],grasp_pose[1],grasp_pose[2]], angle=grasp_pose[3], close_position=close_position,force=force)
        
        #self.ur_robot.grasp([-0.35,-0.3,0.1-0.005], angle=-1.57, close_position=5000)

        # if self.visualize
        #     plot_grasp(fig=self.fig, rgb_img=self.cam_data.get_rgb(rgb, False), grasps=grasps, save=True)
        #     time.sleep(3)
        return True

    def transform_pos_to_cropped(self,pos, top_left, output_width, output_height):
        """
        将原图上的物体框坐标转换为裁剪后图像中的坐标
        :param pos: 形状为 [x1, y1, x2, y2] 的数组，表示一个物体框
        :param top_left: 裁剪区域左上角坐标 (top, left)
        :param output_width: 裁剪后图像的宽度
        :param output_height: 裁剪后图像的高度
        :return: 转换后的坐标 [new_x1, new_y1, new_x2, new_y2]
        """
        top, left = top_left

        x1, y1, x2, y2 = pos
        # 将坐标转换为裁剪图像的坐标系
        new_x1 = max(x1 - left, 0)  # 防止越界
        new_y1 = max(y1 - top, 0)  # 防止越界
        new_x2 = min(x2 - left, output_width)  # 防止越界
        new_y2 = min(y2 - top, output_height)  # 防止越界


        # 返回转换后的坐标
        return [new_x1, new_y1, new_x2, new_y2]



if __name__ == '__main__':
    g = PlaneGraspClass(
        saved_model_path="C:/Users/LCT/Desktop/URrobot/GRCNN/trained-models/jacquard-rgbd-grconvnet3-drop0-ch32/epoch_48_iou_0.93",
        visualize=True,
        include_rgb=True
    )
    g.generate()
