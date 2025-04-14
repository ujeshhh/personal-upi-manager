import gradio as gr
import PyPDF2
import google.generativeai as genai
import re
import tempfile
import os

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyDnx_qUjGTFG1pv1otPUhNt_bGGv14aMDI"
genai.configure(api_key=GEMINI_API_KEY)

# 📄 Extract text from PDF
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        print("PDF Extraction Error:", e)
        return ""

# ✂️ Extract sections from full text using regex
def extract_section(full_text, label):
    pattern = rf"\*\*\- {re.escape(label)}:\*\*\s*(.*?)(?=\n\*\*|\Z)"
    match = re.search(pattern, full_text, re.DOTALL)
    return match.group(1).strip() if match else "❓ Not found"

# 🧠 Main function to analyze financial data
def analyze_financial_data(file):
    text = extract_text_from_pdf(file)

    if not text:
        return (
            "⚠️ Failed to extract text. Ensure it’s a text-based PDF.",
            "", "", "", "", "", "", "", None
        )

    prompt = f"""
    Analyze the following Paytm transaction history and generate financial insights in the following structure:
    **Financial Insights**
    **- Monthly Income & Expenses:** [data]
    **- Unnecessary Expense Categories:** [data]
    **- Estimated Savings %:** [data]
    **- Spending Trends:** [data]
    **- Category-wise Expense Breakdown (Partial):** [data]
    **- Cost Control Suggestions:** [data]
    Transaction History:
    {text}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        # Save report to temporary .txt file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(full_text)
            report_path = tmp.name

        return (
            "✅ Analysis Complete!",
            text[:2000] + "..." if len(text) > 2000 else text,
            extract_section(full_text, "Monthly Income & Expenses"),
            extract_section(full_text, "Unnecessary Expense Categories"),
            extract_section(full_text, "Estimated Savings %"),
            extract_section(full_text, "Spending Trends"),
            extract_section(full_text, "Category-wise Expense Breakdown (Partial)"),
            extract_section(full_text, "Cost Control Suggestions"),
            report_path
        )

    except Exception as e:
        return (f"❌ Gemini Error: {e}", "", "", "", "", "", "", "", None)

# 🎨 Gradio UI
with gr.Blocks(title="AI Financial Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 💸 AI-Powered Personal Finance Analyzer
    Upload your **UPI Expenses PDF** and get structured financial insights using **Gemini AI**.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(label="📂 Upload PDF", file_types=[".pdf"])
            analyze_btn = gr.Button("🔍 Analyze")

        with gr.Column(scale=1):
            status = gr.Textbox(label="✅ Status", interactive=False)
            download_btn = gr.File(label="📥 Download AI Report", interactive=False)

    with gr.Accordion("📜 View Extracted PDF Text (Optional)", open=False):
        extracted_text = gr.Textbox(label="📝 Extracted Text", lines=10, interactive=False)

    with gr.Row():
        income_expense = gr.Textbox(label="💵 Monthly Income & Expenses", lines=4, interactive=False)
        unnecessary = gr.Textbox(label="🛒 Unnecessary Expenses", lines=4, interactive=False)

    with gr.Row():
        savings = gr.Textbox(label="💰 Estimated Savings %", lines=2, interactive=False)
        trends = gr.Textbox(label="📈 Spending Trends", lines=4, interactive=False)

    with gr.Row():
        category_breakdown = gr.Textbox(label="📊 Category-wise Breakdown", lines=6, interactive=False)
        suggestions = gr.Textbox(label="🧠 Cost Control Suggestions", lines=6, interactive=False)

    analyze_btn.click(
        fn=analyze_financial_data,
        inputs=pdf_input,
        outputs=[
            status, extracted_text,
            income_expense, unnecessary,
            savings, trends,
            category_breakdown, suggestions,
            download_btn
        ]
    )

demo.launch(share=True)