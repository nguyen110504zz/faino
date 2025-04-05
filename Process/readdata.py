#%%
import pandas as pd
import os
from typing import Dict, Any
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#%%Chuyển đổi đơn vị
def convert_units(df, factor, start_col):
    try:
        start_idx = df.columns.get_loc(start_col) + 1
        numeric_cols = df.columns[start_idx:]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi đơn vị: {e}")
    return df
#%%Chuẩn hóa tên cột
def standardize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace("\n", " ").str.upper()
    return df
#%%Gộp dữ liệu theo mã hoặc tên công ty
def merge_balance_sheets(dfs, search_term):
    data = []
    dfs = [standardize_columns(df) for df in dfs]
    search_term = search_term.upper().strip()

    for year, df in zip(range(2020, 2025), dfs):
        if 'MÃ' not in df.columns or 'TÊN CÔNG TY' not in df.columns:
            logger.error(f"Thiếu cột 'MÃ' hoặc 'TÊN CÔNG TY' trong file năm {year}")
            continue

        # Chuẩn hóa dữ liệu để tránh lỗi khoảng trắng hoặc phân biệt chữ hoa/thường
        df['MÃ'] = df['MÃ'].astype(str).str.strip().str.upper()
        df['TÊN CÔNG TY'] = df['TÊN CÔNG TY'].astype(str).str.strip().str.upper()

        # Phân biệt tìm kiếm theo mã hoặc tên công ty
        if len(search_term) <= 3:  # Giả định mã cổ phiếu thường ngắn (ví dụ 3-5 ký tự)
            stock_data = df[df['MÃ'] == search_term]  # Tìm chính xác theo mã
            logger.info(f"Tìm kiếm theo mã {search_term} trong file năm {year}")
        else:
            stock_data = df[df['TÊN CÔNG TY'].str.contains(search_term, case=False, na=False)]  # Tìm theo tên
            logger.info(f"Tìm kiếm theo tên '{search_term}' trong file năm {year}")

        if not stock_data.empty:
            logger.info(f"✅ Tìm thấy {len(stock_data)} dòng dữ liệu cho {search_term} năm {year}")
            data.append(stock_data)
        else:
            logger.warning(f"⚠️ Không tìm thấy dữ liệu cho {search_term} năm {year}")

    if data:
        result = pd.concat(data, ignore_index=True)
        logger.info(f"✅ Tổng cộng tìm thấy {len(result)} dòng dữ liệu cho {search_term}")
        return result
    else:
        logger.error(f"❌ Không tìm thấy dữ liệu cho '{search_term}' trong tất cả các năm")
        return pd.DataFrame()


