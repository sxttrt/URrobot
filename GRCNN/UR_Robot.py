import time
import rtde_control
import rtde_receive
import minimalmodbus
import copy
import numpy as np
import threading
import math

from real.realsenseD415 import Camera

POSITION_HIGH_8 = 0x0102  # 位置寄存器高八位
POSITION_LOW_8 = 0x0103  # 位置寄存器低八位
SPEED = 0x0104
FORCE = 0x0105
MOTION_TRIGGER = 0x0108

lock = threading.Lock()

class UR_Robot:
    def __init__(self, robot_ip="192.168.1.35", gripper_port ='COM6', gripper_baudrate=115200, gripper_address=1,
                 workspace_limits=None, is_use_robot=True, is_use_camera=True):
        if workspace_limits is None:
            # workspace_limits = [[-0.45, -0.30], [-0.5, 0.5], [0.05, 0.15]]
            workspace_limits = [[-0.30, -0.15], [-0.50, 0.05], [0.002, 0.15]]
        self.workspace_limits = workspace_limits
        self.rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        self.rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        self.instrument = minimalmodbus.Instrument(gripper_port, gripper_address)
        self.instrument.serial.baudrate = gripper_baudrate
        self.instrument.serial.timeout = 1
        self.is_use_robotiq85 = is_use_robot
        self.is_use_camera = is_use_camera


        self.joint_acc = 0.2  
        self.joint_spd = 0.2  

        self.tool_acc = 0.1  
        self.tool_spd = 0.1 
        self.tool_pose_tolerance = [0.002, 0.002, 0.002, 0.01, 0.01, 0.01]
        self.joint_tolerance = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01]

        # self.home_joint_config = [-(0 / 360.0) * 2 * np.pi, -(90 / 360.0) * 2 * np.pi,
        #                      (0 / 360.0) * 2 * np.pi, -(90 / 360.0) * 2 * np.pi,
        #                      -(0 / 360.0) * 2 * np.pi, 0.0]
        self.initial_pose = [-0.4, -0.025, 0.14981, 0.000, 3.141, 0.000]

        if(self.is_use_camera):
            # Fetch RGB-D data from RealSense camera
            self.camera = Camera()
            self.cam_intrinsics = np.array([386.89120483,0,321.61746216,0,386.45446777,237.19995117,0,0,1]).reshape(3,3)
            # Load camera pose (from running calibrate.py), intrinsics and depth scale
        self.cam_pose = np.loadtxt("C:/Users/LCT/Desktop/URrobot/GRCNN/real/cam_pose/camera_pose.txt", delimiter=' ')
        self.cam_depth_scale = np.loadtxt("C:/Users/LCT/Desktop/URrobot/GRCNN/real/cam_pose/camera_depth_scale.txt", delimiter=' ')
        
# Define the robot control class
    def moveL(self, target_pose, speed=0.1, acceleration=0.1):
        self.rtde_c.moveL(target_pose, speed, acceleration)
        actual_tool_positions = self.get_actual_tcp_pose()
        while not all([np.abs(actual_tool_positions[j] - target_pose[j]) < self.tool_pose_tolerance[j] for j in range(3)]):
            actual_tool_positions = self.get_actual_tcp_pose()
            time.sleep(0.01)
        time.sleep(1.5)  

    def moveJ(self, target_joint, speed=0.2, acceleration=0.2):
        self.rtde_c.moveJ(target_joint, speed, acceleration)
        actual_joint_positions = self.get_actual_joint_position()
        while not all([np.abs(actual_joint_positions[j] - target_joint[j]) < self.joint_tolerance[j] for j in range(len(target_joint))]):
            actual_joint_positions = self.get_actual_joint_position()
            time.sleep(0.01)
        time.sleep(1.5)

    def go_home(self):
        self.move_j(self.home_joint_config)

    def get_actual_tcp_pose(self):
        return self.rtde_r.getActualTCPPose()

    def get_actual_joint_position(self):
        return self.rtde_r.getActualQ()

    def get_robot_status(self):
        return self.rtde_r.getRobotStatus()
    

