import os
import random
import requests
import time
from PIL import Image
from datetime import datetime

# ================= 配置区 =================
# 1. 核心路径配置
PHOTO_DIR = "/volume1/photo/iPhone11" 
# 取照片的NAS目录
HISTORY_DIR = "/volume1/photo/Zectrix_History"
# 索引缓存文件存放位置 
INDEX_FILE = "/volume1/web/zectrix_photo_index.txt"

# 2. Zectrix 接口配置
API_URL = "https://cloud.zectrix.com/open/v1/devices/[你的设备MAC]]/display/image"
# 参考极趣云平台API的图片推送接口 
API_KEY = "[你的API]"
# 参考极趣云平台API KEY 
TARGET_PAGE = "1" 

# 3. 屏幕分辨率
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
# ==========================================

def get_random_image_fast(directory):
    """带缓存机制的极速随机读取"""
    valid_exts = {'.jpg', '.jpeg', '.png'}
    all_images = []
    
    # 判断是否已有缓存索引
    if os.path.exists(INDEX_FILE):
        print("⚡ 检测到本地照片索引，正在极速读取中...")
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            all_images = f.read().splitlines()
    else:
        print("🐌 初次运行或未找到索引，正在进行全盘深度扫描建立缓存...")
        print("   （请耐心等待几分钟，以后每次运行只需 0.1 秒！）")
        start_time = time.time()
        
        for root, _, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in valid_exts:
                    all_images.append(os.path.join(root, file))
                    
        # 将扫描结果写入本地缓存
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_images))
            
        print(f"✅ 索引建立完成！耗时 {time.time() - start_time:.2f} 秒，共记录 {len(all_images)} 张照片。")

    if not all_images:
        return None
        
    # 随机抽签，并校验文件是否仍然存在（防止你删除了某张图但缓存里还有）
    while True:
        if not all_images:
            return None # 如果所有图都被删光了
            
        choice = random.choice(all_images)
        if os.path.exists(choice):
            return choice
        else:
            # 如果文件已不存在，从列表里移除重新抽
            all_images.remove(choice)

def process_image_for_zectrix(image_path, output_path):
    img = Image.open(image_path)
    img_ratio = img.width / img.height
    target_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    
    if img_ratio > target_ratio:
        new_height = SCREEN_HEIGHT
        new_width = int(new_height * img_ratio)
    else:
        new_width = SCREEN_WIDTH
        new_height = int(new_width / img_ratio)
        
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    left = (new_width - SCREEN_WIDTH) / 2
    top = (new_height - SCREEN_HEIGHT) / 2
    right = (new_width + SCREEN_WIDTH) / 2
    bottom = (new_height + SCREEN_HEIGHT) / 2
    
    img = img.crop((left, top, right, bottom))
    img = img.convert('RGB')
    img.save(output_path, format="JPEG", quality=95)
    print(f"✂️ 图像已裁剪并归档: {output_path}")

def push_to_zectrix(image_path):
    headers = {'X-API-Key': API_KEY}
    data = {'pageId': TARGET_PAGE, 'dither': 'true'}
    
    with open(image_path, 'rb') as f:
        files = {'images': ('photo.jpg', f, 'image/jpeg')}
        try:
            print("🚀 发送请求至 Zectrix...")
            response = requests.post(API_URL, headers=headers, data=data, files=files, timeout=15)
            print(f"📡 接口响应: {response.text}")
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    img_path = get_random_image_fast(PHOTO_DIR)
    
    if img_path:
        print(f"🎯 幸运选中: {img_path}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_img_path = os.path.join(HISTORY_DIR, f"zectrix_{timestamp}.jpg")
        
        process_image_for_zectrix(img_path, history_img_path)
        push_to_zectrix(history_img_path)
    else:
        print("图库为空或未找到有效图片！")