# Financial Analysis System

A comprehensive financial analysis system that provides detailed analysis of stocks using financial data, technical indicators, and AI-powered insights.

## Features

- Stock information retrieval
- Financial data analysis
- Technical indicator calculations
- Interactive charts and visualizations
- AI-powered financial analysis using Google's Gemini
- Professional HTML report generation
- PDF report export
- Web interface for easy access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-analysis-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Gemini API key:
```bash
export GEMINI_API_KEY=AIzaSyCFyqIp-sg4iqs3LMOoFNrgjlIlb-pPnQg  # On Windows: set GEMINI_API_KEY=your-api-key-here
```

## Usage

1. Start the web application:
```bash
python App/app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter a stock symbol (e.g., AAPL, GOOGL, MSFT) and click "Analyze"

4. View the generated report and download it as PDF if needed

## Project Structure

```
.
├── App/
│   ├── app.py              # Flask web application
│   ├── templates/          # HTML templates
│   └── reports/           # Generated reports
├── Process/
│   ├── readdata.py        # Data retrieval functions
│   ├── calculate.py       # Financial calculations
│   ├── drawchart.py       # Chart generation
│   ├── ai_analyst.py      # AI analysis using Gemini
│   ├── generate_report.py # HTML report generation
│   └── export_pdf.py      # PDF export functionality
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Dependencies

- Flask: Web framework
- Pandas: Data manipulation
- NumPy: Numerical computations
- yfinance: Stock data retrieval
- Plotly: Interactive charts
- Jinja2: HTML templating
- WeasyPrint: PDF generation
- Google Generative AI: AI analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 