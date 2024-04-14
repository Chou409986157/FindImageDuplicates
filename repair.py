# 不知道为什么，从手机传过来的文件有的会出现无法打开的情况
# 简单地利用ImageMagick修复一下，顺便统一图片的格式为.png

import subprocess, os
from tqdm import tqdm


def convert_image(input_path, output_dir):
    file_name, _ = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, file_name + ".png")
    # print(f"Converting: {input_path} to {output_path}")

    # 替换为 'convert' 如果你使用的是 ImageMagick 版本号小于7
    command = ["magick", input_path, output_path]

    try:
        subprocess.run(command, check=True)
        # print(f"Image converted successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("This script assumes that you have ImageMagick installed on your system")
    print("and in the provided directory, only images exist (except this script)")
    input_dir = input("Enter the pic directory: (if None, use current directory)")
    output_dir = input(
        "Enter the output directory: (if None, a folder will be created in the parent directory)"
    )

    if input_dir == "":
        input_dir = os.getcwd()
    if not os.path.exists(input_dir):
        print("Invalid directory provided.")
        exit(1)

    if output_dir == "":
        output_dir = os.path.join(os.path.dirname(input_dir), "converted_images")
    os.makedirs(output_dir, exist_ok=True)

    file_num = sum(len(files) for _, _, files in os.walk(input_dir))

    with tqdm(total=file_num, desc="Converting images", unit="file") as pbar:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith((".py", ".exe")):
                    continue
                file_path = os.path.join(root, file)
                try:
                    convert_image(file_path, output_dir)
                except Exception as e:
                    print(f"Failed to convert {file_path}: {e}")
                    continue
                pbar.update(1)

    print("All images converted successfully.")
    input("Press any key to exit.")
