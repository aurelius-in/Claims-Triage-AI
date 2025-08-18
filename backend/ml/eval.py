#!/usr/bin/env python3
"""
Evaluation script for Claims Triage AI models.

This script provides a command-line interface for evaluating:
- Risk scoring models
- Classification models
- Model performance comparison
- SHAP explanations

Usage:
    python eval.py --model-id risk_model_risk_scoring --data-path test_data.csv --target-column risk_score
    python eval.py --model-id classification_model_classification --data-path test_data.csv --target-column claim_type --text-column description
"""

import argparse
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.training import evaluate_model, compare_models
from ml.registry import load_model, list_models, get_model_metadata
from ml.explainability import (
    create_explanation_report,
    analyze_model_bias,
    create_interactive_explanation
)


def load_data(data_path: str) -> pd.DataFrame:
    """Load data from various formats."""
    data_path = Path(data_path)
    
    if data_path.suffix.lower() == '.csv':
        return pd.read_csv(data_path)
    elif data_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(data_path)
    elif data_path.suffix.lower() == '.json':
        return pd.read_json(data_path)
    elif data_path.suffix.lower() == '.parquet':
        return pd.read_parquet(data_path)
    else:
        raise ValueError(f"Unsupported file format: {data_path.suffix}")


def validate_data(data: pd.DataFrame, target_column: str, text_column: str = None) -> bool:
    """Validate that the data contains required columns."""
    if target_column not in data.columns:
        print(f"Error: Target column '{target_column}' not found in data")
        print(f"Available columns: {list(data.columns)}")
        return False
    
    if text_column and text_column not in data.columns:
        print(f"Error: Text column '{text_column}' not found in data")
        print(f"Available columns: {list(data.columns)}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Evaluate Claims Triage AI models")
    
    # Required arguments
    parser.add_argument(
        "--model-id",
        required=True,
        help="ID of the model to evaluate"
    )
    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to test data file (CSV, Excel, JSON, Parquet)"
    )
    parser.add_argument(
        "--target-column",
        required=True,
        help="Name of the target column"
    )
    
    # Optional arguments
    parser.add_argument(
        "--text-column",
        help="Name of the text column (for classification models)"
    )
    parser.add_argument(
        "--version",
        help="Model version to evaluate (latest if not provided)"
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation_outputs",
        help="Directory to save evaluation outputs (default: evaluation_outputs)"
    )
    parser.add_argument(
        "--generate-explanations",
        action="store_true",
        help="Generate SHAP explanations"
    )
    parser.add_argument(
        "--analyze-bias",
        nargs="+",
        help="Analyze model bias with respect to sensitive features"
    )
    parser.add_argument(
        "--create-interactive",
        action="store_true",
        help="Create interactive HTML explanation"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        help="Number of samples to use for explanations (default: all)"
    )
    parser.add_argument(
        "--compare-models",
        nargs="+",
        help="Compare multiple models (provide model IDs)"
    )
    parser.add_argument(
        "--comparison-metric",
        default="accuracy",
        help="Metric to use for model comparison (default: accuracy)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and validate data
    print(f"Loading data from {args.data_path}...")
    try:
        data = load_data(args.data_path)
        print(f"Loaded {len(data)} samples with {len(data.columns)} features")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    if not validate_data(data, args.target_column, args.text_column):
        sys.exit(1)
    
    # Sample data if requested
    if args.sample_size and args.sample_size < len(data):
        data = data.sample(args.sample_size, random_state=42)
        print(f"Sampled {len(data)} samples for evaluation")
    
    # Load model
    print(f"Loading model {args.model_id}...")
    try:
        model = load_model(args.model_id, args.version)
        if model is None:
            print(f"Error: Model {args.model_id} not found")
            sys.exit(1)
        
        # Get model metadata
        metadata = get_model_metadata(args.model_id, args.version)
        model_type = metadata.get('model_type', 'unknown') if metadata else 'unknown'
        print(f"Loaded {model_type} model")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
    
    # Determine model type for evaluation
    if 'risk' in model_type:
        eval_model_type = 'risk'
    elif 'classification' in model_type:
        eval_model_type = 'classification'
        if not args.text_column:
            print("Error: --text-column is required for classification models")
            sys.exit(1)
    else:
        print(f"Unknown model type: {model_type}")
        sys.exit(1)
    
    # Evaluate model
    print(f"\nEvaluating {eval_model_type} model...")
    start_time = datetime.now()
    
    try:
        evaluation_results = evaluate_model(
            model_id=args.model_id,
            test_data=data,
            target_column=args.target_column,
            model_type=eval_model_type,
            version=args.version
        )
        
        evaluation_time = datetime.now() - start_time
        print(f"Evaluation completed in {evaluation_time}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)
    
    # Save evaluation results
    results_file = output_dir / f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    print(f"Evaluation results saved to: {results_file}")
    
    # Generate explanations
    if args.generate_explanations:
        print("\nGenerating SHAP explanations...")
        try:
            explanation_report = create_explanation_report(
                model, data, str(output_dir / "explanations")
            )
            print(f"Explanation report saved to: {explanation_report}")
        except Exception as e:
            print(f"Error generating explanations: {e}")
    
    # Analyze bias
    if args.analyze_bias:
        print(f"\nAnalyzing model bias for features: {args.analyze_bias}")
        try:
            bias_results = analyze_model_bias(model, data, args.analyze_bias)
            
            bias_file = output_dir / f"bias_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(bias_file, 'w') as f:
                json.dump(bias_results, f, indent=2)
            print(f"Bias analysis saved to: {bias_file}")
            
        except Exception as e:
            print(f"Error analyzing bias: {e}")
    
    # Create interactive explanation
    if args.create_interactive:
        print("\nCreating interactive explanation...")
        try:
            interactive_file = output_dir / "interactive_explanation.html"
            result = create_interactive_explanation(model, data, str(interactive_file))
            if not result.startswith("Error"):
                print(f"Interactive explanation saved to: {interactive_file}")
            else:
                print(f"Error creating interactive explanation: {result}")
        except Exception as e:
            print(f"Error creating interactive explanation: {e}")
    
    # Model comparison
    if args.compare_models:
        print(f"\nComparing models: {args.compare_models}")
        try:
            # Add current model to comparison
            all_model_ids = [args.model_id] + args.compare_models
            
            # Evaluate all models
            comparison_results = []
            for model_id in all_model_ids:
                try:
                    model_to_eval = load_model(model_id)
                    if model_to_eval:
                        eval_result = evaluate_model(
                            model_id=model_id,
                            test_data=data,
                            target_column=args.target_column,
                            model_type=eval_model_type
                        )
                        comparison_results.append(eval_result)
                    else:
                        print(f"Warning: Could not load model {model_id}")
                except Exception as e:
                    print(f"Warning: Error evaluating model {model_id}: {e}")
            
            if comparison_results:
                comparison = compare_models(comparison_results, args.comparison_metric)
                
                comparison_file = output_dir / f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(comparison_file, 'w') as f:
                    json.dump(comparison, f, indent=2)
                print(f"Model comparison saved to: {comparison_file}")
                
                # Print comparison summary
                print(f"\nModel Comparison Results ({args.comparison_metric}):")
                for i, model_result in enumerate(comparison['models']):
                    print(f"  {i+1}. {model_result['model_id']}: {model_result['metric_value']:.4f}")
                
                if comparison['best_model']:
                    print(f"\nBest model: {comparison['best_model']['model_id']}")
            
        except Exception as e:
            print(f"Error during model comparison: {e}")
    
    # Print evaluation summary
    print(f"\n{'='*50}")
    print("EVALUATION SUMMARY")
    print(f"{'='*50}")
    print(f"Model ID: {args.model_id}")
    if args.version:
        print(f"Version: {args.version}")
    print(f"Model Type: {eval_model_type}")
    print(f"Test Samples: {len(data)}")
    
    metrics = evaluation_results.get('evaluation_metrics', {})
    if eval_model_type == "risk":
        print(f"R² Score: {metrics.get('r2', 'N/A'):.4f}")
        print(f"RMSE: {metrics.get('rmse', 'N/A'):.4f}")
        print(f"MAE: {metrics.get('mae', 'N/A'):.4f}")
    else:
        print(f"Accuracy: {metrics.get('accuracy', 'N/A'):.4f}")
        if 'classification_report' in metrics:
            report = metrics['classification_report']
            if 'weighted avg' in report:
                print(f"F1-Score: {report['weighted avg']['f1-score']:.4f}")
                print(f"Precision: {report['weighted avg']['precision']:.4f}")
                print(f"Recall: {report['weighted avg']['recall']:.4f}")
    
    print(f"Output Directory: {output_dir}")
    print(f"{'='*50}")
    
    # List available models
    print("\nAvailable models in registry:")
    models = list_models()
    for model in models:
        print(f"  - {model['name']} ({model['type']}): {len(model['versions'])} versions")


if __name__ == "__main__":
    main()
