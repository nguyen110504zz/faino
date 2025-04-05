import os
import sys
import logging
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from flask import Flask, render_template, request, jsonify, send_file
from Process.readdata import get_stock_info, get_financial_data, process_financial_data
from Process.calculate import calculate_financial_ratios, calculate_growth_rates
from Process.drawchart import create_financial_charts
from Process.ai_analyst import setup_gemini, analyze_financial_data, generate_recommendations
from Process.generate_report import generate_html_report, save_report
from Process.export_pdf import generate_pdf_report
# Temporarily disable PDF export
# from Process.export_pdf import generate_pdf_report

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = 'AIzaSyCFyqIp-sg4iqs3LMOoFNrgjlIlb-pPnQg'
model = setup_gemini(GEMINI_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    try:
        # Get form data instead of JSON
        symbol = request.form.get('stock_code')
        
        if not symbol:
            return jsonify({'error': 'Mã cổ phiếu là bắt buộc'}), 400
        
        # Get stock information
        stock_info = get_stock_info(symbol)
        if not stock_info:
            return jsonify({'error': 'Không thể lấy thông tin cổ phiếu'}), 404
        
        # Get financial data
        financial_data = get_financial_data(symbol)
        if not financial_data:
            return jsonify({'error': 'Không thể lấy dữ liệu tài chính'}), 404
        
        # Calculate financial metrics
        ratios = calculate_financial_ratios(financial_data)
        growth_rates = calculate_growth_rates(financial_data)
        
        # Create charts
        financial_charts = create_financial_charts(financial_data)
        
        # AI Analysis
        analysis = analyze_financial_data(model, financial_data, ratios, growth_rates)
        recommendations = generate_recommendations(model, analysis)
        
        # Generate report
        html_content = generate_html_report(
            stock_info,
            financial_data,
            ratios,
            growth_rates,
            financial_charts,
            analysis,
            recommendations
        )
        
        # Save report
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        html_path = os.path.join(report_dir, f'{symbol}_report.html')
        save_report(html_content, html_path)
        
        # Read the report content
        with open(html_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # Remove the HTML header and body tags from the report content
        report_content = report_content.replace('<!DOCTYPE html>', '')
        report_content = report_content.replace('<html lang="vi">', '')
        report_content = report_content.replace('<head>', '')
        report_content = report_content.replace('</head>', '')
        report_content = report_content.replace('<body>', '')
        report_content = report_content.replace('</body>', '')
        report_content = report_content.replace('</html>', '')
        
        # Redirect to the report page with content and symbol
        return render_template('report.html', report_content=report_content, symbol=symbol)
        
    except Exception as e:
        logger.error(f"Lỗi khi phân tích: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/download/<symbol>')
def download_report(symbol):
    try:
        # Get the report file path
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        html_path = os.path.join(report_dir, f'{symbol}_report.html')
        
        if not os.path.exists(html_path):
            return jsonify({'error': 'Không tìm thấy báo cáo'}), 404
            
        # Return the file as an attachment
        return send_file(
            html_path,
            as_attachment=True,
            download_name=f'Bao_cao_tai_chinh_{symbol}.html',
            mimetype='text/html'
        )
        
    except Exception as e:
        logger.error(f"Lỗi khi tải báo cáo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    try:
        # Process uploaded files
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400

        # Process financial data
        financial_data = process_financial_data(files)
        if not financial_data:
            return jsonify({'error': 'Error processing financial data'}), 400

        # Create charts
        charts = create_financial_charts(financial_data)
        if not charts:
            return jsonify({'error': 'Error creating charts'}), 400

        # Get AI analysis
        analysis = analyze_financial_data(financial_data)
        if not analysis:
            return jsonify({'error': 'Error generating AI analysis'}), 400

        # Generate report with PDF
        pdf_dir = os.path.join(app.static_folder, 'reports')
        os.makedirs(pdf_dir, exist_ok=True)
        
        report_path = generate_html_report(
            financial_data=financial_data,
            ai_analysis=analysis,
            financial_charts=charts,
            output_path=os.path.join(pdf_dir, 'report.html'),
            generate_pdf=True
        )
        
        if not report_path:
            return jsonify({'error': 'Error generating PDF report'}), 400

        # Return PDF file
        pdf_path = report_path.replace('.html', '.pdf')
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='financial_report.pdf'
        )

    except Exception as e:
        logger.error(f"Error in export-pdf route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        # Get the current report content from form data
        report_content = request.form.get('content')
        if not report_content:
            return jsonify({'error': 'Không có nội dung báo cáo'}), 400
            
        # Add necessary HTML wrapper if not present
        if not report_content.startswith('<!DOCTYPE html>'):
            report_content = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo cáo Phân tích Tài chính</title>
</head>
<body>
{report_content}
</body>
</html>'''
            
        # Generate PDF from the report content
        pdf_dir = os.path.join(app.static_folder, 'reports')
        os.makedirs(pdf_dir, exist_ok=True)
        
        pdf_path = os.path.join(pdf_dir, 'report.pdf')
        generate_pdf_report(report_content, pdf_path)
        
        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='bao_cao_tai_chinh.pdf'
        )
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 