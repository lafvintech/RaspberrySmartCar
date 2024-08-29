#!/bin/bash

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]
  then echo "请以 root 权限运行此脚本"
  exit
fi

echo "欢迎使用 main.py 自动启动设置脚本"
echo "本脚本将设置当前目录下的 main.py 在树莓派启动时自动运行"

# 获取脚本所在目录的绝对路径
DIR_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN_PATH="$DIR_PATH/main.py"

# 检查 main.py 文件是否存在
if [ ! -f "$MAIN_PATH" ]; then
    echo "错误：文件 $MAIN_PATH 不存在"
    exit 1
fi

# 创建 systemd 服务文件
cat << EOF > /etc/systemd/system/carserver.service
[Unit]
Description=Car Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 $MAIN_PATH
WorkingDirectory=$DIR_PATH
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

echo "systemd 服务文件已创建"

# 重新加载 systemd 管理器配置
systemctl daemon-reload

# 启用服务
systemctl enable carserver.service

echo "服务已启用，将在下次启动时自动运行"

# 询问用户是否立即启动服务
read -p "是否立即启动服务？(y/n) " START_NOW

if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    systemctl start carserver.service
    echo "服务已启动"
    echo "您可以使用 'sudo systemctl status carserver.service' 查看服务状态"
else
    echo "服务将在下次系统启动时运行"
fi

echo "设置完成！"
