import os
import random
import requests
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ================= 配置区 =================
# 1. 核心路径配置，参考目录，根据自己需求改
INDEX_FILE = "/volume1/web/zectrix_photo_index.txt" 
OUTPUT_DIR = "/volume1/web"  

# 2. Zectrix 接口配置
API_URL = "https://cloud.zectrix.com/open/v1/devices/[你的设备MAC]/display/image"
API_KEY = "极趣云平台API"
TARGET_PAGE = "1" 

# 3. 屏幕分辨率与显示配置
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
# ==========================================

def parse_date_from_line(line):
    """解析 txt 文件中的日期和路径"""
    date_pattern = re.compile(r'(\d{4})[:/-](\d{2})[:/-](\d{2})')
    path_idx = line.find('/volume1')
    if path_idx == -1:
        return None
        
    date_part = line[:path_idx]
    path_part = line[path_idx:].strip()
    
    match = date_pattern.search(date_part)
    if match:
        return {
            "year": int(match.group(1)),
            "month": int(match.group(2)),
            "day": int(match.group(3)),
            "path": path_part
        }
    return None

def get_day_diff(m1, d1, m2, d2):
    """计算两个日期在一年中的相隔天数（处理跨年和闰年）"""
    try:
        # 统一使用 2004 闰年来规避 2月29日 的计算报错问题
        date1 = datetime(2004, m1, d1)
        date2 = datetime(2004, m2, d2)
        diff = abs((date1 - date2).days)
        # 考虑跨年的情况 (例如 1月1日 和 12月31日 其实只差1天)
        return min(diff, 366 - diff)
    except ValueError:
        return 999  # 如果遇到脏数据（比如 2月30日），直接排除

def get_history_image(index_file):
    """核心逻辑：按年份公平权重，在前后10天内抽取照片"""
    if not os.path.exists(index_file):
        print(f"❌ 找不到索引文件: {index_file}")
        return None

    today = datetime.now()
    current_year = today.year
    
    valid_records_by_year = {}
    all_valid_records = []
    
    print("🔍 正在扫描图库，寻找历史上的近期回忆 (±10天)...")
    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            record = parse_date_from_line(line.strip())
            if record and os.path.exists(record['path']):
                all_valid_records.append(record)
                
                # 排除今年的照片
                if record['year'] != current_year:
                    # 计算相差天数
                    diff = get_day_diff(today.month, today.day, record['month'], record['day'])
                    if diff <= 10:  # 前后 10 天以内
                        year = record['year']
                        if year not in valid_records_by_year:
                            valid_records_by_year[year] = []
                        valid_records_by_year[year].append(record)

    if valid_records_by_year:
        print(f"🎉 在前后10天内，找到了 {len(valid_records_by_year)} 个不同年份的历史足迹！")
        # 核心改动：先随机选一个【年份】，保证每年被抽中的概率均等
        chosen_year = random.choice(list(valid_records_by_year.keys()))
        # 然后再从那个年份里随机选一张【照片】
        chosen_record = random.choice(valid_records_by_year[chosen_year])
        print(f"🎲 抽签结果：选中了 {chosen_year} 年的照片！")
        return chosen_record
        
    if all_valid_records:
        print("⚠️ 近期无历史照片，开启全局随机回忆模式...")
        return random.choice(all_valid_records)
        
    return None

def process_image_with_watermark(record, output_path):
    """处理图片，在右下角添加精致的黑色小铭牌"""
    img_path = record['path']
    # 稍微精简一下文案，让小方块更紧凑
    date_text = f"{record['year']}年{record['month']}月{record['day']}日"
    
    img = Image.open(img_path)
    img = ImageOps.exif_transpose(img)
    
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
    
    draw = ImageDraw.Draw(img)
    
    # === 绘制右下角精致小铭牌 ===
    try:
        # 换成 12 号字体
        font = ImageFont.truetype("ark-pixel-12px-monospaced-zh_cn.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
        print("⚠️ 警告：找不到 ark-pixel-12px-monospaced-zh_cn.ttf，使用默认字体。")
        
    # 获取文字的实际宽高
    text_bbox = draw.textbbox((0, 0), date_text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    # 铭牌样式设置
    padding_x = 6      # 文字左右留白
    padding_y = 4      # 文字上下留白
    margin_right = 10  # 距离屏幕最右侧的边距
    margin_bottom = 10 # 距离屏幕最底部的边距
    
    rect_w = text_w + padding_x * 2
    rect_h = text_h + padding_y * 2
    
    # 计算黑色方块的左上角和右下角坐标
    rect_x1 = SCREEN_WIDTH - rect_w - margin_right
    rect_y1 = SCREEN_HEIGHT - rect_h - margin_bottom
    rect_x2 = rect_x1 + rect_w
    rect_y2 = rect_y1 + rect_h
    
    # 画黑色小方块
    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill="black")
    
    # 画白色文字 (微调文字的Y轴使其在黑块中垂直居中)
    text_x = rect_x1 + padding_x
    text_y = rect_y1 + padding_y - text_bbox[1] 
    
    draw.text((text_x, text_y), date_text, font=font, fill="white")
    
    img.save(output_path, format="JPEG", quality=95)
    print(f"✂️ 图像已处理并打上精致铭牌: {output_path}")

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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    selected_record = get_history_image(INDEX_FILE)
    
    if selected_record:
        print(f"🎯 最终选中照片: {selected_record['path']}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_img_path = os.path.join(OUTPUT_DIR, f"zectrix_history_{timestamp}.jpg")
        
        process_image_with_watermark(selected_record, history_img_path)
        push_to_zectrix(history_img_path)
    else:
        print("❌ 未能成功匹配到任何有效照片！")