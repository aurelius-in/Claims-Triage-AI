# ML/MLOps Module

This module provides a comprehensive machine learning and MLOps pipeline for the Claims Triage AI system. It includes model training, evaluation, explainability, and model management capabilities.

## 🏗️ Architecture

```
ml/
├── __init__.py              # Module exports
├── models.py               # Core ML models (RiskModel, ClassificationModel)
├── features.py             # Feature extraction and feature store
├── training.py             # Training and evaluation functions
├── explainability.py       # SHAP-based model explanations
├── registry.py             # Model registry and versioning
├── train.py               # Command-line training script
├── eval.py                # Command-line evaluation script
└── README.md              # This file
```

## 🚀 Quick Start

### Training a Risk Model

```bash
# Train a risk scoring model with hyperparameter tuning
python ml/train.py \
  --model-type risk \
  --data-path data/claims.csv \
  --target-column risk_score \
  --hyperparameter-tuning \
  --cross-validate \
  --generate-explanations
```

### Training a Classification Model

```bash
# Train a classification model with zero-shot LLM + ML fallback
python ml/train.py \
  --model-type classification \
  --data-path data/claims.csv \
  --text-column description \
  --target-column claim_type \
  --cross-validate
```

### Evaluating a Model

```bash
# Evaluate a trained model
python ml/eval.py \
  --model-id risk_model_risk_scoring \
  --data-path test_data.csv \
  --target-column risk_score \
  --generate-explanations \
  --analyze-bias state customer_tier
```

## 📊 Models

### RiskModel

XGBoost-based risk scoring model for claims assessment.

**Features:**
- Claim amount, policy duration, customer age
- Geographic risk factors, temporal features
- Document completeness, urgency indicators
- Customer history and claim frequency

**Usage:**
```python
from ml.models import RiskModel

# Initialize model
model = RiskModel()

# Train model
metrics = model.train(X_train, y_train)

# Make predictions
risk_scores = model.predict(X_test)
```

### ClassificationModel

Hybrid classification model using zero-shot LLM + ML fallback.

**Capabilities:**
- Claim type classification (auto, health, property, etc.)
- Urgency classification (low, medium, high, critical)
- Fraud detection
- Fallback to traditional ML when LLM confidence is low

**Usage:**
```python
from ml.models import ClassificationModel

# Initialize model
model = ClassificationModel()

# Classify claim type
result = model.classify_claim_type("Car accident with injuries")
print(result['prediction'])  # 'auto_collision'

# Classify urgency
urgency = model.classify_urgency(claim_data)
print(urgency['prediction'])  # 'high'
```

## 🔧 Feature Engineering

### FeatureExtractor

Automated feature extraction from raw claim data.

**Features Extracted:**
- Numerical features (amounts, durations, ratios)
- Categorical features (types, states, tiers)
- Text features (TF-IDF vectorization)
- Temporal features (day of week, month, quarter)
- Derived features (risk indicators, completeness scores)

**Usage:**
```python
from ml.features import FeatureExtractor

extractor = FeatureExtractor()
features = extractor.extract_claim_features(claim_data)
```

### FeatureStore

Redis-based feature store for caching and serving features.

**Capabilities:**
- Feature caching with TTL
- Batch feature operations
- Feature set management
- Statistics and monitoring

**Usage:**
```python
from ml.features import FeatureStore

store = FeatureStore()
store.store_features("claim_123", features_dict)
cached_features = store.get_features("claim_123")
```

## 🎯 Training Pipeline

### Training Functions

**Risk Model Training:**
```python
from ml.training import train_risk_model

results = train_risk_model(
    data=claims_data,
    target_column='risk_score',
    hyperparameter_tuning=True,
    save_model=True
)
```

**Classification Model Training:**
```python
from ml.training import train_classification_model

results = train_classification_model(
    data=claims_data,
    text_column='description',
    target_column='claim_type',
    use_zero_shot=True,
    train_ml_fallback=True
)
```

