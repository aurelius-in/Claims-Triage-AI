"""
Model explainability and interpretability for Claims Triage AI.

This module provides:
- SHAP integration for model explanations
- Feature importance analysis
- Prediction explanations
- Model interpretability utilities
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

import shap
from shap import TreeExplainer, LinearExplainer, KernelExplainer
from shap.plots import waterfall, force, summary, bar, beeswarm

from .models import RiskModel, ClassificationModel


class SHAPExplainer:
    """SHAP-based model explainer for risk and classification models."""
    
    def __init__(self, model, background_data: pd.DataFrame = None):
        self.model = model
        self.background_data = background_data
        self.explainer = None
        self.feature_names = []
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize the appropriate SHAP explainer based on model type."""
        if hasattr(self.model, 'model') and self.model.model is not None:
            # For RiskModel or other models with a sklearn/xgboost model
            if hasattr(self.model.model, 'feature_importances_'):
                # Tree-based model (XGBoost, Random Forest, etc.)
                self.explainer = TreeExplainer(self.model.model)
            elif hasattr(self.model.model, 'coef_'):
                # Linear model
                if self.background_data is not None:
                    self.explainer = LinearExplainer(self.model.model, self.background_data)
                else:
                    print("Warning: LinearExplainer requires background data")
            else:
                # Generic model - use KernelExplainer
                if self.background_data is not None:
                    self.explainer = KernelExplainer(self._model_predict, self.background_data)
                else:
                    print("Warning: KernelExplainer requires background data")
        
        # Set feature names
        if hasattr(self.model, 'feature_names'):
            self.feature_names = self.model.feature_names
        elif hasattr(self.model.model, 'feature_names_in_'):
            self.feature_names = self.model.model.feature_names_in_.tolist()
    
    def _model_predict(self, X):
        """Wrapper for model prediction to use with KernelExplainer."""
        if hasattr(self.model, 'predict'):
            return self.model.predict(X)
        else:
            return self.model.model.predict(X)
    
    def explain_prediction(self, data: pd.DataFrame, sample_idx: int = 0) -> Dict[str, Any]:
        """
        Explain a single prediction.
        
        Args:
            data: Input data for prediction
            sample_idx: Index of the sample to explain
        
        Returns:
            Dictionary containing SHAP values and explanation
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}
        
        try:
            # Prepare data
            if hasattr(self.model, 'extract_features'):
                # For RiskModel, extract features first
                features = self.model.extract_features(data.iloc[[sample_idx]])
                if hasattr(self.model, 'scaler'):
                    features = self.model.scaler.transform(features)
            else:
                features = data.iloc[[sample_idx]]
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # Handle different SHAP value formats
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # Take first class for binary classification
            
            # Get feature names
            feature_names = self.feature_names if self.feature_names else [f"Feature_{i}" for i in range(features.shape[1])]
            
            # Create explanation
            explanation = {
                'shap_values': shap_values[0].tolist(),
                'feature_names': feature_names,
                'feature_values': features.iloc[0].tolist(),
                'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
                'prediction': float(self._model_predict(features)[0]),
                'sample_idx': sample_idx,
                'explained_at': datetime.now().isoformat()
            }
            
            return explanation
            
        except Exception as e:
            return {"error": f"Failed to explain prediction: {str(e)}"}
    
    def explain_predictions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Explain multiple predictions.
        
        Args:
            data: Input data for predictions
        
        Returns:
            Dictionary containing SHAP values for all predictions
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}
        
        try:
            # Prepare data
            if hasattr(self.model, 'extract_features'):
                # For RiskModel, extract features first
                features = self.model.extract_features(data)
                if hasattr(self.model, 'scaler'):
                    features = self.model.scaler.transform(features)
            else:
                features = data
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # Handle different SHAP value formats
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # Take first class for binary classification
            
            # Get feature names
            feature_names = self.feature_names if self.feature_names else [f"Feature_{i}" for i in range(features.shape[1])]
            
            # Create explanation
            explanation = {
                'shap_values': shap_values.tolist(),
                'feature_names': feature_names,
                'feature_values': features.values.tolist(),
                'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
                'predictions': self._model_predict(features).tolist(),
                'explained_at': datetime.now().isoformat()
            }
            
            return explanation
            
        except Exception as e:
            return {"error": f"Failed to explain predictions: {str(e)}"}
    
    def get_feature_importance(self, data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Get feature importance based on SHAP values.
        
        Args:
            data: Data to calculate feature importance on (optional)
        
        Returns:
            Dictionary containing feature importance information
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}
        
        try:
            if data is not None:
                # Calculate SHAP values on provided data
                if hasattr(self.model, 'extract_features'):
                    features = self.model.extract_features(data)
                    if hasattr(self.model, 'scaler'):
                        features = self.model.scaler.transform(features)
                else:
                    features = data
                
                shap_values = self.explainer.shap_values(features)
                if isinstance(shap_values, list):
                    shap_values = shap_values[0]
                
                # Calculate mean absolute SHAP values
                mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
            else:
                # Use model's built-in feature importance if available
                if hasattr(self.model.model, 'feature_importances_'):
                    mean_abs_shap = self.model.model.feature_importances_
                else:
                    return {"error": "No data provided and model has no feature_importances_"}
            
            # Get feature names
            feature_names = self.feature_names if self.feature_names else [f"Feature_{i}" for i in range(len(mean_abs_shap))]
            
            # Create feature importance dictionary
            feature_importance = dict(zip(feature_names, mean_abs_shap.tolist()))
            
            # Sort by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'feature_importance': feature_importance,
                'sorted_features': sorted_features,
                'top_features': sorted_features[:10],
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get feature importance: {str(e)}"}
    
    def generate_explanation_plots(self, data: pd.DataFrame, output_dir: str = "plots") -> Dict[str, str]:
        """
        Generate SHAP explanation plots.
        
        Args:
            data: Data to generate plots for
            output_dir: Directory to save plots
        
        Returns:
            Dictionary containing paths to generated plots
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare data
            if hasattr(self.model, 'extract_features'):
                features = self.model.extract_features(data)
                if hasattr(self.model, 'scaler'):
                    features = self.model.scaler.transform(features)
            else:
                features = data
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Get feature names
            feature_names = self.feature_names if self.feature_names else [f"Feature_{i}" for i in range(features.shape[1])]
            
            plot_paths = {}
            
            # Summary plot
            plt.figure(figsize=(10, 8))
            summary(shap_values, features, feature_names=feature_names, show=False)
            summary_path = os.path.join(output_dir, "shap_summary.png")
            plt.savefig(summary_path, bbox_inches='tight', dpi=300)
            plt.close()
            plot_paths['summary'] = summary_path
            
            # Bar plot
            plt.figure(figsize=(10, 8))
            bar(shap_values, feature_names=feature_names, show=False)
            bar_path = os.path.join(output_dir, "shap_bar.png")
            plt.savefig(bar_path, bbox_inches='tight', dpi=300)
            plt.close()
            plot_paths['bar'] = bar_path
            
            # Beeswarm plot
            plt.figure(figsize=(10, 8))
            beeswarm(shap_values, feature_names=feature_names, show=False)
            beeswarm_path = os.path.join(output_dir, "shap_beeswarm.png")
            plt.savefig(beeswarm_path, bbox_inches='tight', dpi=300)
            plt.close()
            plot_paths['beeswarm'] = beeswarm_path
            
            # Waterfall plot for first sample
            plt.figure(figsize=(10, 8))
            waterfall(shap_values[0], feature_names=feature_names, show=False)
            waterfall_path = os.path.join(output_dir, "shap_waterfall.png")
            plt.savefig(waterfall_path, bbox_inches='tight', dpi=300)
            plt.close()
            plot_paths['waterfall'] = waterfall_path
            
            return plot_paths
            
        except Exception as e:
            return {"error": f"Failed to generate plots: {str(e)}"}