# Define the gripper control class
    def write_position_high8(self, value):
        with lock:
            self.instrument.write_register(POSITION_HIGH_8, value, functioncode=6)

    def write_position_low8(self, value):
        with lock:
            self.instrument.write_register(POSITION_LOW_8, value, functioncode=6)

    def write_position(self, value):
        with lock:
            self.instrument.write_long(POSITION_HIGH_8, value)

    def write_speed(self, speed):
        with lock:
            self.instrument.write_register(SPEED, speed, functioncode=6)

    def write_force(self, force):
        with lock:
            self.instrument.write_register(FORCE, force, functioncode=6)

    def trigger_motion(self):
        with lock:
            self.instrument.write_register(MOTION_TRIGGER, 1, functioncode=6)

    def read_position(self):
        with lock:
            high = self.instrument.read_register(POSITION_HIGH_8, functioncode=3)
            low = self.instrument.read_register(POSITION_LOW_8, functioncode=3)
            position = (high << 8) | low
            return position

    def grip(self, position, speed, force):
        self.write_position(position)
        self.write_speed(speed)
        self.write_force(force)
        self.trigger_motion()
        time.sleep(2)
        return self.read_position()
    

    ## get camera data
    def get_camera_data(self):
        color_img, depth_img = self.camera.get_data()
        return color_img, depth_img
    
    def angle_to_cartesian(self,angle_degrees):
    # 将角度从度转换为弧度
        angle_radians = math.radians(angle_degrees)
    # 计算x和y坐标
        rx = math.cos(angle_radians)
        ry = math.sin(angle_radians)

        return rx, ry 

    def grasp(self, position,angle,close_position=5000, k_acc=0.1, k_vel=0.1, speed=100, force=40):

        open_position=4000

        rpy = [0,3.141,0]
        for i in range(3):
            position[i] = min(max(position[i], self.workspace_limits[i][0]), self.workspace_limits[i][1])
        # 判定抓取的角度RPY是否在规定范围内 [0.5*pi,1.5*pi]

        print('Executing: grasp at (%f, %f, %f)' \
              % (position[0], position[1], position[2]))


        # pre work
        #grasp_home =[-0.4, -0.025, 0.15, 0.000, 3.141, 0.000]
        grasp_home = [-0.3, 0.05, 0.12, 0.000, 3.141, 0.000]  #初始位置
        self.moveL(grasp_home, k_acc, k_vel)
        self.grip(open_position, speed, force)
        self.read_position()

        # Firstly, achieve pre-grasp position
        pre_position = copy.deepcopy(position)
        pre_position[2] = pre_position[2] + 0.05  # z axis + tcp
        print(pre_position)
        self.moveL(pre_position + rpy, k_acc, k_vel)

        # Second，achieve higher positiao
        air_joint = self.get_actual_joint_position()
        air_joint[5] = air_joint[5] + angle+1.57
        self.moveJ(air_joint,0.4,0.4)
        air_position  = self.get_actual_tcp_pose()

        #Third,grasp
        grasp_position = air_position
        grasp_position[2] = grasp_position[2]-0.05
        self.moveL(grasp_position, k_acc, k_vel)
        self.grip(close_position, speed, force)

        grasp_position[2] = grasp_position[2] +0.05
        self.moveL(grasp_position , k_acc, k_vel)

        # Third,put the object into box
        box_position = [-0.3, 0.05, 0.08, 0.000, 3.141, 0.000]  # 末端位置
        self.moveL(box_position, k_acc, k_vel)
        # box_position[2] = 0.1  # down to the 10cm
        # self.moveL(box_position, k_acc, k_vel)
        self.grip(open_position, speed, force)
        # box_position[2] = 0.1
        # self.moveL(box_position, k_acc, k_vel)
        self.moveL(grasp_home, k_acc, k_vel)
        print("grasp success!")

