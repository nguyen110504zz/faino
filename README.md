# Financial Report Generator

Hệ thống tạo báo cáo tài chính chuyên nghiệp với định dạng A4 chuẩn cho in ấn.

## Yêu cầu cài đặt
## Cài đặt GTK3 (Bắt buộc cho WeasyPrint)

### Windows:
1. Tải GTK3 từ: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Chạy file cài đặt GTK3-Runtime Win64
3. Thêm đường dẫn vào PATH (thường là `C:\Program Files\GTK3-Runtime Win64\bin`)

## Các bước chạy ứng dụng
1. Cài đặt môi trường:
```bash
# Tạo và kích hoạt môi trường ảo
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Cài đặt thư viện
python -m pip install --upgrade pip
pip install -r requirements.txt

```
2. Chạy ứng dụng:
```bash
python App/app.py
```

## Tạo PDF
1. Từ trình duyệt, chọn một trong hai cách:
- Click nút "Tải báo cáo PDF"
- Hoặc nhấn Ctrl+P (Windows) / Cmd+P (Mac)
2. Thiết lập PDF:
- Đích: Save as PDF
- Khổ giấy: A4
- Lề: None
- Tỷ lệ: 100%
- Đồ họa nền: Bật

## Xử lý lỗi thường gặp

1. Lỗi cài đặt thư viện:
```bash
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

2. Lỗi không chạy được:
- Kiểm tra đã activate môi trường ảo
- Chạy lại lệnh cài đặt thư viện

3. Lỗi tạo PDF:
- Dùng Chrome/Chromium
- Đảm bảo đúng thiết lập in

## Hỗ trợ
Tạo issue trên GitHub hoặc liên hệ: [your-email/contact]

## License
Dự án này là tài sản độc quyền. Nghiêm cấm sao chép khi chưa được phép.