# 不知道为什么，从手机传过来的文件有的会出现无法打开的情况
# 简单地利用ImageMagick修复一下，顺便统一图片的格式为.png

import subprocess, os
from tqdm import tqdm
from multiprocessing import Pool


# def convert_image(input_path, output_dir):
#     file_name, _ = os.path.splitext(os.path.basename(input_path))
#     output_path = os.path.join(output_dir, file_name + ".png")
#     # print(f"Converting: {input_path} to {output_path}")

#     # 替换为 'convert' 如果你使用的是 ImageMagick 版本号小于7
#     command = ["magick", input_path, output_path]


#     try:
#         subprocess.run(command, check=True)
#         # print(f"Image converted successfully: {output_path}")
#     except subprocess.CalledProcessError as e:
#         print(f"An error occurred: {e}")


def convert_image(args):
    input_path, output_dir, converted_log = args
    file_name, _ = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, file_name + ".png")

    if file_name in converted_log:
        return None

    command = ["magick", input_path, output_path]
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
        return file_name
    except subprocess.CalledProcessError as e:
        return f"Error converting {input_path}: {e.stderr.decode()}"


def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    converted_log_path = os.path.join(output_dir, "converted_log.txt")
    converted_log = set()

    if os.path.exists(converted_log_path):
        with open(converted_log_path, "r") as file:
            converted_log.update(file.read().splitlines())

    images = [
        (os.path.join(root, file), output_dir, converted_log)
        for root, _, files in os.walk(input_dir)
        for file in files
        if file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tiff"))
    ]

    with Pool(processes=os.cpu_count()) as pool:
        with tqdm(total=len(images), desc="Converting images", unit="file") as pbar:
            for result in pool.imap_unordered(convert_image, images):
                if result is not None and not isinstance(result, str):
                    pbar.set_description("Error: " + result)

                    with open("error_log.txt", "a") as log:
                        log.write(result + "\n")
                elif result is not None:

                    with open(converted_log_path, "a") as log:
                        log.write(result + "\n")
                pbar.update(1)


if __name__ == "__main__":
    print("Make sure ImageMagick is installed and accessible from the command line.")
    input_dir = input("Enter the input directory: ") or os.getcwd()
    output_dir = input("Enter the output directory: ") or os.path.join(
        os.path.dirname(input_dir), "converted_images"
    )

    if not os.path.exists(input_dir):
        print("Invalid directory provided.")
        exit(1)

    main(input_dir, output_dir)
    print("All images converted. Check 'error_log.txt' for any errors.")
    input("Press enter to exit.")

    # print("This script assumes that you have ImageMagick installed on your system")
    # print("and in the provided directory, only images exist (except this script)")
    # input_dir = input("Enter the pic directory: (if None, use current directory)")
    # output_dir = input(
    #     "Enter the output directory: (if None, a folder will be created in the parent directory)"
    # )

    # if input_dir == "":
    #     input_dir = os.getcwd()
    # if not os.path.exists(input_dir):
    #     print("Invalid directory provided.")
    #     exit(1)

    # if output_dir == "":
    #     output_dir = os.path.join(os.path.dirname(input_dir), "converted_images")
    # os.makedirs(output_dir, exist_ok=True)

    # file_num = sum(len(files) for _, _, files in os.walk(input_dir))

    # with tqdm(total=file_num, desc="Converting images", unit="file") as pbar:
    #     for root, _, files in os.walk(input_dir):
    #         for file in files:
    #             if file.endswith((".py", ".exe")) or file==".converted":
    #                 continue
    #             file_path = os.path.join(root, file)
    #             try:
    #                 convert_image(file_path, output_dir)
    #             except Exception as e:
    #                 print(f"Failed to convert {file_path}: {e}")
    #                 continue
    #             pbar.update(1)

    # print("All images converted successfully.")
    # input("Press enter to exit.")
