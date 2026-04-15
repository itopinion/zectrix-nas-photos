# 极趣AI便利贴NAS图片同步脚本
项目原地址 https://wiki.zectrix.com/zh/software/Community-OpenSource

# 📸 Zectrix NAS Photo Pusher (桌面时光机)

拒绝让 NAS 里的几万张照片吃灰！这是一个专为 **极趣实验室 (Zectrix Lab)** AI 墨水屏便利贴（如 Note4）设计的轻量级 Python 脚本。

配合群晖 (Synology) 或其他 NAS 的定时任务功能，你可以轻松打造一个专属的“桌面时光机”，在桌面上自动轮播那些被遗忘的美好瞬间。

## ✨ 核心特性

* **⚡️ 极速缓存机制**：脚本首次运行会自动扫描照片目录并建立 `.txt` 索引。此后运行仅需 **0.1 秒** 即可完成随机抽图，支持数万张照片的大型图库。
* **✂️ 智能适配裁剪**：自动识别照片比例，进行高质量的等比缩放与居中裁剪，完美适配 400x300 分辨率，确保在墨水屏上不拉伸、不变形。
* **☁️ 云端直接推送**：调用 Zectrix 开放平台 API，支持 Dither 抖动算法，优化照片在 E-ink 屏幕上的灰度表现。

---

## 🛠️ 环境准备

在开始使用前，请确保您的 NAS 环境满足以下要求：

1. **Python 3 环境**：建议在群晖套件中心安装官方 Python 3 套件。
2. **安装依赖库**：在终端执行以下命令（根据您的 Python 版本调整）：
   ```bash
   # 示例：如果是 Python 3.14 环境
   python3.14 -m pip install Pillow requests
   ```
3. **获取 API 信息**：登录 [极趣云平台](https://cloud.zectrix.com) 获取设备的 **MAC 地址** 和 **API KEY**。

---

## ⚙️ 配置指南

打开 `nas_pic_demo.py`，修改开头 **`配置区`** 的以下参数：

```python
# 1. 路径配置 (请务必使用绝对路径)
PHOTO_DIR = "/volume1/photo/iPhone11"        # 你的照片源目录
HISTORY_DIR = "/volume1/photo/Zectrix_History" # 裁剪后的图片存放目录
INDEX_FILE = "/volume1/web/zectrix_photo_index.txt" # 索引文件位置

# 2. 设备 API 配置
API_URL = "https://cloud.zectrix.com/open/v1/devices/[你的设备MAC]/display/image"
API_KEY = "[你的API_KEY]"
TARGET_PAGE = "1" # 推送到屏幕的页码
```

---

## 🚀 运行说明

### 手动测试
通过 SSH 连接到 NAS，进入脚本目录并运行：
```bash
python3 nas_pic_demo.py
```

### 自动推送 (群晖任务计划)
为了实现“时光机”效果，建议设置定时运行：
1. 进入群晖 **控制面板** -> **任务计划** -> **新增** -> **计划的任务** -> **用户定义的脚本**。
2. 在“计划”页签设置刷新频率（如每天早晨，或每 1 小时一次）。
3. 在“任务设置”的运行命令中输入（请替换为你自己的实际路径）：
   ```bash
   cd /volume1/web/ && python3 nas_pic_demo.py
   ```

---

## 💡 常见问题

* **问：如何更新图库索引？**
  * 答：如果新增了照片，只需删除配置的 `.txt` 索引文件，脚本下次运行时会自动重新全量扫描。
* **问：运行报 PIL 错误？**
  * 答：请确保通过 `pip` 安装了 `Pillow` 库，且运行脚本的 Python 版本与安装库的版本一致。
* **问：竖构图照片被裁剪太多？**
  * 答：当前 Demo 采用居中满屏裁剪方案。如需“历史上的今天”高级逻辑或更精细的排版（自动留白、添加日期铭牌），请关注我们的进阶教程。

---

### 关注我们
欢迎关注 **极趣实验室 (Zectrix Lab)**，获取更多硬核硬件玩法！网址 www.zectrix.com
* **Bilibili**: 搜索 `极趣实验室` 
