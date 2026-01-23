import requests
import os

# --- CẤU HÌNH BẢO MẬT ---
# Thay vì điền trực tiếp, ta dùng os.environ.get để lấy từ Secret
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_LIST_ID    = os.environ.get("CLOUDFLARE_LIST_ID")
CLOUDFLARE_API_TOKEN  = os.environ.get("CLOUDFLARE_API_TOKEN")

# URL này thường không cần mật, nhưng nếu bạn muốn giấu luôn thì làm như sau:
GITHUB_RAW_URL = os.environ.get("TARGET_RAW_URL") 
# Nếu không cần giấu URL thì để nguyên string cũng được:
# GITHUB_RAW_URL = "https://raw.githubusercontent.com/user/repo/main/list.txt"

# Cloudflare giới hạn số lượng IP (Gói Free thường là 1000 hoặc 5000 IP)
# Chúng ta sẽ lấy 2000 IP đứng đầu (nguy hiểm nhất) để tránh lỗi Full List
MAX_IPS = 1000

def run_update():
    print("1. Đang tải danh sách từ Github Ipsum...")
    try:
        r = requests.get(IPSUM_URL)
        data = r.text.splitlines()
    except Exception as e:
        print(f"Lỗi tải file: {e}")
        return

    # --- XỬ LÝ LÀM SẠCH DỮ LIỆU ---
    clean_ips = []
    for line in data:
        line = line.strip()
        # Bỏ qua dòng comment hoặc dòng trống
        if not line or line.startswith("#"):
            continue
        
        # Cắt chuỗi: File ipsum có dạng "IP  ConSo", ta chỉ lấy phần IP đầu tiên
        # split() mặc định cắt theo khoảng trắng/tab
        parts = line.split()
        if len(parts) >= 1:
            ip = parts[0]
            # Tạo đúng định dạng Cloudflare yêu cầu: {"value": "1.2.3.4"}
            clean_ips.append({"value": ip})

    # Cắt lấy số lượng giới hạn để không bị lỗi quá tải
    final_list = clean_ips[:MAX_IPS]
    print(f"-> Đã lọc được {len(final_list)} IP sạch.")

    # --- GỬI LÊN CLOUDFLARE ---
    print("2. Đang gửi lên Cloudflare...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/gateway/lists/{CF_LIST_ID}/items"
    
    # Dùng method PUT để GHI ĐÈ toàn bộ (Thay thế danh sách cũ bằng mới)
    resp = requests.put(
        url,
        json=final_list,
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json"
        }
    )

    if resp.status_code == 200:
        print("✅ THÀNH CÔNG! Danh sách đã được cập nhật.")
    else:
        print(f"❌ THẤT BẠI: {resp.text}")

if __name__ == "__main__":
    run_update()
