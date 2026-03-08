# Windows定时关机/重启工具

一个简单易用的Windows定时关机和重启工具，带有图形化界面。

## 功能特性

- 支持设置任意日期和时间的定时关机或重启
- 图形化界面，操作简单直观
- 系统托盘功能，最小化后在后台运行
- 支持随时取消任务

## 安装依赖

```bash
pip install pystray pillow
```

## 运行程序

```bash
python main.py
```

## 打包成EXE

```bash
# 安装打包工具
pip install pyinstaller

# 执行打包
pyinstaller --onefile --windowed --name "定时关机工具" --hidden-import pystray --hidden-import PIL main.py
```

打包完成后，在 `dist` 目录下会生成独立的EXE文件。

## 使用说明

1. 设置执行日期和时间
2. 选择操作类型（关机/重启）
3. 点击"确定"开始任务
4. 如需取消，点击"撤销"

## 项目结构

```
shutdowntime/
├── main.py          # 主程序文件
└── README.md        # 项目说明
```