def explain_prediction(model, data: pd.DataFrame, sample_idx: int = 0) -> Dict[str, Any]:
    """
    Convenience function to explain a single prediction.
    
    Args:
        model: Trained model
        data: Input data
        sample_idx: Index of sample to explain
    
    Returns:
        Dictionary containing explanation
    """
    explainer = SHAPExplainer(model)
    return explainer.explain_prediction(data, sample_idx)


def generate_feature_importance(model, data: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Convenience function to generate feature importance.
    
    Args:
        model: Trained model
        data: Data to calculate importance on (optional)
    
    Returns:
        Dictionary containing feature importance
    """
    explainer = SHAPExplainer(model)
    return explainer.get_feature_importance(data)


def create_explanation_report(
    model,
    data: pd.DataFrame,
    output_dir: str = "explanation_reports"
) -> str:
    """
    Create a comprehensive explanation report.
    
    Args:
        model: Trained model
        data: Data to explain
        output_dir: Directory to save report
    
    Returns:
        Path to the generated report
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize explainer
    explainer = SHAPExplainer(model)
    
    # Generate explanations
    predictions_explanation = explainer.explain_predictions(data)
    feature_importance = explainer.get_feature_importance(data)
    
    # Generate plots
    plot_paths = explainer.generate_explanation_plots(data, output_dir)
    
    # Create report content
    report_lines = [
        "# Model Explanation Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Feature Importance",
        ""
    ]
    
    if 'sorted_features' in feature_importance:
        report_lines.append("### Top 10 Most Important Features")
        for feature, importance in feature_importance['sorted_features'][:10]:
            report_lines.append(f"- **{feature}**: {importance:.4f}")
        report_lines.append("")
    
    # Add prediction explanations for first few samples
    if 'shap_values' in predictions_explanation:
        report_lines.extend([
            "## Sample Predictions Explanation",
            ""
        ])
        
        num_samples = min(3, len(predictions_explanation['shap_values']))
        for i in range(num_samples):
            report_lines.extend([
                f"### Sample {i+1}",
                f"- **Prediction**: {predictions_explanation['predictions'][i]:.4f}",
                f"- **Base Value**: {predictions_explanation['base_value']:.4f}",
                ""
            ])
            
            # Top contributing features
            shap_values = predictions_explanation['shap_values'][i]
            feature_names = predictions_explanation['feature_names']
            
            # Sort by absolute SHAP value
            feature_contributions = sorted(
                zip(feature_names, shap_values),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            report_lines.append("**Top Contributing Features:**")
            for feature, contribution in feature_contributions[:5]:
                direction = "increases" if contribution > 0 else "decreases"
                report_lines.append(f"- {feature}: {contribution:.4f} ({direction} prediction)")
            report_lines.append("")
    
    # Add plot references
    if 'error' not in plot_paths:
        report_lines.extend([
            "## Generated Plots",
            ""
        ])
        
        plot_descriptions = {
            'summary': 'Summary plot showing feature importance and SHAP value distributions',
            'bar': 'Bar plot of mean absolute SHAP values',
            'beeswarm': 'Beeswarm plot showing SHAP value distributions',
            'waterfall': 'Waterfall plot for the first sample prediction'
        }
        
        for plot_type, description in plot_descriptions.items():
            if plot_type in plot_paths:
                report_lines.append(f"- **{plot_type.title()}**: {description}")
                report_lines.append(f"  - File: `{plot_paths[plot_type]}`")
        report_lines.append("")
    
    # Add metadata
    report_lines.extend([
        "## Report Metadata",
        f"- Model Type: {type(model).__name__}",
        f"- Data Samples: {len(data)}",
        f"- Features: {len(predictions_explanation.get('feature_names', []))}",
        f"- Generated At: {datetime.now().isoformat()}"
    ])
    
    # Save report
    report_content = "\n".join(report_lines)
    report_path = os.path.join(output_dir, f"explanation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    return report_path


def analyze_model_bias(
    model,
    data: pd.DataFrame,
    sensitive_features: List[str]
) -> Dict[str, Any]:
    """
    Analyze model bias with respect to sensitive features.
    
    Args:
        model: Trained model
        data: Data to analyze
        sensitive_features: List of sensitive feature names
    
    Returns:
        Dictionary containing bias analysis results
    """
    try:
        # Get predictions
        if hasattr(model, 'predict'):
            predictions = model.predict(data)
        else:
            predictions = model.model.predict(data)
        
        # Create analysis results
        bias_analysis = {
            'sensitive_features': sensitive_features,
            'analysis_results': {},
            'created_at': datetime.now().isoformat()
        }
        
        for feature in sensitive_features:
            if feature in data.columns:
                feature_values = data[feature].unique()
                feature_analysis = {}
                
                for value in feature_values:
                    mask = data[feature] == value
                    group_predictions = predictions[mask]
                    
                    feature_analysis[value] = {
                        'count': len(group_predictions),
                        'mean_prediction': float(np.mean(group_predictions)),
                        'std_prediction': float(np.std(group_predictions)),
                        'min_prediction': float(np.min(group_predictions)),
                        'max_prediction': float(np.max(group_predictions))
                    }
                
                bias_analysis['analysis_results'][feature] = feature_analysis
        
        return bias_analysis
        
    except Exception as e:
        return {"error": f"Failed to analyze model bias: {str(e)}"}


def create_interactive_explanation(
    model,
    data: pd.DataFrame,
    output_path: str = "interactive_explanation.html"
) -> str:
    """
    Create an interactive HTML explanation using SHAP.
    
    Args:
        model: Trained model
        data: Data to explain
        output_path: Path to save HTML file
    
    Returns:
        Path to the generated HTML file
    """
    try:
        explainer = SHAPExplainer(model)
        
        # Prepare data
        if hasattr(model, 'extract_features'):
            features = model.extract_features(data)
            if hasattr(model, 'scaler'):
                features = model.scaler.transform(features)
        else:
            features = data
        
        # Calculate SHAP values
        shap_values = explainer.explainer.shap_values(features)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Get feature names
        feature_names = explainer.feature_names if explainer.feature_names else [f"Feature_{i}" for i in range(features.shape[1])]
        
        # Create force plot
        force_plot = force(
            explainer.explainer.expected_value,
            shap_values,
            features,
            feature_names=feature_names,
            show=False
        )
        
        # Save as HTML
        shap.save_html(output_path, force_plot)
        
        return output_path
        
    except Exception as e:
        return f"Error creating interactive explanation: {str(e)}"