### Cross-Validation

```python
from ml.training import cross_validate_model

cv_results = cross_validate_model(
    data=claims_data,
    target_column='risk_score',
    model_type='risk',
    cv_folds=5
)
```

### Model Comparison

```python
from ml.training import compare_models

comparison = compare_models(
    model_results=[result1, result2, result3],
    comparison_metric='accuracy'
)
```

## 🔍 Model Explainability

### SHAP Integration

Comprehensive SHAP-based model explanations.

**Features:**
- Individual prediction explanations
- Feature importance analysis
- Global model explanations
- Interactive visualizations
- Bias analysis

**Usage:**
```python
from ml.explainability import SHAPExplainer

# Initialize explainer
explainer = SHAPExplainer(model)

# Explain single prediction
explanation = explainer.explain_prediction(data, sample_idx=0)

# Get feature importance
importance = explainer.get_feature_importance(data)

# Generate plots
plot_paths = explainer.generate_explanation_plots(data, "plots/")
```

### Bias Analysis

```python
from ml.explainability import analyze_model_bias

bias_results = analyze_model_bias(
    model=model,
    data=test_data,
    sensitive_features=['state', 'customer_tier']
)
```

## 📦 Model Registry

### Model Management

File-based model registry with versioning and metadata.

**Features:**
- Model versioning and tracking
- Metadata storage
- Performance history
- Import/export capabilities
- Registry validation

**Usage:**
```python
from ml.registry import save_model, load_model, list_models

# Save model
model_id = save_model(model, "my_risk_model", metadata=metrics)

# Load model
model = load_model(model_id)

# List all models
models = list_models()
```

### Registry Operations

```python
from ml.registry import (
    copy_model,
    export_model,
    import_model,
    cleanup_old_models,
    validate_model_registry
)

# Copy model
new_id = copy_model("source_model", "target_model")

# Export model
export_path = export_model("model_id", export_path="exports/")

# Import model
imported_id = import_model("exports/model_export/")

# Cleanup old versions
deleted_count = cleanup_old_models(max_versions_per_model=5)

# Validate registry
validation = validate_model_registry()
```

## 🛠️ Command-Line Tools

### Training Script (`train.py`)

```bash
# Basic training
python ml/train.py --model-type risk --data-path data.csv --target-column risk_score

# Advanced training with all features
python ml/train.py \
  --model-type risk \
  --data-path data.csv \
  --target-column risk_score \
  --hyperparameter-tuning \
  --cross-validate \
  --generate-explanations \
  --output-dir training_outputs
```

**Options:**
- `--model-type`: `risk` or `classification`
- `--data-path`: Path to training data
- `--target-column`: Name of target column
- `--text-column`: Text column (for classification)
- `--hyperparameter-tuning`: Enable HP tuning
- `--cross-validate`: Perform cross-validation
- `--generate-explanations`: Generate SHAP explanations
- `--output-dir`: Output directory for results

### Evaluation Script (`eval.py`)

```bash
# Basic evaluation
python ml/eval.py --model-id model_id --data-path test.csv --target-column risk_score

# Comprehensive evaluation
python ml/eval.py \
  --model-id model_id \
  --data-path test.csv \
  --target-column risk_score \
  --generate-explanations \
  --analyze-bias state customer_tier \
  --create-interactive \
  --compare-models model1 model2
```

**Options:**
- `--model-id`: ID of model to evaluate
- `--data-path`: Path to test data
- `--target-column`: Name of target column
- `--generate-explanations`: Generate SHAP explanations
- `--analyze-bias`: Analyze bias for specified features
- `--create-interactive`: Create interactive HTML explanation
- `--compare-models`: Compare multiple models

## 📈 Makefile Commands