#%%Xử lý dữ liệu tài chính
def process_financial_data(search_term):
    try:
        # Đọc dữ liệu từ các file Excel
        file_names = [f"D:/TAI LIEU/web/faino/Data/{year}-Vietnam.xlsx" for year in range(2020, 2025)]
        dfs = [pd.read_excel(file, engine="openpyxl") for file in file_names]

        # Chuẩn hóa tên cột
        for df, year in zip(dfs, range(2020, 2025)):
            df.columns = df.columns.str.replace(f"Năm: {year}", "", regex=True).str.strip()
            df.columns = df.columns.str.replace(r"Đơn vị: (Tỷ|Triệu|Đồng) VND", "", regex=True).str.strip()
            df.columns = df.columns.str.replace(r"\bHợp nhất\b", "", regex=True).str.strip()
            df.columns = df.columns.str.replace(r"\bQuý: Hàng năm\b", "", regex=True).str.strip()

        # Xóa các cột không cần thiết
        for df in dfs:
            df.drop(columns=[col for col in df.columns if "TM" in col], inplace=True, errors='ignore')

        # Xác định tên cột tham chiếu
        start_column = "Trạng thái kiểm toán"
        start_column_cleaned = start_column.replace("Hợp nhất", "").replace("Hàng năm", "").strip()

        # Chuyển đổi đơn vị cho các năm 2020-2022 (giữ nguyên vì đã là đồng)
        for i in range(3):
            dfs[i] = convert_units(dfs[i], 1, start_column_cleaned)

        # Chuyển đổi đơn vị cho các năm 2023-2024 (từ tỷ sang đồng)
        for i in range(3, 5):
            start_idx = dfs[i].columns.get_loc(start_column_cleaned) + 1
            numeric_cols = dfs[i].columns[start_idx:]
            dfs[i][numeric_cols] = dfs[i][numeric_cols].apply(pd.to_numeric, errors='coerce') * 1000000000
            logger.info(f"Đã chuyển đổi dữ liệu năm {2020 + i} từ tỷ sang đồng")

        # Gộp dữ liệu
        merged_df = merge_balance_sheets(dfs, search_term)
        if merged_df.empty:
            return pd.DataFrame()

        # Xóa cột không mong muốn
        merged_df = merged_df.loc[:, ~merged_df.columns.str.contains("CURRENT RATIO", case=False, na=False)]

        # Chuyển đổi DataFrame từ 5 hàng × N cột thành N hàng × 5 cột
        transposed_df = merged_df.T
        transposed_df.reset_index(inplace=True)

        # Xử lý cột dư thừa
        expected_years = [str(year) for year in range(2020, 2025)]
        valid_columns = ["Chỉ tiêu"] + expected_years

        if len(transposed_df.columns) != len(valid_columns):
            print(f"⚠️ Phát hiện số cột không khớp. Đang điều chỉnh...")
            transposed_df = transposed_df.iloc[:, :len(valid_columns)]

        # Gán lại tên cột
        transposed_df.columns = valid_columns
        transposed_df.fillna(0, inplace=True)

        print(f"✅ Dữ liệu sau khi điều chỉnh: {transposed_df.shape[1]} cột")
        return transposed_df

    except Exception as e:
        print(f"🛑 Lỗi trong quá trình xử lý dữ liệu: {e}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Get basic information about a stock symbol from local data
    """
    try:
        logger.info(f"Đang tìm thông tin cho mã: {symbol}")
        # Sử dụng hàm process_financial_data để lấy dữ liệu
        df = process_financial_data(symbol)
        if df.empty:
            logger.error(f"Không tìm thấy dữ liệu cho mã {symbol}")
            return {}
            
        logger.info(f"Đã tìm thấy dữ liệu cho mã {symbol}")

        # Đọc dữ liệu giá từ file CSV
        price_data = pd.DataFrame()
        try:
            price_file = os.path.join(os.path.dirname(__file__), '..', 'Data', f'{symbol}_prices.csv')
            if os.path.exists(price_file):
                price_data = pd.read_csv(price_file)
                price_data['Date'] = pd.to_datetime(price_data['Date'])
                price_data = price_data.sort_values('Date')
                logger.info(f"Đã đọc dữ liệu giá từ file {price_file}")
        except Exception as e:
            logger.error(f"Lỗi khi đọc dữ liệu giá: {e}")

        # Tính toán các chỉ số từ dữ liệu giá
        close_price = 0
        high_52w = '-'
        low_52w = '-'
        one_day_change = '-'
        five_day_change = '-'
        three_month_change = '-'
        six_month_change = '-'
        mtd_change = '-'
        ytd_change = '-'
        ytd_relative_change = '-'

        if not price_data.empty:
            # Lấy giá đóng cửa mới nhất
            close_price = price_data['Close'].iloc[-1]
            
            # Tính 52 week high/low
            last_year_data = price_data[price_data['Date'] >= price_data['Date'].max() - pd.DateOffset(years=1)]
            if not last_year_data.empty:
                high_52w = f"{last_year_data['High'].max():,.0f}"
                low_52w = f"{last_year_data['Low'].min():,.0f}"

            # Tính các thay đổi giá
            latest_price = price_data['Close'].iloc[-1]
            
            # 1 day change
            if len(price_data) > 1:
                prev_price = price_data['Close'].iloc[-2]
                one_day_change = f"{((latest_price - prev_price) / prev_price * 100):.2f}%"

            # 5 day change
            if len(price_data) > 5:
                five_day_ago = price_data['Close'].iloc[-6]
                five_day_change = f"{((latest_price - five_day_ago) / five_day_ago * 100):.2f}%"

            # 3 month change
            three_months_ago_data = price_data[price_data['Date'] >= price_data['Date'].max() - pd.DateOffset(months=3)]
            if not three_months_ago_data.empty:
                three_month_start = three_months_ago_data['Close'].iloc[0]
                three_month_change = f"{((latest_price - three_month_start) / three_month_start * 100):.2f}%"

            # 6 month change
            six_months_ago_data = price_data[price_data['Date'] >= price_data['Date'].max() - pd.DateOffset(months=6)]
            if not six_months_ago_data.empty:
                six_month_start = six_months_ago_data['Close'].iloc[0]
                six_month_change = f"{((latest_price - six_month_start) / six_month_start * 100):.2f}%"

            # Month to date
            current_month = price_data[price_data['Date'].dt.month == price_data['Date'].max().month]
            if not current_month.empty:
                month_start = current_month['Close'].iloc[0]
                mtd_change = f"{((latest_price - month_start) / month_start * 100):.2f}%"

            # Year to date
            current_year = price_data[price_data['Date'].dt.year == price_data['Date'].max().year]
            if not current_year.empty:
                year_start = current_year['Close'].iloc[0]
                ytd_change = f"{((latest_price - year_start) / year_start * 100):.2f}%"
                ytd_relative_change = ytd_change  # Giả định tương đối với index

        # Tính volume trung bình
        avg_volume_5d = '-'
        avg_volume_10d = '-'
        if not price_data.empty:
            if len(price_data) >= 5:
                avg_volume_5d = f"{price_data['Volume'].tail(5).mean():,.0f}"
            if len(price_data) >= 10:
                avg_volume_10d = f"{price_data['Volume'].tail(10).mean():,.0f}"

        return {
            'name': f'{symbol} Group',
            'symbol': symbol,
            'sector': 'Consumer Goods',
            'industry': 'Food & Beverage',
            'description': 'VNG Corporation, founded in 2004, is a leading technology company in Vietnam, primarily focused on digital entertainment, social networking, and e-commerce. The company has expanded its reach to various sectors, becoming a prominent player in Vietnam''s internet industry. VNG Group is a tech conglomerate with a strong presence in gaming, social networking, e-commerce, and fintech, driven by a vision to innovate and lead the digital transformation in Vietnam and Southeast Asia.',
            'address': 'VIETNAM',
            'phone': '+84 (22) 8 3724 4555',
            'website': 'Start@vng.com.vn',
            'employees': 34816,
            'market_cap': '169,720.61B',
            'close_price': f"{close_price:,.0f}",
            'avg_volume_5d': avg_volume_5d,
            'avg_volume_10d': avg_volume_10d,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'currency': 'VND',
            'beta': '-',
            'isin_code': 'VN000000HPG4',
            'exchange_code': 'HNX',
            'one_day_change': one_day_change,
            'five_day_change': five_day_change,
            'three_month_change': three_month_change,
            'six_month_change': six_month_change,
            'mtd_change': mtd_change,
            'ytd_change': ytd_change,
            'ytd_relative_change': ytd_relative_change,
            'strong_buy': '5',
            'buy': '3',
            'hold': '2',
            'sell': '1',
            'strong_sell': '0',
            'recommendation': 'BUY',
            'shares_outstanding': '4,472,500,000'
        }
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin cổ phiếu: {e}")
        return {}

def get_financial_data(symbol: str) -> Dict[str, pd.DataFrame]:
    """
    Get financial statements from local data
    """
    try:
        logger.info(f"Đang lấy dữ liệu tài chính cho mã: {symbol}")
        # Sử dụng hàm process_financial_data để lấy dữ liệu
        df = process_financial_data(symbol)
        if df.empty:
            logger.error(f"Không tìm thấy dữ liệu tài chính cho mã {symbol}")
            return {}

        # Tạo các DataFrame cho từng loại báo cáo tài chính
        years = [str(year) for year in range(2020, 2025)]
        
        # In ra tất cả các chỉ tiêu để debug
        logger.info("Danh sách các chỉ tiêu có sẵn:")
        for idx, row in df.iterrows():
            logger.info(f"- {row['Chỉ tiêu']}")
        
        # Tìm các chỉ tiêu cần thiết trong DataFrame với nhiều pattern khác nhau
        balance_sheet_patterns = {
            'current_assets': ['TÀI SẢN NGẮN HẠN', 'TSNH'],
            'fixed_assets': ['TÀI SẢN DÀI HẠN', 'TSDH'],
            'total_assets': ['TỔNG CỘNG TÀI SẢN', 'TỔNG TÀI SẢN'],
            'current_liabilities': ['NỢ NGẮN HẠN'],
            'long_term_debt': ['NỢ DÀI HẠN'],
            'total_liabilities': ['NỢ PHẢI TRẢ', 'TỔNG NỢ PHẢI TRẢ'],
            'equity': ['VỐN CHỦ SỞ HỮU', 'TỔNG VỐN CHỦ SỞ HỮU']
        }
        
        income_stmt_patterns = {
            'revenue': ['DOANH THU THUẦN', 'DOANH THU BÁN HÀNG VÀ CUNG CẤP DỊCH VỤ'],
            'operating_expense': ['CHI PHÍ HOẠT ĐỘNG', 'TỔNG CHI PHÍ HOẠT ĐỘNG'],
            'operating_income': ['LỢI NHUẬN THUẦN TỪ HOẠT ĐỘNG KINH DOANH', 'LỢI NHUẬN TỪ HOẠT ĐỘNG KINH DOANH', 'LỢI NHUẬN TỪ HĐKD'],
            'income_before_tax': ['Tổng lợi nhuận kế toán trước thuế', 'TỔNG LỢI NHUẬN TRƯỚC THUẾ'],
            'net_income': ['LỢI NHUẬN SAU THUẾ THU NHẬP DOANH NGHIỆP', 'LNST', 'LỢI NHUẬN SAU THUẾ'],
            'income_before_extra': ['LỢI NHUẬN TRƯỚC CÁC KHOẢN BẤT THƯỜNG', 'LỢI NHUẬN TRƯỚC KHOẢN BẤT THƯỜNG','Cổ đông của Công ty mẹ']
        }
        
        # Tạo DataFrame cho bảng cân đối kế toán
        balance_sheet_data = pd.DataFrame(index=years)
        for key, patterns in balance_sheet_patterns.items():
            for pattern in patterns:
                matches = df[df['Chỉ tiêu'].str.contains(pattern, case=False, na=False)]
                if not matches.empty:
                    balance_sheet_data.loc[:, key] = matches[years].iloc[0]
                    logger.info(f"Tìm thấy dữ liệu cho {key} với pattern '{pattern}'")
                    break
        
        # Tạo DataFrame cho báo cáo kết quả kinh doanh
        income_stmt_data = pd.DataFrame(index=years)
        for key, patterns in income_stmt_patterns.items():
            if key != 'operating_expense':  # Bỏ qua operating_expense vì sẽ tính sau
                for pattern in patterns:
                    matches = df[df['Chỉ tiêu'].str.contains(pattern, case=False, na=False)]
                    if not matches.empty:
                        income_stmt_data.loc[:, key] = matches[years].iloc[0]
                        logger.info(f"Tìm thấy dữ liệu cho {key} với pattern '{pattern}'")
                        break
        
        # Tính operating_expense = revenue - operating_income
        if 'revenue' in income_stmt_data.columns and 'operating_income' in income_stmt_data.columns:
            income_stmt_data['operating_expense'] = income_stmt_data['revenue'] - income_stmt_data['operating_income']
            logger.info("Đã tính Chi phí hoạt động = Doanh thu thuần - Lợi nhuận từ HĐKD")
        
        # Kiểm tra dữ liệu trước khi trả về
        if balance_sheet_data.empty:
            logger.error("Không tìm thấy dữ liệu bảng cân đối kế toán")
            return {}
        
        if income_stmt_data.empty:
            logger.error("Không tìm thấy dữ liệu báo cáo kết quả kinh doanh")
            return {}
        
        # Log thông tin về dữ liệu tìm thấy
        logger.info("Dữ liệu bảng cân đối kế toán:")
        logger.info(balance_sheet_data)
        logger.info("Dữ liệu báo cáo kết quả kinh doanh:")
        logger.info(income_stmt_data)
        
        return {
            'balance_sheet': balance_sheet_data,
            'income_stmt': income_stmt_data,
            'years': years
        }
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu tài chính: {e}")
        return {}
