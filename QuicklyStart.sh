#!/bin/bash
# 脚本名称：run_script.sh
# 功能：使用sudo权限运行指定的Python脚本

# 指定Python脚本的路径
SCRIPT_PATH="/home/pi/Code/Server/main.py"

# 使用sudo和python执行脚本
sudo python $SCRIPT_PATH
