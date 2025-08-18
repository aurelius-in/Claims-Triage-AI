"""
Model registry and versioning for Claims Triage AI.

This module provides:
- Model saving and loading utilities
- Model versioning and metadata management
- Model registry operations
- Model lifecycle management
"""

import os
import json
import pickle
import shutil
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from .models import ModelRegistry, ModelVersion, BaseModel, RiskModel, ClassificationModel


def save_model(
    model: BaseModel,
    model_name: str,
    version: str = None,
    metadata: Dict[str, Any] = None,
    registry_path: str = "ml/models"
) -> str:
    """
    Save a model to the registry.
    
    Args:
        model: Model to save
        model_name: Name of the model
        version: Version string (auto-generated if None)
        metadata: Additional metadata to store
        registry_path: Path to the model registry
    
    Returns:
        Model ID of the saved model
    """
    if version is None:
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize registry
    registry = ModelRegistry(registry_path)
    
    # Prepare metadata
    if metadata is None:
        metadata = {}
    
    # Add default metadata
    metadata.update({
        'model_name': model_name,
        'model_type': model.model_type,
        'created_at': datetime.now().isoformat(),
        'feature_count': len(model.feature_names) if hasattr(model, 'feature_names') else 0
    })
    
    # Register model
    model_id = registry.register_model(model, version, metadata)
    
    print(f"Model saved successfully: {model_id}")
    return model_id


def load_model(
    model_id: str,
    version: str = None,
    registry_path: str = "ml/models"
) -> Optional[BaseModel]:
    """
    Load a model from the registry.
    
    Args:
        model_id: ID of the model to load
        version: Version to load (latest if None)
        registry_path: Path to the model registry
    
    Returns:
        Loaded model or None if not found
    """
    registry = ModelRegistry(registry_path)
    model = registry.get_model(model_id, version)
    
    if model is None:
        print(f"Model {model_id} not found")
        return None
    
    print(f"Model loaded successfully: {model_id}")
    return model


def list_models(registry_path: str = "ml/models") -> List[Dict[str, Any]]:
    """
    List all models in the registry.
    
    Args:
        registry_path: Path to the model registry
    
    Returns:
        List of model information dictionaries
    """
    registry = ModelRegistry(registry_path)
    models = registry.list_models()
    
    print(f"Found {len(models)} models in registry")
    return models


def list_model_versions(
    model_id: str,
    registry_path: str = "ml/models"
) -> List[Dict[str, Any]]:
    """
    List all versions of a specific model.
    
    Args:
        model_id: ID of the model
        registry_path: Path to the model registry
    
    Returns:
        List of version information dictionaries
    """
    registry = ModelRegistry(registry_path)
    versions = registry.list_versions(model_id)
    
    print(f"Found {len(versions)} versions for model {model_id}")
    return versions


