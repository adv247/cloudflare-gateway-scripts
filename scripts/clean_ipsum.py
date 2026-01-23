import requests
import os
import sys

# --- TẬN DỤNG BIẾN MÔI TRƯỜNG CÓ SẴN (NHƯ TRONG ẢNH 1) ---
# Ảnh 1 của bạn đã có ACCOUNT_ID và API_TOKEN, ta gọi ra dùng luôn
CF_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID") 
CF_API_TOKEN  = os.environ.get("CLOUDFLARE_API_TOKEN")

# Biến này bạn vừa tạo thêm ở Bước 1
CF_LIST_ID    = os.environ.get("CLOUDFLARE_IP_LIST_ID")

# Link danh sách gốc (Ipsum)
IPSUM_URL = "https://raw.githubusercontent.com/stamparm/ipsum/refs/heads/master/ipsum.txt"

# Giới hạn số lượng (để tránh lỗi quá tải quota)
MAX_IPS = 2000

def run_update():
    # Kiểm tra xem có đủ "chìa khóa" chưa
    if not CF_ACCOUNT_ID or not CF_API_TOKEN or not CF_LIST_ID:
        print("❌ LỖI: Thiếu biến môi trường! Hãy kiểm tra lại Secrets trong Settings.")
        sys.exit(1)

    print("1. Đang tải và làm sạch danh sách từ Github Ipsum...")
    try:
        r = requests.get(IPSUM_URL)
        data = r.text.splitlines()
    except Exception as e:
        print(f"❌ Lỗi tải file: {e}")
        return

    # --- XỬ LÝ LÀM SẠCH DỮ LIỆU ---
    clean_ips = []
    for line in data:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Cắt bỏ số lượng, chỉ lấy IP (Ví dụ: '1.2.3.4  5' -> lấy '1.2.3.4')
        parts = line.split()
        if len(parts) >= 1:
            ip = parts[0]
            # Format đúng chuẩn Cloudflare API yêu cầu
            clean_ips.append({"value": ip})

    # Cắt lấy top IP nguy hiểm nhất
    final_list = clean_ips[:MAX_IPS]
    print(f"-> Đã lọc được {len(final_list)} IP sạch.")

    # --- GỬI LÊN CLOUDFLARE ---
    print("2. Đang đồng bộ lên Cloudflare Zero Trust...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/gateway/lists/{CF_LIST_ID}/items"
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Dùng method PUT để GHI ĐÈ hoàn toàn danh sách cũ
    resp = requests.put(url, json=final_list, headers=headers)

    if resp.status_code == 200:
        print("✅ THÀNH CÔNG! Danh sách IP chặn đã được cập nhật.")
    else:
        print(f"❌ THẤT BẠI: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    run_update()
