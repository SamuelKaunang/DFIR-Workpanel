import sys
try:
    from reports.generator import generate_ir_report
    print("Generating...")
    output = generate_ir_report("CASE-2026-002")
    print(f"Success! {output}")
except Exception as e:
    print(f"Error: {e}")
