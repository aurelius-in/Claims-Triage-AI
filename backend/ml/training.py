"""
Training and evaluation functions for Claims Triage AI models.

This module provides:
- Model training functions
- Model evaluation and metrics
- Cross-validation utilities
- Hyperparameter tuning
- Model comparison and selection
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from sklearn.model_selection import (
    train_test_split, 
    cross_val_score, 
    GridSearchCV,
    StratifiedKFold,
    KFold
)
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
import matplotlib.pyplot as plt
import seaborn as sns

from .models import RiskModel, ClassificationModel, ModelRegistry
from .features import FeaturePipeline, FeatureStore
from .explainability import SHAPExplainer


def train_risk_model(
    data: pd.DataFrame,
    target_column: str = 'risk_score',
    test_size: float = 0.2,
    random_state: int = 42,
    hyperparameter_tuning: bool = False,
    save_model: bool = True,
    model_version: str = None
) -> Dict[str, Any]:
    """
    Train a risk scoring model.
    
    Args:
        data: DataFrame containing claim data
        target_column: Name of the target column
        test_size: Fraction of data to use for testing
        random_state: Random seed for reproducibility
        hyperparameter_tuning: Whether to perform hyperparameter tuning
        save_model: Whether to save the trained model
        model_version: Version string for the model
    
    Returns:
        Dictionary containing training results and metrics
    """
    print("Starting risk model training...")
    
    # Prepare data
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Initialize model
    model = RiskModel()
    
    # Hyperparameter tuning
    if hyperparameter_tuning:
        print("Performing hyperparameter tuning...")
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1, 0.2]
        }
        
        grid_search = GridSearchCV(
            model.model,
            param_grid,
            cv=5,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        # Extract features for training
        X_train_features = model.extract_features(X_train)
        X_test_features = model.extract_features(X_test)
        
        grid_search.fit(X_train_features, y_train)
        
        # Update model with best parameters
        model.model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")
    
    # Train model
    print("Training model...")
    training_metrics = model.train(X_train, y_train, validation_split=0.2)
    
    # Evaluate on test set
    print("Evaluating model...")
    X_test_features = model.extract_features(X_test)
    X_test_scaled = model.scaler.transform(X_test_features)
    y_pred = model.model.predict(X_test_scaled)
    
    # Calculate metrics
    test_metrics = {
        'mse': mean_squared_error(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred),
        'r2': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
    }
    
    # Generate feature importance
    feature_importance = model.model.feature_importances_
    feature_names = model.feature_names
    
    # Create results dictionary
    results = {
        'model_type': 'risk_scoring',
        'training_metrics': training_metrics,
        'test_metrics': test_metrics,
        'feature_importance': dict(zip(feature_names, feature_importance)),
        'best_features': sorted(
            zip(feature_names, feature_importance),
            key=lambda x: x[1],
            reverse=True
        )[:10],
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'model_version': model_version or datetime.now().strftime('%Y%m%d_%H%M%S'),
        'created_at': datetime.now().isoformat()
    }
    
    # Save model if requested
    if save_model:
        registry = ModelRegistry()
        model_id = registry.register_model(model, results['model_version'], test_metrics)
        results['model_id'] = model_id
        print(f"Model saved with ID: {model_id}")
    
    print("Risk model training completed!")
    return results


def train_classification_model(
    data: pd.DataFrame,
    text_column: str = 'description',
    target_column: str = 'claim_type',
    test_size: float = 0.2,
    random_state: int = 42,
    use_zero_shot: bool = True,
    train_ml_fallback: bool = True,
    save_model: bool = True,
    model_version: str = None
) -> Dict[str, Any]:
    """
    Train a classification model.
    
    Args:
        data: DataFrame containing claim data
        text_column: Name of the text column for classification
        target_column: Name of the target column
        test_size: Fraction of data to use for testing
        random_state: Random seed for reproducibility
        use_zero_shot: Whether to use zero-shot classification
        train_ml_fallback: Whether to train ML fallback model
        save_model: Whether to save the trained model
        model_version: Version string for the model
    
    Returns:
        Dictionary containing training results and metrics
    """
    print("Starting classification model training...")
    
    # Prepare data
    texts = data[text_column].fillna('').tolist()
    labels = data[target_column].tolist()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=test_size, random_state=random_state, stratify=labels
    )
    
    # Initialize model
    model = ClassificationModel()
    
    # Train ML fallback model
    ml_metrics = None
    if train_ml_fallback:
        print("Training ML fallback model...")
        ml_metrics = model.train_ml_fallback(X_train, y_train)
    
    # Evaluate on test set
    print("Evaluating model...")
    predictions = []
    confidences = []
    methods = []
    
    for text in X_test:
        result = model.classify_claim_type(text)
        predictions.append(result['prediction'])
        confidences.append(result['confidence'])
        methods.append(result['method'])
    
    # Calculate metrics
    accuracy = sum(1 for p, t in zip(predictions, y_test) if p == t) / len(y_test)
    
    # Classification report
    class_report = classification_report(y_test, predictions, output_dict=True)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, predictions)
    
    # Method distribution
    method_distribution = {}
    for method in methods:
        method_distribution[method] = method_distribution.get(method, 0) + 1
    
    # Create results dictionary
    results = {
        'model_type': 'classification',
        'ml_fallback_metrics': ml_metrics,
        'test_metrics': {
            'accuracy': accuracy,
            'classification_report': class_report,
            'confusion_matrix': cm.tolist()
        },
        'method_distribution': method_distribution,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'model_version': model_version or datetime.now().strftime('%Y%m%d_%H%M%S'),
        'created_at': datetime.now().isoformat()
    }
    
    # Save model if requested
    if save_model:
        registry = ModelRegistry()
        model_id = registry.register_model(model, results['model_version'], {'accuracy': accuracy})
        results['model_id'] = model_id
        print(f"Model saved with ID: {model_id}")
    
    print("Classification model training completed!")
    return results


def evaluate_model(
    model_id: str,
    test_data: pd.DataFrame,
    target_column: str,
    model_type: str = 'risk',
    version: str = None
) -> Dict[str, Any]:
    """
    Evaluate a trained model on new data.
    
    Args:
        model_id: ID of the model to evaluate
        test_data: Test dataset
        target_column: Name of the target column
        model_type: Type of model ('risk' or 'classification')
        version: Model version to evaluate
    
    Returns:
        Dictionary containing evaluation results
    """
    print(f"Evaluating model {model_id}...")
    
    # Load model
    registry = ModelRegistry()
    model = registry.get_model(model_id, version)
    
    if model is None:
        raise ValueError(f"Model {model_id} not found")
    
    # Prepare data
    X = test_data.drop(columns=[target_column])
    y_true = test_data[target_column]
    
    # Make predictions
    if model_type == 'risk':
        y_pred = model.predict(X)
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
        }
        
        # Generate SHAP explanations
        explainer = SHAPExplainer(model)
        shap_values = explainer.explain_predictions(X)
        
    elif model_type == 'classification':
        # For classification, we need text data
        if 'description' not in test_data.columns:
            raise ValueError("Classification evaluation requires 'description' column")
        
        texts = test_data['description'].fillna('').tolist()
        predictions = []
        confidences = []
        
        for text in texts:
            result = model.classify_claim_type(text)
            predictions.append(result['prediction'])
            confidences.append(result['confidence'])
        
        # Calculate metrics
        accuracy = sum(1 for p, t in zip(predictions, y_true) if p == t) / len(y_true)
        
        metrics = {
            'accuracy': accuracy,
            'classification_report': classification_report(y_true, predictions, output_dict=True),
            'confusion_matrix': confusion_matrix(y_true, predictions).tolist()
        }
        
        shap_values = None  # SHAP not applicable for text classification in this context
    
    # Create evaluation results
    results = {
        'model_id': model_id,
        'model_version': version,
        'model_type': model_type,
        'evaluation_metrics': metrics,
        'shap_values': shap_values,
        'test_samples': len(test_data),
        'evaluated_at': datetime.now().isoformat()
    }
    
    print("Model evaluation completed!")
    return results


def cross_validate_model(
    data: pd.DataFrame,
    target_column: str,
    model_type: str = 'risk',
    cv_folds: int = 5,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Perform cross-validation on a model.
    
    Args:
        data: Dataset for cross-validation
        target_column: Name of the target column
        model_type: Type of model ('risk' or 'classification')
        cv_folds: Number of cross-validation folds
        random_state: Random seed for reproducibility
    
    Returns:
        Dictionary containing cross-validation results
    """
    print(f"Performing {cv_folds}-fold cross-validation...")
    
    # Prepare data
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    if model_type == 'risk':
        # Initialize model
        model = RiskModel()
        
        # Extract features
        X_features = model.extract_features(X)
        
        # Perform cross-validation
        cv_scores = cross_val_score(
            model.model,
            X_features,
            y,
            cv=cv_folds,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        # Convert to positive MSE
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        
        results = {
            'model_type': 'risk',
            'cv_folds': cv_folds,
            'mse_scores': mse_scores.tolist(),
            'rmse_scores': rmse_scores.tolist(),
            'mean_mse': np.mean(mse_scores),
            'std_mse': np.std(mse_scores),
            'mean_rmse': np.mean(rmse_scores),
            'std_rmse': np.std(rmse_scores)
        }
        
    elif model_type == 'classification':
        # For classification, we need to handle text data differently
        texts = data.get('description', [''] * len(data)).fillna('').tolist()
        labels = y.tolist()
        
        # Initialize model
        model = ClassificationModel()
        
        # Train ML fallback model for cross-validation
        model.train_ml_fallback(texts, labels)
        
        # Perform cross-validation using stratified k-fold
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
        
        accuracy_scores = []
        
        for train_idx, val_idx in skf.split(texts, labels):
            train_texts = [texts[i] for i in train_idx]
            train_labels = [labels[i] for i in train_idx]
            val_texts = [texts[i] for i in val_idx]
            val_labels = [labels[i] for i in val_idx]
            
            # Train model on fold
            fold_model = ClassificationModel()
            fold_model.train_ml_fallback(train_texts, train_labels)
            
            # Evaluate on validation fold
            correct = 0
            for text, true_label in zip(val_texts, val_labels):
                result = fold_model.classify_claim_type(text)
                if result['prediction'] == true_label:
                    correct += 1
            
            accuracy = correct / len(val_labels)
            accuracy_scores.append(accuracy)
        
        results = {
            'model_type': 'classification',
            'cv_folds': cv_folds,
            'accuracy_scores': accuracy_scores,
            'mean_accuracy': np.mean(accuracy_scores),
            'std_accuracy': np.std(accuracy_scores)
        }
    
    results['created_at'] = datetime.now().isoformat()
    
    print("Cross-validation completed!")
    return results


def compare_models(
    model_results: List[Dict[str, Any]],
    comparison_metric: str = 'accuracy'
) -> Dict[str, Any]:
    """
    Compare multiple models based on their performance.
    
    Args:
        model_results: List of model evaluation results
        comparison_metric: Metric to use for comparison
    
    Returns:
        Dictionary containing comparison results
    """
    print("Comparing models...")
    
    comparison_data = []
    
    for result in model_results:
        model_info = {
            'model_id': result.get('model_id', 'unknown'),
            'model_type': result.get('model_type', 'unknown'),
            'model_version': result.get('model_version', 'unknown'),
            'metric_value': None
        }
        
        # Extract metric value based on model type
        if result.get('model_type') == 'risk':
            if comparison_metric in result.get('test_metrics', {}):
                model_info['metric_value'] = result['test_metrics'][comparison_metric]
        elif result.get('model_type') == 'classification':
            if comparison_metric in result.get('test_metrics', {}):
                model_info['metric_value'] = result['test_metrics'][comparison_metric]
        
        comparison_data.append(model_info)
    
    # Sort by metric value (higher is better for most metrics)
    comparison_data.sort(key=lambda x: x['metric_value'] or 0, reverse=True)
    
    # Find best model
    best_model = comparison_data[0] if comparison_data else None
    
    results = {
        'comparison_metric': comparison_metric,
        'models': comparison_data,
        'best_model': best_model,
        'total_models': len(comparison_data),
        'created_at': datetime.now().isoformat()
    }
    
    print("Model comparison completed!")
    return results


def generate_training_report(
    training_results: Dict[str, Any],
    output_path: str = None
) -> str:
    """
    Generate a comprehensive training report.
    
    Args:
        training_results: Results from model training
        output_path: Path to save the report
    
    Returns:
        Path to the generated report
    """
    print("Generating training report...")
    
    # Create report content
    report_lines = [
        "# Model Training Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## Model Information",
        f"- Model Type: {training_results.get('model_type', 'Unknown')}",
        f"- Model Version: {training_results.get('model_version', 'Unknown')}",
        f"- Model ID: {training_results.get('model_id', 'Unknown')}",
        "",
        f"## Training Statistics",
        f"- Training Samples: {training_results.get('training_samples', 0)}",
        f"- Test Samples: {training_results.get('test_samples', 0)}",
        ""
    ]
    
    # Add training metrics
    if 'training_metrics' in training_results:
        report_lines.extend([
            "## Training Metrics",
            "```json",
            json.dumps(training_results['training_metrics'], indent=2),
            "```",
            ""
        ])
    
    # Add test metrics
    if 'test_metrics' in training_results:
        report_lines.extend([
            "## Test Metrics",
            "```json",
            json.dumps(training_results['test_metrics'], indent=2),
            "```",
            ""
        ])
    
    # Add feature importance for risk models
    if 'feature_importance' in training_results:
        report_lines.extend([
            "## Top 10 Feature Importance",
            ""
        ])
        
        for feature, importance in training_results.get('best_features', []):
            report_lines.append(f"- {feature}: {importance:.4f}")
        
        report_lines.append("")
    
    # Add method distribution for classification models
    if 'method_distribution' in training_results:
        report_lines.extend([
            "## Classification Method Distribution",
            ""
        ])
        
        for method, count in training_results['method_distribution'].items():
            report_lines.append(f"- {method}: {count}")
        
        report_lines.append("")
    
    # Join lines and save
    report_content = "\n".join(report_lines)
    
    if output_path is None:
        output_path = f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    print(f"Training report saved to: {output_path}")
    return output_path
