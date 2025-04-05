from jinja2 import Environment, FileSystemLoader
import json
from typing import Dict, Any, Optional
import os
import pandas as pd
import numpy as np
import logging
from .export_pdf import generate_pdf_report
from .drawchart import create_price_charts

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_jinja_env():
    """
    Setup Jinja2 environment with templates directory
    """
    # Change template directory to App/templates
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'App', 'templates')
    return Environment(loader=FileSystemLoader(template_dir))

def convert_to_serializable(obj):
    """
    Convert various data types to JSON serializable format
    """
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int64, np.float64)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    return obj

def prepare_financial_data(financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Prepare financial data for the template by converting Pandas objects to Python native types
    """
    prepared_data = {
        'years': ['2020', '2021', '2022', '2023', '2024'],
        'balance_sheet': {
            'current_assets': [],
            'fixed_assets': [],
            'total_assets': [],
            'current_liabilities': [],
            'long_term_debt': [],
            'total_liabilities': [],
            'equity': []
        },
        'income_stmt': {
            'revenue': [],                  # Doanh thu thuần
            'operating_expense': [],        # Chi phí hoạt động
            'operating_income': [],         # Lợi nhuận từ HĐKD
            'income_before_tax': [],        # Lợi nhuận trước thuế
            'net_income': [],              # Lợi nhuận sau thuế
            'income_before_extra': []       # Lợi nhuận trước các khoản bất thường
        },
        'profitability': {
            'income_after_tax_margin': [],  # Tỷ suất lợi nhuận sau thuế
            'long_term_debt_equity': [],    # Tỷ suất nợ dài hạn/vốn CSH
            'roa': [],                      # ROA
            'roe': [],                      # ROE
            'revenue_total_assets': [],     # Doanh thu/Tổng tài sản
            'total_debt_equity': []         # Tổng nợ/Vốn CSH
        }
    }
    
    try:
        income_stmt = financial_data.get('income_stmt', pd.DataFrame())
        balance_sheet = financial_data.get('balance_sheet', pd.DataFrame())
        
        # Get balance sheet data
        if not balance_sheet.empty:
            balance_sheet_mapping = {
                'current_assets': 'current_assets',
                'fixed_assets': 'fixed_assets', 
                'total_assets': 'total_assets',
                'current_liabilities': 'current_liabilities',
                'long_term_debt': 'long_term_debt',
                'total_liabilities': 'total_liabilities',
                'equity': 'equity'
            }
            
            for df_col, prep_key in balance_sheet_mapping.items():
                if df_col in balance_sheet.columns:
                    prepared_data['balance_sheet'][prep_key] = balance_sheet[df_col].astype(float).tolist()
                else:
                    prepared_data['balance_sheet'][prep_key] = [0] * len(prepared_data['years'])
        
        # Get income statement data
        if not income_stmt.empty:
            income_stmt_mapping = {
                'revenue': 'revenue',
                'operating_expense': 'operating_expense',
                'operating_income': 'operating_income',
                'income_before_tax': 'income_before_tax',
                'net_income': 'net_income',
                'income_before_extra': 'income_before_extra'
            }
            
            for df_col, prep_key in income_stmt_mapping.items():
                if df_col in income_stmt.columns:
                    prepared_data['income_stmt'][prep_key] = income_stmt[df_col].astype(float).tolist()
                else:
                    prepared_data['income_stmt'][prep_key] = [0] * len(prepared_data['years'])
        
        # Calculate profitability ratios
        for i in range(len(prepared_data['years'])):
            net_income = prepared_data['income_stmt']['net_income'][i]
            revenue = prepared_data['income_stmt']['revenue'][i]
            total_assets = prepared_data['balance_sheet']['total_assets'][i]
            equity = prepared_data['balance_sheet']['equity'][i]
            long_term_debt = prepared_data['balance_sheet']['long_term_debt'][i]
            total_liabilities = prepared_data['balance_sheet']['total_liabilities'][i]
            
            # Tỷ suất lợi nhuận sau thuế (%)
            income_after_tax_margin = (net_income / revenue * 100) if revenue != 0 else 0
            prepared_data['profitability']['income_after_tax_margin'].append(income_after_tax_margin)
            
            # Tỷ suất nợ dài hạn/vốn CSH (%)
            long_term_debt_equity = (long_term_debt / equity * 100) if equity != 0 else 0
            prepared_data['profitability']['long_term_debt_equity'].append(long_term_debt_equity)
            
            # ROA (%)
            roa = (net_income / total_assets * 100) if total_assets != 0 else 0
            prepared_data['profitability']['roa'].append(roa)
            
            # ROE (%)
            roe = (net_income / equity * 100) if equity != 0 else 0
            prepared_data['profitability']['roe'].append(roe)
            
            # Doanh thu/Tổng tài sản (lần)
            revenue_total_assets = revenue / total_assets if total_assets != 0 else 0
            prepared_data['profitability']['revenue_total_assets'].append(revenue_total_assets)
            
            # Tổng nợ/Vốn CSH (%)
            total_debt_equity = (total_liabilities / equity * 100) if equity != 0 else 0
            prepared_data['profitability']['total_debt_equity'].append(total_debt_equity)
    
    except Exception as e:
        print(f"Lỗi khi chuẩn bị dữ liệu tài chính: {e}")
        # Initialize with empty lists if there's an error
        for section in ['income_stmt', 'balance_sheet', 'profitability']:
            for key in prepared_data[section]:
                if not prepared_data[section][key]:
                    prepared_data[section][key] = [0] * len(prepared_data['years'])
    
    return prepared_data

def prepare_ratios(ratios: Dict[str, Any]) -> Dict[str, list]:
    """
    Prepare ratios data for the template
    """
    prepared_ratios = {
        'roe': [],
        'roa': [],
        'profit_margin': []
    }
    
    try:
        # Convert single values to lists if necessary
        for key in prepared_ratios:
            if key in ratios:
                value = ratios[key]
                if isinstance(value, (float, int, np.float64, np.int64)):
                    prepared_ratios[key] = [float(value)]
                elif isinstance(value, (list, np.ndarray, pd.Series)):
                    prepared_ratios[key] = [float(x) for x in value]
    except Exception as e:
        print(f"Lỗi khi chuẩn bị tỷ lệ tài chính: {e}")
    
    return prepared_ratios

def generate_html_report(stock_info: Dict[str, Any], 
                        financial_data: Dict[str, Any],
                        ratios: Dict[str, float],
                        growth_rates: Dict[str, float],
                        financial_charts: Dict[str, str],
                        analysis: Dict[str, Any],
                        recommendations: Dict[str, Any],
                        output_path: Optional[str] = None,
                        generate_pdf: bool = False) -> Optional[str]:
    """
    Generate HTML report and optionally export to PDF
    """
    try:
        env = setup_jinja_env()
        template = env.get_template('report_template.html')
        
        # Convert all data to serializable format
        stock_info = convert_to_serializable(stock_info)
        prepared_financial_data = prepare_financial_data(financial_data)
        prepared_ratios = prepare_ratios(ratios)
        growth_rates = convert_to_serializable(growth_rates)
        
        # Ensure charts is a dictionary
        if not isinstance(financial_charts, dict):
            financial_charts = {}
            
        # Create price charts
        price_charts = create_price_charts(stock_info.get('symbol', ''))
        
        # Prepare data for template
        report_data = {
            'stock_info': stock_info,
            'financial_data': prepared_financial_data,
            'ratios': prepared_ratios,
            'growth_rates': growth_rates,
            'financial_charts': financial_charts,
            'price_charts': price_charts,
            'analysis': analysis,
            'recommendations': recommendations,
            'current_date': pd.Timestamp.now().strftime('%Y-%m-%d')
        }
        
        # Render template
        html_content = template.render(**report_data)
        
        # Default output path if none provided - save to App/templates
        if output_path is None:
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'App', 'templates', 'report.html')
            
        # Also save a copy to reports directory
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'App', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, f"{stock_info.get('symbol', 'report')}_report.html")
        
        # Save both copies
        for path in [output_path, report_path]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML report generated at: {path}")
        
        # Generate PDF if requested
        if generate_pdf:
            pdf_path = output_path.replace('.html', '.pdf')
            if generate_pdf_report(output_path, pdf_path):
                logger.info(f"PDF report generated at: {pdf_path}")
            else:
                logger.error("Failed to generate PDF report")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None

def save_report(html_content: str, output_path: str):
    """
    Save the generated HTML report to a file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Đã lưu báo cáo thành công tại {output_path}")
    except Exception as e:
        print(f"Lỗi khi lưu báo cáo: {e}") 