import os
import shutil
import platform
# Author: Luke Jordan (bruceli)
# Date: 2/1/2023

"""
@author Luke Jordan (bruceli)
"""

class COLOR:
    WARN = "\x1b[1;31m"
    HIGHLIGHT = "\x1b[1;33m"
    RESET = "\x1b[0m"


def install_pip_packages(list_name, dir):
    print("Installing packages at " + dir)
    try:
        package_list = open(list_name, "r")
        for package_name in package_list:
            package_name = package_name.strip()
            print("Installing " + package_name)
            os.system("pip3 install " + package_name + " -t " + dir)
    except FileNotFoundError:
        return False
    return True

def install_include_files(list_name, dir):
    print("Including files at " + dir)
    try:
        file_list = open(list_name, "r")
        for file in file_list:
            file_name = file.strip()
            print("Including " + file_name)
            shutil.copy(file_name, dir)
    except:
        return False
    return True

file_seperator = "\\"
if (platform.system() == "Darwin"):
    file_seperator = "/"
path_to_write_to = "./exportables_to_aws/" 
path_to_install_pip = "./amazon_python_packages/"
path_to_install_helper_functions = "./include_files.txt"
package_list = "installed_packages.txt"

# Anything in this "skip list" will definitely be ignored during the zipping process.
skip_list = [
    "amazon-python-packages", 
    "exportables_to_aws"
]

# Generate the folder to hold aws lambda executable zips
if (not os.path.exists(path_to_write_to)):
    os.mkdir(path_to_write_to)
else:
    shutil.rmtree(path_to_write_to)
    os.mkdir(path_to_write_to)


#Generate the folder that contains all pip packages used by aws lambda executables
if (not os.path.exists(path_to_install_pip)):
    os.mkdir(path_to_install_pip)
    install_include_files(path_to_install_helper_functions, path_to_install_pip)
    install_pip_packages(package_list, path_to_install_pip)
else:
    would_like_to_install = input(COLOR.HIGHLIGHT + "Would you like to reinstall pip packages? [Y/n] " + COLOR.RESET)
    if (would_like_to_install.lower().strip() == "y"):
        shutil.rmtree(path_to_install_pip, ignore_errors=True)
        os.mkdir(path_to_install_pip)
        install_include_files(path_to_install_helper_functions, path_to_install_pip)
        install_pip_packages(package_list, path_to_install_pip)
    else:
        print("Skipping Pip install.")


for folder_name, sub_folders, file_names in os.walk('.'):
    if (folder_name in skip_list):
        continue
    file_path = ""
    copy_path_list = []
    for filename in file_names:
        file_path = os.path.join(folder_name, filename)
        if (("handle-" not in file_path) or ".git" in file_path):
            continue
        # Add files to zip file
        copy_path = path_to_install_pip + filename
        print("Zipping Lambda function file: " + file_path)
        f = open(copy_path, "x")
        f.close()
        shutil.copy(file_path, copy_path)
        copy_path_list.append(copy_path)
    if file_path and copy_path_list:
        shutil.make_archive(path_to_write_to + file_path.split(file_seperator)[1], 'zip', path_to_install_pip)
        for copy_path in copy_path_list:
            os.remove(copy_path)

print(COLOR.HIGHLIGHT  + "Upload the zip files at " + path_to_write_to + " to the AWS Lambda function" + COLOR.RESET)
print(COLOR.WARN + "HEADS-UP: List any python packages you used in installed_packages.txt or your lambda function won't work." + COLOR.RESET)
        