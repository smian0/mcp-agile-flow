#!/usr/bin/env python3
"""
Dead Code Analyzer - Vulture Report Generator

This script uses Vulture to identify potentially unused code in a Python project
and generates a structured report at different confidence levels.

Usage:
    python analyze_dead_code.py [--src SRC] [--output OUTPUT] [--html] [--json]

Options:
    --src SRC        Source directory to analyze [default: src]
    --output OUTPUT  Output file path for the report [default: dead_code_report]
    --html           Generate HTML report
    --json           Generate JSON report
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Define confidence levels for analysis
CONFIDENCE_LEVELS = [60, 75, 90, 100]


class DeadCodeFinding:
    """Represents a single dead code finding from Vulture."""

    def __init__(self, file_path: str, line_number: int, item_type: str, item_name: str, confidence: int):
        self.file_path = file_path
        self.line_number = line_number
        self.item_type = item_type
        self.item_name = item_name
        self.confidence = confidence

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number}: unused {self.item_type} '{self.item_name}' ({self.confidence}% confidence)"

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "item_type": self.item_type,
            "item_name": self.item_name,
            "confidence": self.confidence,
        }


def parse_vulture_output(output: str) -> List[DeadCodeFinding]:
    """Parse the output from Vulture and extract findings."""
    findings = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        
        # Parse vulture output line format: file_path:line_number: unused item_type 'item_name' (confidence% confidence)
        try:
            file_info, description = line.split(": unused ", 1)
            file_path, line_number = file_info.rsplit(":", 1)
            
            # Extract item details
            item_parts = description.split(" (", 1)
            item_details = item_parts[0]
            confidence_part = item_parts[1].replace("% confidence)", "")
            
            # Extract item name from quotes
            if "'" in item_details:
                item_type, item_name = item_details.split("'", 1)
                item_name = item_name.strip("'")
            else:
                item_type = item_details
                item_name = "unknown"
            
            findings.append(
                DeadCodeFinding(
                    file_path=file_path,
                    line_number=int(line_number),
                    item_type=item_type.strip(),
                    item_name=item_name,
                    confidence=int(confidence_part)
                )
            )
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
    
    return findings


def run_vulture(src_dir: str, min_confidence: int) -> Tuple[List[DeadCodeFinding], int]:
    """Run Vulture with the specified confidence level and return findings."""
    try:
        result = subprocess.run(
            ["vulture", src_dir, f"--min-confidence={min_confidence}"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode not in [0, 3]:  # 0=no issues, 3=dead code found
            print(f"Vulture error (code {result.returncode}): {result.stderr}")
            return [], result.returncode
        
        findings = parse_vulture_output(result.stdout)
        return findings, result.returncode
    except Exception as e:
        print(f"Error running Vulture: {e}")
        return [], 1


def generate_text_report(findings_by_confidence: Dict[int, List[DeadCodeFinding]], output_file: str) -> None:
    """Generate a text report of findings at different confidence levels."""
    with open(f"{output_file}.txt", "w") as f:
        f.write("===========================================================\n")
        f.write(f"DEAD CODE ANALYSIS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("===========================================================\n\n")
        
        total_findings = sum(len(findings) for findings in findings_by_confidence.values())
        f.write(f"Total findings: {total_findings}\n\n")
        
        for confidence in sorted(findings_by_confidence.keys(), reverse=True):
            findings = findings_by_confidence[confidence]
            if not findings:
                continue
                
            f.write(f"CONFIDENCE LEVEL: {confidence}%\n")
            f.write("-" * 50 + "\n")
            f.write(f"Found {len(findings)} potential issues\n\n")
            
            # Group by file
            findings_by_file = defaultdict(list)
            for finding in findings:
                findings_by_file[finding.file_path].append(finding)
            
            for file_path, file_findings in sorted(findings_by_file.items()):
                f.write(f"File: {file_path}\n")
                for finding in sorted(file_findings, key=lambda x: x.line_number):
                    f.write(f"  - Line {finding.line_number}: unused {finding.item_type} '{finding.item_name}'\n")
                f.write("\n")
            
            f.write("\n")
    
    print(f"Text report generated: {output_file}.txt")


def generate_html_report(findings_by_confidence: Dict[int, List[DeadCodeFinding]], output_file: str) -> None:
    """Generate an HTML report of findings at different confidence levels."""
    with open(f"{output_file}.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dead Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; }
        h2 { color: #555; margin-top: 20px; }
        .summary { background-color: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .confidence-section { margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .confidence-100 { background-color: #fdd; }
        .confidence-90 { background-color: #fed; }
        .confidence-75 { background-color: #ffe; }
        .confidence-60 { background-color: #eff; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .file-section { margin: 15px 0; }
        .file-header { background-color: #f2f2f2; padding: 5px; border-left: 3px solid #333; }
    </style>
</head>
<body>
        """)
        
        f.write(f"<h1>Dead Code Analysis Report</h1>")
        f.write(f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        total_findings = sum(len(findings) for findings in findings_by_confidence.values())
        f.write(f"<div class='summary'>")
        f.write(f"<h2>Summary</h2>")
        f.write(f"<p>Total findings: {total_findings}</p>")
        
        # Summary table
        f.write(f"<table>")
        f.write(f"<tr><th>Confidence Level</th><th>Number of Findings</th></tr>")
        for confidence in sorted(findings_by_confidence.keys(), reverse=True):
            findings = findings_by_confidence[confidence]
            if findings:
                f.write(f"<tr><td>{confidence}%</td><td>{len(findings)}</td></tr>")
        f.write(f"</table>")
        f.write(f"</div>")
        
        for confidence in sorted(findings_by_confidence.keys(), reverse=True):
            findings = findings_by_confidence[confidence]
            if not findings:
                continue
                
            f.write(f"<div class='confidence-section confidence-{confidence}'>")
            f.write(f"<h2>Confidence Level: {confidence}%</h2>")
            f.write(f"<p>Found {len(findings)} potential issues</p>")
            
            # Group by file
            findings_by_file = defaultdict(list)
            for finding in findings:
                findings_by_file[finding.file_path].append(finding)
            
            for file_path, file_findings in sorted(findings_by_file.items()):
                f.write(f"<div class='file-section'>")
                f.write(f"<div class='file-header'><strong>File:</strong> {file_path}</div>")
                
                f.write(f"<table>")
                f.write(f"<tr><th>Line</th><th>Type</th><th>Name</th></tr>")
                for finding in sorted(file_findings, key=lambda x: x.line_number):
                    f.write(f"<tr>")
                    f.write(f"<td>{finding.line_number}</td>")
                    f.write(f"<td>{finding.item_type}</td>")
                    f.write(f"<td>{finding.item_name}</td>")
                    f.write(f"</tr>")
                f.write(f"</table>")
                f.write(f"</div>")
            
            f.write(f"</div>")
        
        f.write("""
</body>
</html>
        """)
    
    print(f"HTML report generated: {output_file}.html")


def generate_json_report(findings_by_confidence: Dict[int, List[DeadCodeFinding]], output_file: str) -> None:
    """Generate a JSON report of findings at different confidence levels."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_findings": sum(len(findings) for findings in findings_by_confidence.values()),
        "confidence_levels": {},
    }
    
    for confidence, findings in findings_by_confidence.items():
        data["confidence_levels"][str(confidence)] = {
            "count": len(findings),
            "findings": [finding.to_dict() for finding in findings]
        }
    
    with open(f"{output_file}.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON report generated: {output_file}.json")


def main() -> None:
    """Run the dead code analysis and generate reports."""
    # Parse command line arguments
    src_dir = "src"
    output_file = "dead_code_report"
    html_report = False
    json_report = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--src" and i + 1 < len(args):
            src_dir = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == "--html":
            html_report = True
            i += 1
        elif args[i] == "--json":
            json_report = True
            i += 1
        else:
            i += 1
    
    # Check if source directory exists
    if not os.path.isdir(src_dir):
        print(f"Error: Source directory '{src_dir}' does not exist.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Store all findings by confidence level
    findings_by_confidence = {}
    all_findings = set()
    
    # Run Vulture at each confidence level
    for confidence in CONFIDENCE_LEVELS:
        print(f"Running Vulture with confidence level {confidence}%...")
        findings, return_code = run_vulture(src_dir, confidence)
        
        # Store only unique findings not already found at higher confidence levels
        unique_findings = []
        for finding in findings:
            finding_key = (finding.file_path, finding.line_number, finding.item_type, finding.item_name)
            if finding_key not in all_findings:
                all_findings.add(finding_key)
                unique_findings.append(finding)
        
        findings_by_confidence[confidence] = unique_findings
        print(f"Found {len(unique_findings)} unique issues at {confidence}% confidence")
    
    # Generate reports
    generate_text_report(findings_by_confidence, output_file)
    
    if html_report:
        generate_html_report(findings_by_confidence, output_file)
    
    if json_report:
        generate_json_report(findings_by_confidence, output_file)


if __name__ == "__main__":
    main()