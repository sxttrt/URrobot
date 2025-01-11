import os

# 定义类别映射规则：旧类别 -> 新类别索引
label_mapping = {
    0: 1,  # 类别 0 保持不变
    1: 2,  # 删除类别 1
    2: 3,     # 类别 2 映射为新类别 1
    3: 0   # 删除类别 3
}

# 数据集主目录
dataset_dir = "C:/Users/LCT/Desktop/YOLOV8/person_42_yolo_format"

# 子目录列表（train、valid、test）
subdirs = ["train", "valid", "test"]

# 遍历每个子目录
for subdir in subdirs:
    labels_dir = os.path.join(dataset_dir, subdir, "labels")
    print(f"正在处理目录：{labels_dir}")

    if not os.path.exists(labels_dir):
        print(f"路径不存在：{labels_dir}")
        continue

    # 遍历当前目录下的所有 .txt 文件
    for filename in os.listdir(labels_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(labels_dir, filename)

            # 打开并读取标注文件内容
            with open(file_path, "r") as f:
                lines = f.readlines()

            # 修改类别索引
            updated_lines = []
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])

                # 如果类别在映射规则中
                if class_id in label_mapping:
                    new_class_id = label_mapping[class_id]
                    if new_class_id is not None:  # 如果类别不为 None，保留
                        parts[0] = str(new_class_id)
                        updated_lines.append(" ".join(parts))
                else:
                    # 如果类别不在映射规则中，跳过
                    print(f"未处理的类别 {class_id}，文件 {filename}")

            # 写回修改后的内容
            with open(file_path, "w") as f:
                f.write("\n".join(updated_lines))

            print(f"文件 {file_path} 处理完成")

print("所有文件已处理完成！")