```bash
# Train risk model
make ml-train-risk

# Train classification model
make ml-train-classification

# Evaluate model (set MODEL_ID)
make ml-eval MODEL_ID=risk_model_risk_scoring

# List models in registry
make ml-list-models

# Cleanup old model versions
make ml-cleanup

# Validate model registry
make ml-validate-registry
```

## 📊 Output Structure

### Training Outputs

```
training_outputs/
├── training_results_20231201_120000.json
├── training_report.md
├── cv_results_20231201_120000.json
└── explanations/
    ├── explanation_report_20231201_120000.md
    ├── shap_summary.png
    ├── shap_bar.png
    ├── shap_beeswarm.png
    └── shap_waterfall.png
```

### Evaluation Outputs

```
evaluation_outputs/
├── evaluation_results_20231201_120000.json
├── bias_analysis_20231201_120000.json
├── model_comparison_20231201_120000.json
├── interactive_explanation.html
└── explanations/
    └── explanation_report_20231201_120000.md
```

## 🔧 Configuration

### Model Configuration

Models can be configured through their constructors:

```python
# Risk model configuration
risk_model = RiskModel(
    model_name="custom_risk_model"
)

# Classification model configuration
class_model = ClassificationModel(
    model_name="custom_classification_model"
)
```

### Feature Store Configuration

```python
# Redis configuration
feature_store = FeatureStore(
    redis_url="redis://localhost:6379",
    cache_ttl=3600  # 1 hour
)
```

### Registry Configuration

```python
# Registry path configuration
registry = ModelRegistry(
    registry_path="custom/models/path"
)
```

## 🧪 Testing

### Unit Tests

```bash
# Run ML module tests
cd backend
python -m pytest tests/test_ml_*.py -v
```

### Integration Tests

```bash
# Test full training pipeline
python -c "
from ml.training import train_risk_model
import pandas as pd

# Create test data
data = pd.DataFrame({
    'claim_amount': [1000, 5000, 10000],
    'risk_score': [0.1, 0.5, 0.9]
})

# Test training
results = train_risk_model(data, 'risk_score', save_model=False)
print('Training successful:', results)
"
```

## 📚 Best Practices

### Data Preparation

1. **Clean your data**: Remove duplicates, handle missing values
2. **Feature engineering**: Create meaningful derived features
3. **Data validation**: Ensure data quality and consistency
4. **Train/test split**: Use proper validation strategies

### Model Training

1. **Start simple**: Begin with basic models before adding complexity
2. **Cross-validation**: Always use CV for reliable performance estimates
3. **Hyperparameter tuning**: Use grid search or Bayesian optimization
4. **Monitor overfitting**: Check training vs validation performance

### Model Management

1. **Version control**: Always version your models
2. **Metadata tracking**: Store training parameters and performance metrics
3. **Regular evaluation**: Continuously monitor model performance
4. **Model comparison**: Compare new models against baselines

### Explainability

1. **Always explain**: Generate explanations for important predictions
2. **Monitor bias**: Regularly check for bias in sensitive features
3. **Document decisions**: Keep records of model decisions and rationale
4. **Stakeholder communication**: Make explanations accessible to non-technical users

## 🚨 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the backend directory
cd backend

# Add parent directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Memory Issues:**
```python
# Use smaller sample sizes for explanations
explainer.generate_explanation_plots(data.sample(100))
```

**Model Loading Errors:**
```python
# Check if model exists
from ml.registry import list_models
models = list_models()
print(f"Available models: {models}")
```

**SHAP Errors:**
```python
# Ensure SHAP is properly installed
pip install shap==0.44.0

# For tree-based models, use TreeExplainer
from shap import TreeExplainer
explainer = TreeExplainer(model.model)
```

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the test files for usage examples
3. Check the model registry for available models
4. Validate your data format and column names

## 🔄 Version History

- **v1.0.0**: Initial release with basic ML pipeline
- **v1.1.0**: Added SHAP explainability
- **v1.2.0**: Enhanced model registry and versioning
- **v1.3.0**: Added bias analysis and interactive explanations
