import google.generativeai as genai
from typing import Dict, Any
import json
import pandas as pd
import numpy as np

def setup_gemini(api_key: str):
    """
    Setup Gemini API with the provided API key
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

def convert_to_json_serializable(obj):
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
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    return obj

def prepare_metrics(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare key metrics from financial data
    """
    metrics = {
        'revenue': [],
        'net_income': [],
        'total_assets': [],
        'total_liabilities': [],
        'equity': []
    }
    
    try:
        # Get data from the financial_data dictionary
        income_stmt = financial_data.get('income_stmt', {})
        balance_sheet = financial_data.get('balance_sheet', {})
        
        # Extract metrics from income statement
        if income_stmt:
            metrics['revenue'] = income_stmt.get('revenue', [])
            metrics['net_income'] = income_stmt.get('net_income', [])
        
        # Extract metrics from balance sheet
        if balance_sheet:
            metrics['total_assets'] = balance_sheet.get('total_assets', [])
            metrics['total_liabilities'] = balance_sheet.get('total_liabilities', [])
            metrics['equity'] = balance_sheet.get('equity', [])
    
    except Exception as e:
        print(f"Lỗi khi chuẩn bị chỉ số tài chính: {e}")
    
    return metrics

def get_response_text(response) -> str:
    """
    Safely extract text from Gemini API response and clean it up
    """
    try:
        if response is None:
            return "Không có dữ liệu"

        # In ra kiểu của response để debug    
        print(f"Kiểu của response: {type(response)}")
        
        # Lấy text từ response
        result = ""
        
        # Nếu response là GenerateContentResponse
        if str(type(response).__name__) == 'GenerateContentResponse':
            try:
                # Truy cập candidates[0] trước
                if hasattr(response, 'candidates') and response.candidates:
                    first_candidate = response.candidates[0]
                    if hasattr(first_candidate, 'content'):
                        content = first_candidate.content
                        if hasattr(content, 'parts') and content.parts:
                            # Đảm bảo parts là list và mỗi phần tử được chuyển thành string
                            result = ' '.join([str(part) for part in content.parts if part is not None])
            except Exception as e:
                print(f"Lỗi khi xử lý GenerateContentResponse: {e}")

        # Nếu response có thuộc tính text
        elif hasattr(response, 'text'):
            result = str(response.text) if response.text is not None else "Không có dữ liệu"

        # Nếu response là string
        elif isinstance(response, str):
            result = response
            
        # Nếu response là dict và có key 'text'
        elif isinstance(response, dict) and 'text' in response:
            result = str(response['text']) if response['text'] is not None else "Không có dữ liệu"

        # Thử chuyển đổi response thành string an toàn
        else:
            try:
                result = str(response)
            except:
                return "Không có dữ liệu"

        # Làm sạch kết quả
        if result:
            # Loại bỏ 'text: "' ở đầu nếu có
            if result.startswith('text: "'):
                result = result[7:]
            elif result.startswith('text:"'):
                result = result[6:]
            elif result.startswith('text: '):
                result = result[6:]
            elif result.startswith('text:'):
                result = result[5:]
                
            # Loại bỏ dấu ngoặc kép ở đầu nếu có
            if result.startswith('"'):
                result = result[1:]
            
            # Loại bỏ dấu ngoặc kép ở cuối nếu có
            if result.endswith('"'):
                result = result[:-1]
            
            # Loại bỏ \n và \
            result = result.replace('\\n', ' ')
            result = result.replace('\\', '')
            
            # Loại bỏ khoảng trắng thừa
            result = ' '.join(result.split())
            
            # Loại bỏ dấu ngoặc kép thừa ở giữa câu
            result = result.replace(' " ', ' ')
            result = result.replace('" ', ' ')
            result = result.replace(' "', ' ')
            
        return result if result else "Không có dữ liệu"
            
    except Exception as e:
        print(f"Lỗi khi xử lý response: {e}")
        print(f"Response type: {type(response)}")
        print(f"Response value: {str(response)}")
        return "Không có dữ liệu"

