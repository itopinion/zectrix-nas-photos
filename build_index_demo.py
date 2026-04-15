import os
import time
from PIL import Image, ExifTags

# ================= 配置区 =================
# 注意：如果你想扫整个 photo 文件夹，请改成 "/volume1/photo"
PHOTO_DIR = "/volume1/photo" 
INDEX_FILE = "/volume1/web/zectrix_photo_index.txt" 
# ==========================================

def get_photo_info(image_path):
    """
    核心鉴定器：提取 EXIF，鉴别真假，获取时间
    """
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if not exif:
            return False, None

        is_real_photo = False
        shoot_date = None

        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if tag_name in ('Make', 'Model'):
                is_real_photo = True
            if tag_name in ('DateTimeOriginal', 'DateTime') and isinstance(value, str):
                if len(value) >= 10:
                    shoot_date = value[:10].replace(':', '-')

        if is_real_photo and not shoot_date:
            timestamp = os.path.getmtime(image_path)
            shoot_date = time.strftime('%Y-%m-%d', time.localtime(timestamp))

        return is_real_photo, shoot_date
    except:
        return False, None

if __name__ == "__main__":
    print("🚀 启动岁月史书扫描机 (已开启 @eaDir 免疫护盾)...")
    valid_records = []
    processed_count = 0
    
    # os.walk 会返回三个值：当前路径(root)、子文件夹列表(dirs)、文件列表(files)
    for root, dirs, files in os.walk(PHOTO_DIR):
        
        # 🛡️ 核心护盾：看到群晖的缩略图文件夹，直接踢出遍历列表，根本不进去！
        if '@eaDir' in dirs:
            dirs.remove('@eaDir')
            
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                processed_count += 1
                full_path = os.path.join(root, file)
                
                is_real, p_date = get_photo_info(full_path)
                
                if is_real and p_date:
                    valid_records.append(f"{p_date}|{full_path}")
                
                if processed_count % 2000 == 0:
                    print(f"⏳ 已处理 {processed_count} 个原图，收录 {len(valid_records)} 张真实照片...")

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(valid_records))
        
    print(f"✅ 建库完成！成功避开所有缩略图，共提纯 {len(valid_records)} 张高清原图。")