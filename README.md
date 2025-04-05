# Financial Report Generator

Hệ thống tạo báo cáo tài chính chuyên nghiệp với định dạng A4 chuẩn cho in ấn.

## Yêu cầu cài đặt
- Python 3.8 trở lên
- Google Chrome/Chromium
- GTK3 (cho WeasyPrint)

## Cài đặt GTK3 (Bắt buộc cho WeasyPrint)

### Windows:
1. Tải GTK3 từ: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Chạy file cài đặt GTK3-Runtime Win64
3. Thêm đường dẫn vào PATH (thường là `C:\Program Files\GTK3-Runtime Win64\bin`)

### macOS:
```bash
brew install cairo pango gdk-pixbuf libffi
```

## Cài đặt ứng dụng

### Phương pháp 1: Sử dụng môi trường ảo (Khuyến nghị)
1. Tạo môi trường ảo:
```bash
# Tạo môi trường ảo
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Cài đặt thư viện:
```bash
# Cập nhật pip
python -m pip install --upgrade pip

# Cài đặt thư viện
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
python App/app.py
```

4. Truy cập ứng dụng:
- Mở Chrome/Chromium
- Truy cập: http://localhost:5000

### Phương pháp 2: Cài đặt trực tiếp (Không dùng môi trường ảo)
1. Cài đặt thư viện:
```bash
# Cập nhật pip
python -m pip install --upgrade pip

# Cài đặt thư viện
pip install -r requirements.txt
```

2. Chạy ứng dụng:
```bash
python App/app.py
```
## Xử lý lỗi thường gặp

1. Lỗi WeasyPrint:
```bash
# Windows - Kiểm tra GTK3
echo %PATH%  # Kiểm tra đường dẫn GTK3
# Thử cài đặt lại
pip uninstall WeasyPrint
pip install WeasyPrint==60.1
```

2. Lỗi cài đặt thư viện:
```bash
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

3. Lỗi không chạy được:
- Kiểm tra đã activate môi trường ảo (nếu dùng)
- Kiểm tra cài đặt GTK3 thành công
- Chạy lại lệnh cài đặt thư viện