def analyze_financial_data(model, financial_data: Dict[str, Any], ratios: Dict[str, float], 
                         growth_rates: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze financial data using Gemini AI
    """
    try:
        # Convert data to JSON serializable format
        serializable_ratios = convert_to_json_serializable(ratios)
        serializable_growth_rates = convert_to_json_serializable(growth_rates)
        key_metrics = prepare_metrics(financial_data)
        
        # Prepare the data for analysis
        analysis_data = {
            'financial_ratios': serializable_ratios,
            'growth_rates': serializable_growth_rates,
            'key_metrics': key_metrics
        }

        # Create prompts for different sections
        prompts = {
            'financial_summary': f"""
            You are a financial expert. Please write a detailed paragraph (no more than 4 sentences, natural language, professional, no effects) about the company's financial situation based on:

            Revenue and profit:
            {json.dumps(key_metrics, indent=2, ensure_ascii=False)}
            
            Growth rates:
            {json.dumps(serializable_growth_rates, indent=2, ensure_ascii=False)}
            """,
            
            'balance_sheet_analysis': f"""
            You are a financial expert. Please analyze in detail (no more than 4 sentences, natural language, professional, no effects) the following balance sheet data:

            1. Data:
            {json.dumps(convert_to_json_serializable(financial_data.get('balance_sheet', pd.DataFrame())), indent=2, ensure_ascii=False)}

            Requirements:
            Please analyze the indicators in the balance sheet (no more than 6 sentences, natural language, professional, no effects)
            """,
            
            'fundamental_analysis': f"""
            You are a financial expert. Please write a detailed paragraph (no more than 6 sentences, natural language, professional, no effects) about fundamental indicators based on:
            
            Financial ratios:
            {json.dumps(serializable_ratios, indent=2, ensure_ascii=False)}
            """,
            
            'income_statement_analysis': f"""
            You are a financial expert. Please write a detailed paragraph (no more than 6 sentences, natural language, professional, no effects) about business results based on:
            
            Revenue and profit:
            {json.dumps(key_metrics, indent=2, ensure_ascii=False)}
            
            Growth rates:
            {json.dumps(serializable_growth_rates, indent=2, ensure_ascii=False)}
            """,
            
            'profitability_analysis': f"""
             You are a financial expert. Please write a brief and focused paragraph (no more than 4 sentences, natural language, professional) about profitability based on:
            
             Profitability ratios:
             {json.dumps(serializable_ratios, indent=2, ensure_ascii=False)}
             """
        }

        # Generate analysis for each section
        analysis = {}
        for section, prompt in prompts.items():
            try:
                print(f"\nAnalyzing section: {section}")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 512,  # Reduced token limit for more concise responses
                    }
                )
                result = get_response_text(response)
                print(f"Analysis result for {section}: {result}")
                
                # Add default value if result is empty or None
                if not result or result == "No data":
                    if section == 'financial_summary':
                        result = "Insufficient data available for comprehensive financial analysis."
                    elif section == 'balance_sheet_analysis':
                        result = "Insufficient data available for balance sheet analysis."
                    elif section == 'income_statement_analysis':
                        result = "Insufficient data available for income statement analysis."
                    elif section == 'profitability_analysis':
                        result = "Insufficient data available for profitability analysis."
                    else:
                        result = "Insufficient data available for analysis."
                        
                analysis[section] = result
            except Exception as e:
                print(f"Error analyzing section {section}: {e}")
                analysis[section] = "Error in analysis process"
        
        # Add summary metrics with error handling
        try:
            analysis['summary'] = {
                'financial_health': 'Good' if serializable_ratios.get('current_ratio', 0) > 2 else 'Average',
                'growth_potential': 'High' if serializable_growth_rates.get('revenue_growth', 0) > 10 else 'Average',
                'risk_level': 'Low' if serializable_ratios.get('debt_to_equity', 0) < 1 else 'High'
            }
        except Exception as e:
            print(f"Error creating summary metrics: {e}")
            analysis['summary'] = {
                'financial_health': 'Undetermined',
                'growth_potential': 'Undetermined',
                'risk_level': 'Undetermined'
            }
        
        return analysis
        
    except Exception as e:
        print(f"Error in AI analysis process: {e}")
        return {
            'financial_summary': 'Insufficient data available for comprehensive financial analysis.',
            'balance_sheet_analysis': 'Insufficient data available for balance sheet analysis.',
            'fundamental_analysis': 'Insufficient data available for analysis.',
            'income_statement_analysis': 'Insufficient data available for income statement analysis.',
            'profitability_analysis': 'Insufficient data available for profitability analysis.',
            'summary': {
                'financial_health': 'Undetermined',
                'growth_potential': 'Undetermined',
                'risk_level': 'Undetermined'
            }
        }

def generate_recommendations(model, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate investment recommendations based on the analysis (no effects)
    """
    try:
        # Extract key metrics for recommendations
        financial_health = analysis.get('summary', {}).get('financial_health', 'Average')
        growth_potential = analysis.get('summary', {}).get('growth_potential', 'Average')
        risk_level = analysis.get('summary', {}).get('risk_level', 'Medium')
        
        # Create a focused prompt with key information
        prompt = f"""
        You are a financial expert. Based on the following key metrics:
        - Financial Health: {financial_health}
        - Growth Potential: {growth_potential}
        - Risk Level: {risk_level}

        And considering these analyses:
        - Financial Summary: {analysis.get('financial_summary', '')}
        - Profitability Analysis: {analysis.get('profitability_analysis', '')}

        Please provide a clear investment recommendation in 3-4 sentences that includes (no effects bold):
        1. Overall investment stance (Buy/Hold/Sell)
        2. Key reasons for the recommendation
        3. Main risks to consider
        """
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 512,
        }
        
        try:
            print("\nGenerating investment recommendations...")
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            recommendations_text = get_response_text(response)
            
            # If recommendation is empty or error, generate a basic recommendation
            if not recommendations_text or recommendations_text == "Unable to generate recommendations":
                recommendations_text = f"Based on the financial health being {financial_health} and growth potential being {growth_potential}, with {risk_level} risk level, we recommend a cautious approach. Consider the company's current market position and industry trends before making investment decisions. Monitor key financial metrics and market conditions closely."
            
            print(f"Investment recommendations: {recommendations_text}")
            
            # Adjust risk management based on risk level
            stop_loss = '3%' if risk_level == 'Low' else ('5%' if risk_level == 'Medium' else '8%')
            take_profit = '10%' if risk_level == 'Low' else ('15%' if risk_level == 'Medium' else '20%')
            position_size = '5%' if risk_level == 'Low' else ('3%' if risk_level == 'Medium' else '2%')
            
            return {
                'recommendations': recommendations_text,
                'risk_management': {
                    'stop_loss': f'{stop_loss} below current price',
                    'take_profit': f'{take_profit} above current price',
                    'position_size': f'{position_size} of portfolio'
                }
            }
            
        except Exception as e:
            print(f"Error in API call: {e}")
            # Provide a basic recommendation based on summary metrics
            basic_recommendation = f"Based on our analysis showing {financial_health} financial health and {growth_potential} growth potential, investors should take a balanced approach. Consider the {risk_level} risk level and current market conditions before making investment decisions."
            
            return {
                'recommendations': basic_recommendation,
                'risk_management': {
                    'stop_loss': '5% below current price',
                    'take_profit': '15% above current price',
                    'position_size': '3% of portfolio'
                }
            }
        
    except Exception as e:
        print(f"Error in recommendation generation: {e}")
        return {
            'recommendations': 'Based on available data, we recommend a cautious approach. Monitor market conditions and company performance closely before making investment decisions.',
            'risk_management': {
                'stop_loss': '5% below current price',
                'take_profit': '15% above current price',
                'position_size': '2-3% of portfolio'
            }
        } 