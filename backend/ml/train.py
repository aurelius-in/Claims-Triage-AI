#!/usr/bin/env python3
"""
Training script for Claims Triage AI models.

This script provides a command-line interface for training:
- Risk scoring models (XGBoost-based)
- Classification models (Zero-shot LLM + ML fallback)

Usage:
    python train.py --model-type risk --data-path data/claims.csv --target-column risk_score
    python train.py --model-type classification --data-path data/claims.csv --text-column description --target-column claim_type
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

from ml.training import (
    train_risk_model,
    train_classification_model,
    cross_validate_model,
    generate_training_report
)
from ml.registry import save_model, list_models
from ml.explainability import create_explanation_report


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
    
    # Check for missing values in target
    missing_target = data[target_column].isna().sum()
    if missing_target > 0:
        print(f"Warning: {missing_target} missing values in target column")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Train Claims Triage AI models")
    
    # Required arguments
    parser.add_argument(
        "--model-type",
        choices=["risk", "classification"],
        required=True,
        help="Type of model to train"
    )
    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to training data file (CSV, Excel, JSON, Parquet)"
    )
    parser.add_argument(
        "--target-column",
        required=True,
        help="Name of the target column"
    )
    
    # Optional arguments
    parser.add_argument(
        "--text-column",
        help="Name of the text column (required for classification models)"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data to use for testing (default: 0.2)"
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--hyperparameter-tuning",
        action="store_true",
        help="Perform hyperparameter tuning (for risk models)"
    )
    parser.add_argument(
        "--use-zero-shot",
        action="store_true",
        default=True,
        help="Use zero-shot classification (for classification models)"
    )
    parser.add_argument(
        "--train-ml-fallback",
        action="store_true",
        default=True,
        help="Train ML fallback model (for classification models)"
    )
    parser.add_argument(
        "--model-version",
        help="Version string for the model (auto-generated if not provided)"
    )
    parser.add_argument(
        "--output-dir",
        default="training_outputs",
        help="Directory to save training outputs (default: training_outputs)"
    )
    parser.add_argument(
        "--cross-validate",
        action="store_true",
        help="Perform cross-validation after training"
    )
    parser.add_argument(
        "--cv-folds",
        type=int,
        default=5,
        help="Number of cross-validation folds (default: 5)"
    )
    parser.add_argument(
        "--generate-explanations",
        action="store_true",
        help="Generate SHAP explanations after training"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the trained model to registry"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.model_type == "classification" and not args.text_column:
        print("Error: --text-column is required for classification models")
        sys.exit(1)
    
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
    
    # Train model
    print(f"\nTraining {args.model_type} model...")
    start_time = datetime.now()
    
    try:
        if args.model_type == "risk":
            results = train_risk_model(
                data=data,
                target_column=args.target_column,
                test_size=args.test_size,
                random_state=args.random_state,
                hyperparameter_tuning=args.hyperparameter_tuning,
                save_model=not args.no_save,
                model_version=args.model_version
            )
        else:  # classification
            results = train_classification_model(
                data=data,
                text_column=args.text_column,
                target_column=args.target_column,
                test_size=args.test_size,
                random_state=args.random_state,
                use_zero_shot=args.use_zero_shot,
                train_ml_fallback=args.train_ml_fallback,
                save_model=not args.no_save,
                model_version=args.model_version
            )
        
        training_time = datetime.now() - start_time
        print(f"Training completed in {training_time}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        sys.exit(1)
    
    # Save training results
    results_file = output_dir / f"training_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Training results saved to: {results_file}")
    
    # Generate training report
    report_path = generate_training_report(results, str(output_dir / "training_report.md"))
    print(f"Training report saved to: {report_path}")
    
    # Cross-validation
    if args.cross_validate:
        print("\nPerforming cross-validation...")
        try:
            cv_results = cross_validate_model(
                data=data,
                target_column=args.target_column,
                model_type=args.model_type,
                cv_folds=args.cv_folds,
                random_state=args.random_state
            )
            
            cv_file = output_dir / f"cv_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(cv_file, 'w') as f:
                json.dump(cv_results, f, indent=2)
            print(f"Cross-validation results saved to: {cv_file}")
            
        except Exception as e:
            print(f"Error during cross-validation: {e}")
    
    # Generate explanations
    if args.generate_explanations and args.model_type == "risk":
        print("\nGenerating SHAP explanations...")
        try:
            # Load the trained model
            if 'model_id' in results:
                from ml.registry import load_model
                model = load_model(results['model_id'])
                if model:
                    # Create test data for explanations
                    test_data = data.sample(min(100, len(data)), random_state=args.random_state)
                    explanation_report = create_explanation_report(
                        model, test_data, str(output_dir / "explanations")
                    )
                    print(f"Explanation report saved to: {explanation_report}")
            
        except Exception as e:
            print(f"Error generating explanations: {e}")
    
    # Print summary
    print(f"\n{'='*50}")
    print("TRAINING SUMMARY")
    print(f"{'='*50}")
    print(f"Model Type: {args.model_type}")
    print(f"Data Samples: {len(data)}")
    print(f"Training Samples: {results.get('training_samples', 'N/A')}")
    print(f"Test Samples: {results.get('test_samples', 'N/A')}")
    
    if args.model_type == "risk":
        test_metrics = results.get('test_metrics', {})
        print(f"Test R²: {test_metrics.get('r2', 'N/A'):.4f}")
        print(f"Test RMSE: {test_metrics.get('rmse', 'N/A'):.4f}")
    else:
        test_metrics = results.get('test_metrics', {})
        print(f"Test Accuracy: {test_metrics.get('accuracy', 'N/A'):.4f}")
    
    if 'model_id' in results:
        print(f"Model ID: {results['model_id']}")
    
    print(f"Output Directory: {output_dir}")
    print(f"{'='*50}")
    
    # List models in registry
    if not args.no_save:
        print("\nModels in registry:")
        models = list_models()
        for model in models:
            print(f"  - {model['name']} ({model['type']}): {len(model['versions'])} versions")


if __name__ == "__main__":
    main()
