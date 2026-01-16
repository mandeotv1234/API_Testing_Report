import json
import os
import sys
from datetime import datetime

# Function to read JSON data
def load_json_data(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return None

def generate_combined_html_report(all_data, output_dir):
    # Aggregation Variables
    total_requests = 0
    total_passed_requests = 0
    total_failed_requests = 0
    total_time = 0
    
    combined_results = []
    suite_statistics = []
    
    # Iterate through all loaded data to aggregate metrics
    for data in all_data:
        if not data: continue
        
        suite_name = data.get('name', 'Unknown')
        suite_total = 0
        suite_pass = 0
        suite_fail = 0
        
        # Build method map for this file
        req_methods = {}
        if 'collection' in data and 'requests' in data['collection']:
            for r in data['collection']['requests']:
                req_methods[r['id']] = r.get('method', 'UNKNOWN')

        results = data.get('results', [])
        for res in results:
            total_requests += 1
            suite_total += 1
            
            time_ms = res.get('time', 0)
            total_time += time_ms
            
            # Recalculate status for display logic
            tests = res.get('tests', {})
            all_passed = all(tests.values()) if tests else True
            
            if not all_passed:
                total_failed_requests += 1
                suite_fail += 1
            else:
                total_passed_requests += 1
                suite_pass += 1

            res_augmented = res.copy()
            res_augmented['method'] = req_methods.get(res.get('id'), 'UNKNOWN')
            res_augmented['status_str'] = 'Passed' if all_passed else 'Failed'
            res_augmented['status_class'] = 'status-passed' if all_passed else 'status-failed'
            res_augmented['suite_name'] = suite_name # Add suite name to result for filtering if needed later
            
            combined_results.append(res_augmented)
            
        # Store suite stats
        suite_rate = round((suite_pass / suite_total) * 100, 2) if suite_total > 0 else 0
        suite_statistics.append({
            'name': suite_name,
            'total': suite_total,
            'pass': suite_pass,
            'fail': suite_fail,
            'rate': suite_rate
        })

    results_count = len(combined_results)
    avg_time = round(total_time / results_count, 2) if results_count > 0 else 0
    success_rate = round((total_passed_requests / results_count) * 100, 2) if results_count > 0 else 0
    
    # Current Timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Báo Cáo Kiểm Thử API Tổng Hợp</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-color: #4a90e2;
                --success-color: #2ecc71;
                --danger-color: #e74c3c;
                --text-color: #2c3e50;
                --bg-color: #f4f6f9;
                --card-bg: #ffffff;
                --header-bg: #34495e;
            }}

            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--bg-color);
                color: var(--text-color);
            }}

            .container {{
                max-width: 1200px;
                margin: 40px auto;
                padding: 0 20px;
            }}

            header {{
                background-color: var(--header-bg);
                color: white;
                padding: 20px 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}

            h1 {{ margin: 0; font-weight: 500; letter-spacing: 1px; }}
            .report-date {{ opacity: 0.8; font-size: 0.9em; margin-top: 5px; }}

            /* Section Titles */
            .section-title {{
                margin-top: 40px;
                margin-bottom: 20px;
                font-size: 1.5em;
                color: var(--header-bg);
                border-left: 5px solid var(--primary-color);
                padding-left: 15px;
            }}

            /* Stats Grid */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}

            .stat-card {{
                background: var(--card-bg);
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                text-align: center;
                transition: transform 0.3s ease;
            }}

            .stat-card:hover {{ transform: translateY(-5px); }}

            .stat-value {{ font-size: 2.5em; font-weight: 700; margin: 10px 0; color: var(--primary-color); }}
            .stat-label {{ color: #7f8c8d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
            
            .stat-card.passed .stat-value {{ color: var(--success-color); }}
            .stat-card.failed .stat-value {{ color: var(--danger-color); }}

            /* Progress Bar */
            .progress-container {{
                background-color: #e0e0e0;
                border-radius: 20px;
                height: 10px;
                width: 100%;
                margin: 20px 0;
                overflow: hidden;
            }}
            .progress-bar {{
                background-color: var(--success-color);
                height: 100%;
                border-radius: 20px;
                transition: width 1s ease-in-out;
            }}

            /* Suite Breakdown Table */
            .suite-table th, .suite-table td {{ padding: 12px 15px; }}
            .suite-table th {{ background-color: #e9ecef; color: #555; }}
            
            /* Main Table Styles */
            .table-container {{
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                overflow: hidden;
                margin-bottom: 40px;
            }}

            table {{ width: 100%; border-collapse: collapse; }}
            
            th, td {{ padding: 15px 20px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
            th {{ background-color: #f8f9fa; font-weight: 600; color: #7f8c8d; }}
            tr:hover {{ background-color: #f9f9f9; }}

            .status-badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .status-passed {{ background-color: rgba(46, 204, 113, 0.15); color: var(--success-color); }}
            .status-failed {{ background-color: rgba(231, 76, 60, 0.15); color: var(--danger-color); }}

            .method-badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                color: white;
                font-size: 0.8em;
                font-weight: bold;
                min-width: 50px;
                text-align: center;
            }}
            .GET {{ background-color: #61affe; }}
            .POST {{ background-color: #49cc90; }}
            .PUT {{ background-color: #fca130; }}
            .DELETE {{ background-color: #f93e3e; }}

            /* Collapsible Tests */
            .test-details {{ display: none; background-color: #fcfcfc; padding: 15px 20px; border-bottom: 1px solid #ecf0f1; }}
            .test-row {{ cursor: pointer; }}
            .expand-icon {{ transition: transform 0.2s; display: inline-block; }}
            .test-row.active .expand-icon {{ transform: rotate(90deg); }}
            
            .test-item {{ margin-bottom: 5px; font-size: 0.9em; }}
            .test-pass {{ color: var(--success-color); }}
            .test-fail {{ color: var(--danger-color); }}

        </style>
    </head>
    <body>

        <header>
            <div class="container" style="margin: 0 auto;">
                <h1>Báo Cáo Tự Động Hóa - API Testing</h1>
                <div class="report-date">Ngày tạo: {now}</div>
            </div>
        </header>

        <div class="container">
            
            <div class="section-title">5.1 Chỉ số Tổng hợp</div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Tổng số Request</div>
                    <div class="stat-value">{total_requests}</div>
                </div>
                <div class="stat-card passed">
                    <div class="stat-label">Đạt (Passed)</div>
                    <div class="stat-value">{total_passed_requests}</div>
                </div>
                <div class="stat-card failed">
                    <div class="stat-label">Thất bại (Failed)</div>
                    <div class="stat-value">{total_failed_requests}</div>
                    <div style="font-size: 0.8em; color: #999;">(Do lỗi hệ thống)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Tỷ lệ thành công</div>
                    <div class="stat-value">{success_rate}%</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {success_rate}%;"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Thời gian phản hồi TB</div>
                    <div class="stat-value">~{avg_time}ms</div>
                </div>
            </div>

            <div class="section-title">Thống kê theo từng bộ Test</div>
            <div class="table-container">
                <table class="suite-table">
                    <thead>
                        <tr>
                            <th>Tên bộ Test (Collection)</th>
                            <th style="width: 100px;">Tổng số</th>
                            <th style="width: 100px; color: var(--success-color);">Passed</th>
                            <th style="width: 100px; color: var(--danger-color);">Failed</th>
                            <th style="width: 150px;">Tỷ lệ thành công</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Add Suite breakdown rows
    for suite in suite_statistics:
        html_content += f"""
                        <tr>
                            <td><strong>{suite['name']}</strong></td>
                            <td>{suite['total']}</td>
                            <td style="color: var(--success-color); font-weight: bold;">{suite['pass']}</td>
                            <td style="color: var(--danger-color); font-weight: bold;">{suite['fail']}</td>
                            <td>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span>{suite['rate']}%</span>
                                    <div class="progress-container" style="width: 80px; height: 6px; margin: 0;">
                                        <div class="progress-bar" style="width: {suite['rate']}%;"></div>
                                    </div>
                                </div>
                            </td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>

            <div class="section-title">Chi Tiết Test Case</div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 50px;"></th>
                            <th>Tên Test Case</th>
                            <th>Method</th>
                            <th>URL</th>
                            <th>Thời gian</th>
                            <th>Trạng thái</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    # Generate HTML Loop
    for idx, res in enumerate(combined_results):
        row_id = f"row-{idx}"
        tests = res.get('tests', {})
        test_list_items = ""
        for t_name, t_pass in tests.items():
            icon = "✔" if t_pass else "✖"
            cls = "test-pass" if t_pass else "test-fail"
            test_list_items += f"<div class='test-item {cls}'><span>{icon}</span> {t_name}</div>"

        html_content += f"""
                        <tr class="test-row" onclick="toggleDetails('{row_id}')">
                            <td style="text-align: center;"><span class="expand-icon">▶</span></td>
                            <td>
                                <div><strong>{res['name']}</strong></div>
                                <div style="font-size: 0.8em; color: #999;">{res['suite_name']}</div>
                            </td>
                            <td><span class="method-badge {res['method']}">{res['method']}</span></td>
                            <td style="font-size: 0.9em; color: #666;">{res['url']}</td>
                            <td>{res['time']}ms</td>
                            <td><span class="status-badge {res['status_class']}">{res['status_str']}</span></td>
                        </tr>
                        <tr id="{row_id}" class="test-details">
                            <td colspan="6">
                                <strong>Chi tiết kiểm tra:</strong>
                                <div style="margin-top: 10px;">
                                    {test_list_items if test_list_items else "Không có assert nào."}
                                </div>
                            </td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            function toggleDetails(rowId) {
                const detailsRow = document.getElementById(rowId);
                const parentRow = detailsRow.previousElementSibling;
                
                if (detailsRow.style.display === 'table-row') {
                    detailsRow.style.display = 'none';
                    parentRow.classList.remove('active');
                } else {
                    detailsRow.style.display = 'table-row';
                    parentRow.classList.add('active');
                }
            }
        </script>
    </body>
    </html>
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "report.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Đã tạo báo cáo tổng hợp tại: {output_path}")

# --- Main Configuration & Execution ---

tasks = [
    {
        "json": "SearchEmployee/CSC13003 - API Testing - Search Employee.postman_test_run.json",
        "output": "reports"
    },
    {
        "json": "AddEmployee/CSC13003 - API Testing - Add Employee.postman_test_run.json",
        "output": "reports"
    }
]

base_dir = os.getcwd() 
all_json_data = []

print("--- Bắt đầu tạo báo cáo ---")

for task in tasks:
    json_path = os.path.join(base_dir, task["json"])
    print(f"Đọc dữ liệu từ: {task['json']}")
    data = load_json_data(json_path)
    if data:
        all_json_data.append(data)

# Generate Combined Report
if all_json_data:
    reports_dir = os.path.join(base_dir, "reports")
    generate_combined_html_report(all_json_data, reports_dir)
else:
    print("❌ Không tìm thấy dữ liệu để tạo báo cáo.")