def get_model_metadata(
    model_id: str,
    version: str = None,
    registry_path: str = "ml/models"
) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific model version.
    
    Args:
        model_id: ID of the model
        version: Version to get metadata for (latest if None)
        registry_path: Path to the model registry
    
    Returns:
        Model metadata dictionary or None if not found
    """
    registry = ModelRegistry(registry_path)
    
    if version is None:
        # Get latest version
        model_info = registry.registry["models"].get(model_id)
        if not model_info or not model_info["versions"]:
            return None
        version = model_info["versions"][-1]["version"]
    
    version_id = f"{model_id}_v{version}"
    version_info = registry.registry["versions"].get(version_id)
    
    if version_info is None:
        print(f"Model version {version_id} not found")
        return None
    
    return version_info["metadata"]


def delete_model(
    model_id: str,
    version: str = None,
    registry_path: str = "ml/models"
) -> bool:
    """
    Delete a model from the registry.
    
    Args:
        model_id: ID of the model to delete
        version: Version to delete (all versions if None)
        registry_path: Path to the model registry
    
    Returns:
        True if deletion was successful
    """
    registry = ModelRegistry(registry_path)
    
    if version is None:
        # Delete all versions
        model_info = registry.registry["models"].get(model_id)
        if not model_info:
            print(f"Model {model_id} not found")
            return False
        
        # Delete all version files
        for version_info in model_info["versions"]:
            version_path = version_info["model_path"]
            try:
                if os.path.exists(f"{version_path}.pkl"):
                    os.remove(f"{version_path}.pkl")
                if os.path.exists(f"{version_path}_metadata.json"):
                    os.remove(f"{version_path}_metadata.json")
            except Exception as e:
                print(f"Error deleting version files: {e}")
        
        # Remove from registry
        del registry.registry["models"][model_id]
        
        # Remove version entries
        version_keys = [k for k in registry.registry["versions"].keys() if k.startswith(f"{model_id}_v")]
        for key in version_keys:
            del registry.registry["versions"][key]
        
        registry._save_registry()
        print(f"All versions of model {model_id} deleted")
        return True
    
    else:
        # Delete specific version
        version_id = f"{model_id}_v{version}"
        version_info = registry.registry["versions"].get(version_id)
        
        if version_info is None:
            print(f"Model version {version_id} not found")
            return False
        
        # Delete version files
        version_path = version_info["model_path"]
        try:
            if os.path.exists(f"{version_path}.pkl"):
                os.remove(f"{version_path}.pkl")
            if os.path.exists(f"{version_path}_metadata.json"):
                os.remove(f"{version_path}_metadata.json")
        except Exception as e:
            print(f"Error deleting version files: {e}")
            return False
        
        # Remove from registry
        del registry.registry["versions"][version_id]
        
        # Remove from model versions list
        model_info = registry.registry["models"].get(model_id)
        if model_info:
            model_info["versions"] = [
                v for v in model_info["versions"] 
                if v["version"] != version
            ]
            
            # Remove model if no versions left
            if not model_info["versions"]:
                del registry.registry["models"][model_id]
        
        registry._save_registry()
        print(f"Model version {version_id} deleted")
        return True


def copy_model(
    source_model_id: str,
    target_model_id: str,
    source_version: str = None,
    target_version: str = None,
    registry_path: str = "ml/models"
) -> str:
    """
    Copy a model to create a new version or model.
    
    Args:
        source_model_id: ID of the source model
        target_model_id: ID of the target model
        source_version: Source version (latest if None)
        target_version: Target version (auto-generated if None)
        registry_path: Path to the model registry
    
    Returns:
        ID of the copied model
    """
    if target_version is None:
        target_version = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Load source model
    source_model = load_model(source_model_id, source_version, registry_path)
    if source_model is None:
        raise ValueError(f"Source model {source_model_id} not found")
    
    # Get source metadata
    source_metadata = get_model_metadata(source_model_id, source_version, registry_path)
    
    # Update metadata for target
    target_metadata = source_metadata.copy() if source_metadata else {}
    target_metadata.update({
        'copied_from': f"{source_model_id}_v{source_version or 'latest'}",
        'copied_at': datetime.now().isoformat()
    })
    
    # Save as new model
    target_model_id_full = save_model(
        source_model,
        target_model_id,
        target_version,
        target_metadata,
        registry_path
    )
    
    print(f"Model copied: {source_model_id} -> {target_model_id_full}")
    return target_model_id_full


def export_model(
    model_id: str,
    version: str = None,
    export_path: str = None,
    registry_path: str = "ml/models"
) -> str:
    """
    Export a model to a portable format.
    
    Args:
        model_id: ID of the model to export
        version: Version to export (latest if None)
        export_path: Path to export to (auto-generated if None)
        registry_path: Path to the model registry
    
    Returns:
        Path to the exported model
    """
    # Load model
    model = load_model(model_id, version, registry_path)
    if model is None:
        raise ValueError(f"Model {model_id} not found")
    
    # Get metadata
    metadata = get_model_metadata(model_id, version, registry_path)
    
    # Generate export path
    if export_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = f"exports/{model_id}_{timestamp}"
    
    # Create export directory
    os.makedirs(export_path, exist_ok=True)
    
    # Save model
    model.save(os.path.join(export_path, "model"))
    
    # Save metadata
    with open(os.path.join(export_path, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Create export manifest
    manifest = {
        'model_id': model_id,
        'version': version,
        'exported_at': datetime.now().isoformat(),
        'model_type': model.model_type,
        'files': [
            'model.pkl',
            'model_metadata.json',
            'metadata.json'
        ]
    }
    
    with open(os.path.join(export_path, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Model exported to: {export_path}")
    return export_path


def import_model(
    import_path: str,
    model_id: str = None,
    version: str = None,
    registry_path: str = "ml/models"
) -> str:
    """
    Import a model from an exported format.
    
    Args:
        import_path: Path to the exported model
        model_id: ID for the imported model (from manifest if None)
        version: Version for the imported model (from manifest if None)
        registry_path: Path to the model registry
    
    Returns:
        ID of the imported model
    """
    # Load manifest
    manifest_path = os.path.join(import_path, "manifest.json")
    if not os.path.exists(manifest_path):
        raise ValueError(f"Manifest not found at {manifest_path}")
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Use manifest values if not provided
    if model_id is None:
        model_id = manifest['model_id']
    if version is None:
        version = manifest.get('version') or datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Load metadata
    metadata_path = os.path.join(import_path, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Update metadata
    metadata.update({
        'imported_at': datetime.now().isoformat(),
        'imported_from': import_path
    })
    
    # Determine model type and load
    model_type = manifest.get('model_type', 'unknown')
    
    if 'risk' in model_type:
        model = RiskModel()
    elif 'classification' in model_type:
        model = ClassificationModel()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Load model
    model.load(os.path.join(import_path, "model"))
    
    # Save to registry
    imported_model_id = save_model(
        model,
        model_id,
        version,
        metadata,
        registry_path
    )
    
    print(f"Model imported: {imported_model_id}")
    return imported_model_id


def get_model_performance_history(
    model_id: str,
    registry_path: str = "ml/models"
) -> List[Dict[str, Any]]:
    """
    Get performance history for a model across all versions.
    
    Args:
        model_id: ID of the model
        registry_path: Path to the model registry
    
    Returns:
        List of performance metrics for each version
    """
    versions = list_model_versions(model_id, registry_path)
    
    performance_history = []
    for version_info in versions:
        metadata = version_info.get("metadata", {})
        
        # Extract performance metrics
        metrics = metadata.get("metrics", {})
        
        performance_record = {
            'version': version_info['version'],
            'created_at': version_info['created_at'],
            'metrics': metrics,
            'model_type': metadata.get('model_type', 'unknown'),
            'feature_count': metadata.get('feature_count', 0)
        }
        
        performance_history.append(performance_record)
    
    # Sort by creation date
    performance_history.sort(key=lambda x: x['created_at'])
    
    return performance_history


def cleanup_old_models(
    max_versions_per_model: int = 5,
    registry_path: str = "ml/models"
) -> int:
    """
    Clean up old model versions, keeping only the most recent ones.
    
    Args:
        max_versions_per_model: Maximum number of versions to keep per model
        registry_path: Path to the model registry
    
    Returns:
        Number of versions deleted
    """
    registry = ModelRegistry(registry_path)
    deleted_count = 0
    
    for model_id, model_info in registry.registry["models"].items():
        versions = model_info["versions"]
        
        if len(versions) > max_versions_per_model:
            # Sort by creation date (oldest first)
            versions.sort(key=lambda x: x['created_at'])
            
            # Delete oldest versions
            versions_to_delete = versions[:-max_versions_per_model]
            
            for version_info in versions_to_delete:
                version = version_info['version']
                if delete_model(model_id, version, registry_path):
                    deleted_count += 1
    
    print(f"Cleaned up {deleted_count} old model versions")
    return deleted_count


def validate_model_registry(registry_path: str = "ml/models") -> Dict[str, Any]:
    """
    Validate the model registry for consistency and integrity.
    
    Args:
        registry_path: Path to the model registry
    
    Returns:
        Validation results
    """
    registry = ModelRegistry(registry_path)
    
    validation_results = {
        'total_models': len(registry.registry["models"]),
        'total_versions': len(registry.registry["versions"]),
        'errors': [],
        'warnings': [],
        'validated_at': datetime.now().isoformat()
    }
    
    # Check each model
    for model_id, model_info in registry.registry["models"].items():
        versions = model_info["versions"]
        
        if not versions:
            validation_results['warnings'].append(f"Model {model_id} has no versions")
            continue
        
        # Check each version
        for version_info in versions:
            version_path = version_info["model_path"]
            
            # Check if files exist
            model_file = f"{version_path}.pkl"
            metadata_file = f"{version_path}_metadata.json"
            
            if not os.path.exists(model_file):
                validation_results['errors'].append(
                    f"Model file missing: {model_file}"
                )
            
            if not os.path.exists(metadata_file):
                validation_results['errors'].append(
                    f"Metadata file missing: {metadata_file}"
                )
    
    # Check for orphaned version entries
    for version_id, version_info in registry.registry["versions"].items():
        model_id = version_id.rsplit('_v', 1)[0]
        if model_id not in registry.registry["models"]:
            validation_results['warnings'].append(
                f"Orphaned version entry: {version_id}"
            )
    
    validation_results['is_valid'] = len(validation_results['errors']) == 0
    
    print(f"Registry validation completed: {validation_results['total_models']} models, "
          f"{validation_results['total_versions']} versions, "
          f"{len(validation_results['errors'])} errors, "
          f"{len(validation_results['warnings'])} warnings")
    
    return validation_results
