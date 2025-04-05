#%%
import numpy as np
import pandas as pd
from typing import Dict, Any
#%%
# Hàm lấy giá trị từ transposed_df
def get_values(transposed_df, label):
    row = transposed_df[transposed_df["Chỉ tiêu"] == label]
    return row.iloc[:, 1:].values.flatten() if not row.empty else np.zeros(len(transposed_df.columns[1:]))

# Các chỉ tiêu cần thiết
labels = {
    "total_current_assets": [
        "CĐKT. TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN",
        "CĐKT. ĐẦU TƯ TÀI CHÍNH NGẮN HẠN",
        "CĐKT. CÁC KHOẢN PHẢI THU NGẮN HẠN",
        "CĐKT. HÀNG TỒN KHO, RÒNG",
        "CĐKT. TÀI SẢN NGẮN HẠN KHÁC"
    ],
    "ppe": [
        "CĐKT. GTCL TSCĐ HỮU HÌNH",
        "CĐKT. GTCL TÀI SẢN THUÊ TÀI CHÍNH",
        "CĐKT. GTCL TÀI SẢN CỐ ĐỊNH VÔ HÌNH",
        "CĐKT. XÂY DỰNG CƠ BẢN DỞ DANG (TRƯỚC 2015)"
    ],
    "total_assets": [
        "CĐKT. TÀI SẢN NGẮN HẠN",
        "CĐKT. TÀI SẢN DÀI HẠN"
    ],
    "total_current_liabilities": ["CĐKT. NỢ NGẮN HẠN"],
    "total_long_term_debt": ["CĐKT. NỢ DÀI HẠN"],
    "total_liabilities": ["CĐKT. NỢ PHẢI TRẢ"],
    "net_income": ["KQKD. LỢI NHUẬN SAU THUẾ THU NHẬP DOANH NGHIỆP"],
    "interest_expense": ["KQKD. CHI PHÍ LÃI VAY"],
    "taxes": ["KQKD. CHI PHÍ THUẾ TNDN HIỆN HÀNH"],
    "depreciation_amortization": ["KQKD. KHẤU HAO TÀI SẢN CỐ ĐỊNH"],
    "revenue": ["KQKD. DOANH THU THUẦN"],
    "gross_profit": ["KQKD. LỢI NHUẬN GỘP VỀ BÁN HÀNG VÀ CUNG CẤP DỊCH VỤ"],
    "financial_expense": ["KQKD. CHI PHÍ TÀI CHÍNH"],
    "selling_expense": ["KQKD. CHI PHÍ BÁN HÀNG"],
    "admin_expense": ["KQKD. CHI PHÍ QUẢN LÝ DOANH NGHIỆP"],
    "total_equity": ["CĐKT. VỐN CHỦ SỞ HỮU"],
    "total_debt": ["CĐKT. NỢ PHẢI TRẢ"],
    "operating_profit": ["KQKD. LỢI NHUẬN THUẦN TỪ HOẠT ĐỘNG KINH DOANH"],
    "other_profit": ["KQKD. LỢI NHUẬN KHÁC"],
    "jv_profit": ["KQKD. LÃI/ LỖ TỪ CÔNG TY LIÊN DOANH (TRƯỚC 2015)"],
    "other_income": ["KQKD. LỢI NHUẬN KHÁC"]
}
#%%
# Hàm tính các chỉ số
def calculate_financial_ratios(financial_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    Calculate key financial ratios
    """
    ratios = {}
    
    try:
        balance_sheet = financial_data.get('balance_sheet', pd.DataFrame())
        income_stmt = financial_data.get('income_stmt', pd.DataFrame())
        
        if not balance_sheet.empty and not income_stmt.empty:
            # Lấy dữ liệu năm gần nhất (2024)
            current_year = '2024'
            
            # Current Ratio
            current_assets = balance_sheet['total_assets'][current_year]
            current_liabilities = balance_sheet['total_liabilities'][current_year]
            ratios['current_ratio'] = float(current_assets) / float(current_liabilities) if float(current_liabilities) != 0 else 0
            
            # Debt to Equity Ratio
            total_debt = balance_sheet['total_liabilities'][current_year]
            total_equity = balance_sheet['equity'][current_year]
            ratios['debt_to_equity'] = float(total_debt) / float(total_equity) if float(total_equity) != 0 else 0
            
            # Return on Equity (ROE)
            net_income = income_stmt['net_income'][current_year]
            ratios['roe'] = float(net_income) / float(total_equity) if float(total_equity) != 0 else 0
            
            # Profit Margin
            revenue = income_stmt['revenue'][current_year]
            ratios['profit_margin'] = float(net_income) / float(revenue) if float(revenue) != 0 else 0
            
    except Exception as e:
        print(f"Error calculating financial ratios: {e}")
        # Set default values if calculation fails
        ratios = {
            'current_ratio': 0,
            'debt_to_equity': 0,
            'roe': 0,
            'profit_margin': 0
        }
    
    return ratios

def calculate_growth_rates(financial_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    Calculate year-over-year growth rates
    """
    growth_rates = {}
    
    try:
        income_stmt = financial_data.get('income_stmt', pd.DataFrame())
        
        if not income_stmt.empty:
            # Lấy dữ liệu 2 năm gần nhất
            current_year = '2024'
            previous_year = '2023'
            
            # Revenue Growth
            current_revenue = float(income_stmt['revenue'][current_year])
            previous_revenue = float(income_stmt['revenue'][previous_year])
            if previous_revenue != 0:
                growth_rates['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue) * 100
            else:
                growth_rates['revenue_growth'] = 0
            
            # Net Income Growth
            current_net_income = float(income_stmt['net_income'][current_year])
            previous_net_income = float(income_stmt['net_income'][previous_year])
            if previous_net_income != 0:
                growth_rates['net_income_growth'] = ((current_net_income - previous_net_income) / previous_net_income) * 100
            else:
                growth_rates['net_income_growth'] = 0
            
    except Exception as e:
        print(f"Error calculating growth rates: {e}")
        # Set default values if calculation fails
        growth_rates = {
            'revenue_growth': 0,
            'net_income_growth': 0
        }
    
    return growth_rates

def calculate_technical_indicators(historical_data: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Calculate technical indicators
    """
    indicators = {}
    
    try:
        if not historical_data.empty:
            # Calculate Moving Averages
            indicators['sma_20'] = historical_data['Close'].rolling(window=20).mean()
            indicators['sma_50'] = historical_data['Close'].rolling(window=50).mean()
            
            # Calculate RSI
            delta = historical_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
    except Exception as e:
        print(f"Error calculating technical indicators: {e}")
    
    return indicators
