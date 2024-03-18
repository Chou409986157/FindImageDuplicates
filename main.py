from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QLabel
import os, shutil, json
from typing import Union, Tuple
import hashlib, imagehash
from PIL import Image


class LaunchMode(QDialog):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("./LaunchMode.ui", self)
        self.console.clicked.connect(self.InConsole)
        self.ui.clicked.connect(self.OpenUI)

    def InConsole(self) -> None:
        self.close()
        img_dir = "./"
        os.system(
            f'start cmd.exe /c "echo operating in {os.path.abspath(img_dir)} & pause"'
        )
        handler = IdentityComputation(img_dir)
        result = handler.Duplicates()
        if type(result) == tuple:
            same_images, similar_images = result
            print("Same images: ")
            for i in range(len(same_images)):
                print(
                    f"{os.path.basename(same_images[i][0])} is duplicate of {same_images[i][1]}"
                )
            print("Similar images: ")
            for i in range(len(similar_images)):
                print(
                    f"{os.path.basename(similar_images[i][0])} is similar to {similar_images[i][1]}"
                )
        elif result == 0:
            print("No duplicates found")

    def OpenUI(self) -> None:
        self.close()
        self.ui = UI()
        self.ui.show()


class UI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("./UI.ui", self)
        self.file_path.clicked.connect(self.FileDir)

    def FileDir(self) -> str:
        dir = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if dir:
            self.file_path_label.setText(dir)
            return dir
        else:
            return ""

    def InUI(self) -> None:
        img_dir = self.FileDir()
        if img_dir:
            handler = IdentityComputation(img_dir)
            result = handler.Duplicates()
        if type(result) == tuple:
            same_images, similar_images = result
            for i in range(len(same_images)):
                print(
                    f"{os.path.basename(same_images[i][0])} is duplicate of {same_images[i][1]}"
                )


class IdentityComputation:
    def __init__(self, img_folder) -> None:
        self.img_folder = os.path.abspath(img_folder)

    def Duplicates(self) -> Union[str, (Tuple[Tuple, Tuple]), int]:
        similar_images = []
        same_images = []
        image_files = []
        git_folder = ".git"
        duplicates_folder = "duplicates"
        if not os.path.exists(duplicates_folder):
            os.mkdir(duplicates_folder)
        try:
            for root, dirs, files in os.walk(self.img_folder, topdown=True):
                dirs[:] = [d for d in dirs if d not in [duplicates_folder, git_folder]]
                # if (
                #     os.path.abspath(root) == self.duplicates_folder
                #     or os.path.abspath(root) == git_folder
                # ):
                #     continue
                for file in files:
                    if file.endswith(
                        (
                            "exe",
                            "py",
                            "pyc",
                            "pyi",
                            "ui",
                            "json",
                            "txt",
                            "md",
                            "gitignore",
                            "gitattributes",
                        )
                    ):
                        continue
                    image_files.append(os.path.join(root, file))
            image_files.sort(reverse=True, key=lambda x: os.path.basename(x))
            # print(image_files)
        except Exception as e:
            return e
        dhash_dict = {}
        for file in image_files:
            try:
                img = Image.open(file)
                dhash = self.DhashComputation(img)
                if dhash not in dhash_dict.keys():
                    dhash_dict[dhash] = file
                else:
                    same_images.append((dhash_dict[dhash], file))
            except Exception as e:
                print(e)
        # serializable_dict = {str(key): value for key, value in dhash_dict.items()}
        # with open("dhash_dict.json", "w") as f:
        #     json.dump(serializable_dict, f)
        dhash_keys = [key for key in dhash_dict.keys()]
        for i in range(len(dhash_keys)):
            for j in range(i + 1, len(dhash_keys)):
                if dhash_keys[i] - dhash_keys[j] < 5:
                    if self.MD5Computation(
                        dhash_dict[dhash_keys[i]]
                    ) == self.MD5Computation(dhash_dict[dhash_keys[j]]):
                        # try:
                        #     shutil.move(dhash_dict[dhash_keys[j]], self.duplicates_folder)
                        # except Exception as e:
                        #     print(e)
                        same_images.append(
                            (dhash_dict[dhash_keys[i]], dhash_dict[dhash_keys[j]])
                        )
                    else:
                        similar_images.append(
                            (dhash_dict[dhash_keys[i]], dhash_dict[dhash_keys[j]])
                        )
        if same_images:
            # print("Same images: ")
            for i in range(len(same_images)):
                # print(
                #     f"{os.path.basename(same_images[i][0])} is duplicate of {same_images[i][1]}"
                # )
                try:
                    shutil.move(same_images[i][1], duplicates_folder)
                except Exception as e:
                    print(e)
        # if similar_images:
        #     print("Similar images: ")
        #     for i in range(len(similar_images)):
        #         print(
        #             f"{os.path.basename(similar_images[i][0])} is similar to {similar_images[i][1]}"
        #         )
        if same_images or similar_images:
            return (tuple(same_images), tuple(similar_images))
        else:
            # print("No duplicates found")
            return 0

    def MD5Computation(self, file_path) -> str:
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

    def DhashComputation(self, file_path) -> imagehash.ImageHash:
        hash = imagehash.dhash(file_path, 32)
        return hash


if __name__ == "__main__":
    app = QApplication([])
    window = LaunchMode()
    window.show()
    app.exec_()
