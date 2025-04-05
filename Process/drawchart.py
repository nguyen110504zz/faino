import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any
import json
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime, timedelta

def read_price_data(symbol: str) -> pd.DataFrame:
    """Read price data from CSV file"""
    try:
        # Đọc dữ liệu từ file CSV (giả sử file được lưu trong thư mục Data)
        file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', f'{symbol}_prices.csv')
        df = pd.read_csv(file_path)
        
        # Chuyển đổi cột ngày thành datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sắp xếp theo ngày
        df = df.sort_values('Date')
        
        return df
    except Exception as e:
        print(f"Error reading price data: {e}")
        return pd.DataFrame()

def create_price_charts(symbol: str) -> dict:
    """Create 6-month and 5-year price charts"""
    try:
        # Đọc dữ liệu giá
        df = read_price_data(symbol)
        if df.empty:
            return {}

        # Tạo thư mục charts nếu chưa tồn tại
        charts_dir = os.path.join(os.path.dirname(__file__), '..', 'App', 'static', 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Lấy ngày hiện tại
        latest_date = df['Date'].max()

        # Tạo biểu đồ 6 tháng
        six_months_ago = latest_date - timedelta(days=180)
        df_6m = df[df['Date'] >= six_months_ago]
        
        plt.figure(figsize=(10, 6))
        plt.plot(df_6m['Date'], df_6m['Close'], color='blue')
        plt.title(f'{symbol} - 6 Months Price Chart')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Lưu biểu đồ 6 tháng
        six_month_path = os.path.join(charts_dir, f'{symbol}_6m.png')
        plt.savefig(six_month_path)
        plt.close()

        # Tạo biểu đồ 5 năm
        five_years_ago = latest_date - timedelta(days=1825)
        df_5y = df[df['Date'] >= five_years_ago]
        
        plt.figure(figsize=(10, 6))
        plt.plot(df_5y['Date'], df_5y['Close'], color='blue')
        plt.title(f'{symbol} - 5 Years Price Chart')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Lưu biểu đồ 5 năm
        five_year_path = os.path.join(charts_dir, f'{symbol}_5y.png')
        plt.savefig(five_year_path)
        plt.close()

        return {
            'six_months': f'charts/{symbol}_6m.png',
            'five_years': f'charts/{symbol}_5y.png'
        }
    except Exception as e:
        print(f"Error creating price charts: {e}")
        return {}

def create_financial_charts(financial_data):
    """Create and save financial charts"""
    try:
        plt.switch_backend('Agg')  # Ensure we're using Agg backend
        
        # Create charts directory if not exists
        charts_dir = os.path.join(os.path.dirname(__file__), '..', 'App', 'static', 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Get data
        years = [str(year) for year in range(2020, 2025)]
        
        # Balance Sheet data
        total_assets = financial_data['balance_sheet']['total_assets']
        equity = financial_data['balance_sheet']['equity']
        total_liabilities = [total_assets[i] - equity[i] for i in range(len(total_assets))]

        # Income Statement data
        revenue = financial_data['income_stmt']['revenue']
        operating_expense = financial_data['income_stmt']['operating_expense']
        operating_income = financial_data['income_stmt']['operating_income']
        net_income = financial_data['income_stmt']['net_income']

        # Convert Balance Sheet data to billions for better display
        total_assets = [x/1e12 for x in total_assets]
        equity = [x/1e12 for x in equity]
        total_liabilities = [x/1e12 for x in total_liabilities]

        # Convert Income Statement data to billions for better display
        revenue = [x/1e12 for x in revenue]
        operating_expense = [x/1e12 for x in operating_expense]
        operating_income = [x/1e12 for x in operating_income]
        net_income = [x/1e12 for x in net_income]

        # Chart 1: Total Assets and Equity Over Time
        fig, ax1 = plt.subplots(figsize=(10, 8))

        # Plot total assets
        ax1.plot(years, total_assets, 'b-', linewidth=2, marker='o', label='Tổng tài sản (Ngàn tỷ VND)')
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Tổng tài sản (Ngàn tỷ VND)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        # Set y-axis limits for total assets with more padding
        min_assets = min(total_assets) * 0.80  # Increased padding to 20%
        max_assets = max(total_assets) * 1.20
        ax1.set_ylim(min_assets, max_assets)

        # Create second y-axis for equity
        ax2 = ax1.twinx()
        ax2.plot(years, equity, 'g--', linewidth=2, marker='o', label='Vốn chủ sở hữu (Ngàn tỷ VND)')
        ax2.set_ylabel('Vốn chủ sở hữu (Ngàn tỷ VND)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        # Set y-axis limits for equity with more padding
        min_equity = min(equity) * 0.80  # Increased padding to 20%
        max_equity = max(equity) * 1.20
        ax2.set_ylim(min_equity, max_equity)

        # Add value labels for both lines with adjusted vertical position
        for i, v in enumerate(total_assets):
            ax1.text(i, v + (max_assets - min_assets) * 0.02, f'{v:.1f}', ha='center', va='bottom')
        for i, v in enumerate(equity):
            ax2.text(i, v - (max_equity - min_equity) * 0.02, f'{v:.1f}', ha='center', va='top')

        # Add title and grid
        plt.title('Xu hướng Tổng tài sản và Vốn chủ sở hữu')
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Save chart 1
        chart1_path = os.path.join(charts_dir, 'assets_equity_trend.png')
        plt.savefig(chart1_path, bbox_inches='tight', dpi=300, facecolor='white')
        plt.close(fig)

        # Chart 2: Stacked Bar Chart for Liabilities and Equity
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create stacked bar chart
        ax.bar(years, total_liabilities, label='Tổng nợ phải trả', color='orange')
        ax.bar(years, equity, bottom=total_liabilities, label='Vốn chủ sở hữu', color='green')

        # Add value labels
        for i, v in enumerate(total_liabilities):
            ax.text(i, v/2, f'{v:.1f}', ha='center', va='center')
        for i, v in enumerate(equity):
            ax.text(i, total_liabilities[i] + v/2, f'{v:.1f}', ha='center', va='center')

        # Customize chart
        ax.set_title('Cơ cấu Nguồn vốn')
        ax.set_xlabel('Năm')
        ax.set_ylabel('Giá trị (Ngàn tỷ VND)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)

        # Save chart 2
        chart2_path = os.path.join(charts_dir, 'liabilities_equity_stacked.png')
        plt.savefig(chart2_path, bbox_inches='tight', dpi=300, facecolor='white')
        plt.close(fig)

        # Chart 3: Revenue and Net Income Trend
        fig, ax1 = plt.subplots(figsize=(10, 8))

        # Plot revenue
        ax1.plot(years, revenue, 'b-', linewidth=2, marker='o', label='Doanh thu (Ngàn tỷ VND)')
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Doanh thu (Ngàn tỷ VND)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        # Set y-axis limits for revenue with more padding
        min_revenue = min(revenue) * 0.80
        max_revenue = max(revenue) * 1.20
        ax1.set_ylim(min_revenue, max_revenue)

        # Create second y-axis for net income
        ax2 = ax1.twinx()
        
        # Plot net income with different colors based on value
        for i in range(len(years)-1):
            color = 'g' if net_income[i] >= 0 else 'r'
            ax2.plot([years[i], years[i+1]], [net_income[i], net_income[i+1]], 
                    color=color, linestyle='--', linewidth=2, marker='o')
        
        # Add last point with appropriate color
        color = 'g' if net_income[-1] >= 0 else 'r'
        ax2.plot(years[-1], net_income[-1], color=color, marker='o')
        
        # Set y-axis limits for net income with more padding
        padding_factor = 0.20
        min_income = min(net_income)
        max_income = max(net_income)
        income_range = max_income - min_income
        
        y2_min = min_income - (income_range * padding_factor)
        y2_max = max_income + (income_range * padding_factor)
        ax2.set_ylim(y2_min, y2_max)

        ax2.set_ylabel('Lợi nhuận sau thuế (Ngàn tỷ VND)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        # Add value labels for both lines
        for i, v in enumerate(revenue):
            label_offset = (max_revenue - min_revenue) * 0.02
            ax1.text(i, v + label_offset, f'{v:.1f}', ha='center', va='bottom')

        for i, v in enumerate(net_income):
            if v >= 0:
                label_offset = income_range * 0.02
                va_position = 'bottom'
            else:
                label_offset = -income_range * 0.02
                va_position = 'top'
            ax2.text(i, v + label_offset, f'{v:.1f}', ha='center', va=va_position)

        # Add title and grid
        plt.title('Xu hướng Doanh thu và Lợi nhuận sau thuế')
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Add legend with custom colors
        line1 = ax1.lines[0]
        line2_pos = plt.Line2D([], [], color='g', linestyle='--', marker='o', label='Lợi nhuận dương (Ngàn tỷ VND)')
        line2_neg = plt.Line2D([], [], color='r', linestyle='--', marker='o', label='Lợi nhuận âm (Ngàn tỷ VND)')
        ax1.legend([line1, line2_pos, line2_neg], 
                  [line1.get_label(), 'Lợi nhuận dương (Ngàn tỷ VND)', 'Lợi nhuận âm (Ngàn tỷ VND)'], 
                  loc='upper left')

        # Save chart 3
        chart3_path = os.path.join(charts_dir, 'revenue_income_trend.png')
        plt.savefig(chart3_path, bbox_inches='tight', dpi=300, facecolor='white')
        plt.close(fig)

        # Chart 4: Income Structure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create stacked bar chart showing revenue structure
        ax.bar(years, operating_expense, label='Chi phí hoạt động', color='orange')
        
        # Plot operating income with different colors based on value
        bottom = operating_expense
        for i, value in enumerate(operating_income):
            color = 'g' if value >= 0 else 'r'
            ax.bar(years[i], value, bottom=bottom[i], 
                   color=color, 
                   label='Lợi nhuận từ HĐKD' if i == 0 else "")
        
        # Create custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='orange', label='Chi phí hoạt động'),
            Patch(facecolor='g', label='Lợi nhuận dương từ HĐKD'),
            Patch(facecolor='r', label='Lợi nhuận âm từ HĐKD')
        ]

        # Add value labels on top of bars
        for i, v in enumerate(revenue):
            ax.text(i, v, f'{v:.1f}', ha='center', va='bottom')
            
        # Customize chart
        ax.set_title('Cơ cấu Kết quả Kinh doanh')
        ax.set_xlabel('Năm')
        ax.set_ylabel('Giá trị (Ngàn tỷ VND)')
        ax.legend(handles=legend_elements, loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.3)

        # Save chart 4
        chart4_path = os.path.join(charts_dir, 'income_structure.png')
        plt.savefig(chart4_path, bbox_inches='tight', dpi=300, facecolor='white')
        plt.close(fig)

        print(f"Charts saved successfully in {charts_dir}")
        
        return {
            'assets_equity_trend': 'charts/assets_equity_trend.png',
            'liabilities_equity_stacked': 'charts/liabilities_equity_stacked.png',
            'revenue_income_trend': 'charts/revenue_income_trend.png',
            'income_structure': 'charts/income_structure.png'
        }

    except Exception as e:
        print(f"Error creating charts: {str(e)}")
        return {
            'assets_equity_trend': '',
            'liabilities_equity_stacked': '',
            'revenue_income_trend': '',
            'income_structure': ''
        }
