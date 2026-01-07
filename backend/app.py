from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
from analytics import compute_metrics
from preprocess import clean_dataframe, analyze_aggregate
from ai_module import generate_ai_summary
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx'}

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_data():
    # Handle CORS preflight explicitly
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.json
    file_path = data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Process data
        if file_path.endswith('.csv'):
            # Robust CSV read across pandas/py versions
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
            except TypeError:
                # Fallback engine for odd files
                df = pd.read_csv(file_path, engine='python')
        else:
            df = pd.read_excel(file_path)
        # Clean and validate dataset before computing metrics using the standalone cleaner
        df = clean_dataframe(df)
        # If aggregate schema detected, analyze via aggregate path; else compute user-level metrics
        if ('user_id' not in df.columns) and ('date' in df.columns) and ('total_users' in df.columns):
            aggregate_result = analyze_aggregate(df)
            metrics = aggregate_result['metrics']
            visualization_data = aggregate_result['visualizationData']
        else:
            metrics = compute_metrics(df)
            # Build visualization data powered by backend metrics as before
            cohort = metrics.get('cohort_analysis', {}) or {}
            conversion_rate = float(metrics.get('conversion_rate', 0) or 0)
            total_users = int(metrics.get('total_users', 0) or 0)
            active_users = int(metrics.get('active_users', 0) or 0)
            churned_users = int(metrics.get('churned_users', 0) or 0)

            chartData = []
            try:
                def _sort_key(k):
                    return str(k)
                for period, users in sorted(cohort.items(), key=lambda kv: _sort_key(kv[0])):
                    users_count = int(users or 0)
                    est_active = round(users_count * conversion_rate)
                    churn_ratio = (churned_users / total_users) if total_users else 0
                    est_churn = round(users_count * churn_ratio)
                    chartData.append({
                        'period': str(period),
                        'users': users_count,
                        'active': est_active,
                        'churn': est_churn,
                    })
            except Exception:
                chartData = []

            inactive_users = max(total_users - active_users, 0)
            pie_total = active_users + inactive_users
            pieData = [
                { 'name': 'Active Users', 'value': round((active_users / pie_total) * 100, 2) if pie_total else 0 },
                { 'name': 'Inactive', 'value': round((inactive_users / pie_total) * 100, 2) if pie_total else 0 },
            ]
            visualization_data = {
                'chartData': chartData,
                'pieData': pieData,
            }
        
        # Generate AI summary (fail-safe in dev if AI creds are missing)
        try:
            ai_summary = generate_ai_summary(metrics)
        except Exception as ai_err:
            ai_summary = f"AI summary unavailable: {ai_err}"
        
        # Build visualization data powered by backend metrics
        # chartData from cohort_analysis (treat keys as periods, estimate active/churn)
        cohort = metrics.get('cohort_analysis', {}) or {}
        conversion_rate = float(metrics.get('conversion_rate', 0) or 0)
        total_users = int(metrics.get('total_users', 0) or 0)
        active_users = int(metrics.get('active_users', 0) or 0)
        churned_users = int(metrics.get('churned_users', 0) or 0)

        chartData = []
        try:
            # Sort by period key if they look like YYYY-MM
            def _sort_key(k):
                return str(k)
            for period, users in sorted(cohort.items(), key=lambda kv: _sort_key(kv[0])):
                users_count = int(users or 0)
                est_active = round(users_count * conversion_rate)
                # Distribute churn proportionally if available
                churn_ratio = (churned_users / total_users) if total_users else 0
                est_churn = round(users_count * churn_ratio)
                chartData.append({
                    'period': str(period),
                    'users': users_count,
                    'active': est_active,
                    'churn': est_churn,
                })
        except Exception:
            chartData = []

        # pieData from active vs inactive split
        inactive_users = max(total_users - active_users, 0)
        pie_total = active_users + inactive_users
        pieData = [
            { 'name': 'Active Users', 'value': round((active_users / pie_total) * 100, 2) if pie_total else 0 },
            { 'name': 'Inactive', 'value': round((inactive_users / pie_total) * 100, 2) if pie_total else 0 },
        ]
        visualizationData = {
            'chartData': chartData,
            'pieData': pieData,
        }
        
        return jsonify({
            'metrics': metrics,
            'ai_summary': ai_summary,
            'visualizationData': visualization_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)
