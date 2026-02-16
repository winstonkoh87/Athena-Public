#!/usr/bin/env python3
"""
Athena Unified Analysis CLI
Routes analysis requests to the Pattern Recognition engine.
"""

import argparse
import sys
import json
from pathlib import Path

# Add the frameworks directory to sys.path to allow imports from hidden .agent dir
frameworks_path = (Path(__file__).parent.parent / "frameworks").resolve()
sys.path.insert(0, str(frameworks_path))

try:
    from pattern_recognition.factory import PatternRecognitionFactory
except ImportError as e:
    print(f"Debug: sys.path: {sys.path}")
    print(f"Debug: frameworks_path: {frameworks_path}")
    raise e

def main():
    parser = argparse.ArgumentParser(description="Athena Unified Pattern Recognition CLI")
    
    parser.add_argument("--target", required=True, help="Path to file to analyze")
    parser.add_argument("--mode", default="auto", choices=["auto", "financial", "media", "text", "psych"], 
                       help="Force specific analysis mode")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result")
    
    # Passthrough arguments for specific analyzers
    parser.add_argument("--model", help="LLM model (for financial/media)")
    parser.add_argument("--prompt", help="Custom prompt (for media)")
    parser.add_argument("--users", help="Comma-separated users (for psych)")
    
    args = parser.parse_args()
    
    # Prepare kwargs
    kwargs = {}
    if args.model: kwargs['model'] = args.model
    if args.prompt: kwargs['prompt'] = args.prompt
    if args.users: kwargs['users'] = args.users.split(',')
    
    try:
        analyzer = PatternRecognitionFactory.get_analyzer(args.target, args.mode)
        result = analyzer.analyze(args.target, **kwargs)
        
        if args.json:
            # Serializable export
            output = {
                "timestamp": result.timestamp,
                "type": result.analyzer_type,
                "summary": result.summary,
                "data": result.data,
                "confidence": result.confidence_score
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n📊 ANALYSIS REPORT")
            print("=" * 60)
            print(f"Type:       {result.analyzer_type.upper()}")
            print(f"Confidence: {result.confidence_score*100:.0f}%")
            print("-" * 60)
            print(result.summary)
            print("-" * 60)
            
            # Helper for displaying rich data if available
            if result.analyzer_type == "financial":
                # Print specific financial details if needed in non-JSON mode
                d = result.data
                print(f"Input: ${d.get('input_cost', 0):.2f} | Output: ${d.get('output_cost', 0):.2f}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
