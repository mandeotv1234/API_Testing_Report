import json
import os
import sys
from datetime import datetime

def generate_html_report(json_path, output_dir):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return

    collection_name = data.get('name', 'API Test Run')
    timestamp_str = data.get('timestamp', '')
    # Parse and format timestamp nicely if possible
    try:
        # Expected format: "2026-01-15T14:59:57.690Z"
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        formatted_date = timestamp_str

    total_pass = data.get('totalPass', 0)
    total_fail = data.get('totalFail', 0)
    
    # Create a map for request methods
    request_methods = {}
    if 'collection' in data and 'requests' in data['collection']:
        for req in data['collection']['requests']:
            request_methods[req['id']] = req.get('method', 'UNKNOWN')

    results = data.get('results', [])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{collection_name} - Test Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .summary {{ display: flex; gap: 20px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }}
            .summary-item {{ display: flex; flex-direction: column; }}
            .label {{ font-size: 0.9em; color: #666; }}
            .value {{ font-size: 1.2em; font-weight: bold; }}
            .pass {{ color: #28a745; }}
            .fail {{ color: #dc3545; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; vertical-align: top; }}
            th {{ background-color: #f8f9fa; font-weight: 600; }}
            .test-pass {{ color: #28a745; font-weight: bold; }}
            .test-fail {{ color: #dc3545; font-weight: bold; }}
            .method {{ display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.8em; font-weight: bold; }}
            .GET {{ background-color: #61affe; }}
            .POST {{ background-color: #49cc90; }}
            .PUT {{ background-color: #fca130; }}
            .DELETE {{ background-color: #f93e3e; }}
            .PATCH {{ background-color: #50e3c2; }}
            .UNKNOWN {{ background-color: #777; }}
            .url {{ font-size: 0.8em; color: #999; word-break: break-all; }}
            .test-list {{ margin: 0; padding: 0; list-style-type: none; }}
            .test-list li {{ margin-bottom: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{collection_name}</h1>
            <div class="summary">
                <div class="summary-item">
                    <span class="label">Date</span>
                    <span class="value">{formatted_date}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Total Pass</span>
                    <span class="value pass">{total_pass}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Total Fail</span>
                    <span class="value fail">{total_fail}</span>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Request</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Time (ms)</th>
                        <th>Tests</th>
                    </tr>
                </thead>
                <tbody>
    """

    for res in results:
        req_id = res.get('id')
        method = request_methods.get(req_id, 'UNKNOWN')
        name = res.get('name', 'Unnamed Request')
        url = res.get('url', '')
        time_ms = res.get('time', 0)
        status_code = res.get('responseCode', {}).get('code', 'N/A')
        status_name = res.get('responseCode', {}).get('name', '')
        
        tests = res.get('tests', {})
        test_html_items = []
        for test_name, passed in tests.items():
            status_class = "test-pass" if passed else "test-fail"
            status_icon = "✓" if passed else "✗"
            test_html_items.append(f"<li><span class='{status_class}'>{status_icon}</span> {test_name}</li>")
        
        test_list_html = f"<ul class='test-list'>{''.join(test_html_items)}</ul>" if test_html_items else "No tests"

        html_content += f"""
                    <tr>
                        <td>
                            <div><strong>{name}</strong></div>
                            <div class="url">{url}</div>
                        </td>
                        <td><span class="method {method}">{method}</span></td>
                        <td>{status_code} {status_name}</td>
                        <td>{time_ms}</td>
                        <td>
                            {test_list_html}
                        </td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "report.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated report at {output_file}")

# Config
tasks = [
    {
        "json": "SearchEmployee/CSC13003 - API Testing - Search Employee.postman_test_run.json",
        "output": "reports/search"
    },
    {
        "json": "AddEmployee/CSC13003 - API Testing - Add Employee.postman_test_run.json",
        "output": "reports/add"
    }
]

base_dir = os.getcwd() 

for task in tasks:
    json_path = os.path.join(base_dir, task["json"])
    output_path = os.path.join(base_dir, task["output"])
    print(f"Processing {json_path}...")
    generate_html_report(json_path, output_path)
