"""
Training script for ScanLabel AI health classification model.
Downloads Open Food Facts dataset, preprocesses data, and trains a RandomForestClassifier.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.preprocess import clean_dataset, create_health_label, extract_features
from utils.logger import get_logger

logger = get_logger()


def download_dataset(url: str = None, local_path: str = None) -> pd.DataFrame:
    """
    Load Open Food Facts dataset.
    
    For this project, we'll use a sample approach. In production, you would:
    1. Download the full dataset from https://world.openfoodfacts.org/data
    2. Or use the API to collect training data
    
    Args:
        url: Optional URL to download dataset from
        local_path: Optional path to local CSV file
        
    Returns:
        DataFrame with product data
    """
    # If local file exists, use it
    if local_path and os.path.exists(local_path):
        logger.info(f"Loading dataset from {local_path}...")
        # Read in chunks to handle large files
        try:
            df = pd.read_csv(local_path, low_memory=False, nrows=50000)  # Limit rows for faster training
            logger.info(f"Loaded {len(df)} rows from local file")
            return df
        except Exception as e:
            logger.error(f"Error loading local file: {e}")
    
    # Otherwise, create a sample dataset for demonstration
    # In production, download from: https://world.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz
    logger.info("No local dataset found. Creating sample dataset for demonstration...")
    logger.info("NOTE: For production use, download the full dataset from:")
    logger.info("https://world.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz")
    
    # Generate balanced synthetic training data
    np.random.seed(42)
    n_samples_per_class = 5000
    
    # Healthy products (low sugar, fat, salt)
    healthy_data = {
        'energy_100g': np.random.uniform(20, 150, n_samples_per_class),
        'fat_100g': np.random.uniform(0, 3, n_samples_per_class),
        'sugars_100g': np.random.uniform(0, 5, n_samples_per_class),
        'salt_100g': np.random.uniform(0, 0.3, n_samples_per_class),
        'fiber_100g': np.random.uniform(2, 15, n_samples_per_class),
        'proteins_100g': np.random.uniform(5, 25, n_samples_per_class)
    }
    
    # Moderate products
    moderate_data = {
        'energy_100g': np.random.uniform(100, 300, n_samples_per_class),
        'fat_100g': np.random.uniform(3, 10, n_samples_per_class),
        'sugars_100g': np.random.uniform(5, 10, n_samples_per_class),
        'salt_100g': np.random.uniform(0.3, 1.0, n_samples_per_class),
        'fiber_100g': np.random.uniform(1, 8, n_samples_per_class),
        'proteins_100g': np.random.uniform(3, 15, n_samples_per_class)
    }
    
    # Unhealthy products (high sugar, fat, or salt)
    unhealthy_data = {
        'energy_100g': np.random.uniform(200, 600, n_samples_per_class),
        'fat_100g': np.random.uniform(10, 50, n_samples_per_class),
        'sugars_100g': np.random.uniform(10, 80, n_samples_per_class),
        'salt_100g': np.random.uniform(1.0, 5.0, n_samples_per_class),
        'fiber_100g': np.random.uniform(0, 5, n_samples_per_class),
        'proteins_100g': np.random.uniform(0, 10, n_samples_per_class)
    }
    
    # Combine all data
    all_data = {key: np.concatenate([healthy_data[key], moderate_data[key], unhealthy_data[key]]) 
                for key in healthy_data.keys()}
    
    df = pd.DataFrame(all_data)
    logger.info(f"Generated {len(df)} balanced synthetic samples for training")
    
    return df


def train_model(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Train RandomForestClassifier on nutrition data.
    
    Args:
        df: DataFrame with features and health_label
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Trained model and test accuracy
    """
    # Extract features and target
    X = extract_features(df)
    y = df['health_label']
    
    # Split data (remove stratify if classes are too imbalanced)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
    except ValueError:
        # If stratification fails, split without it
        logger.warning("Stratified split failed, using regular split")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
    
    logger.info(f"\nTraining set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    logger.info(f"\nClass distribution in training set:")
    logger.info(f"{y_train.value_counts()}")
    
    # Train RandomForestClassifier
    logger.info("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"\nModel Accuracy: {accuracy:.4f}")
    logger.info("\nClassification Report:")
    logger.info(f"\n{classification_report(y_test, y_pred)}")
    
    # Feature importance
    logger.info("\nFeature Importances:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    logger.info(f"\n{feature_importance}")
    
    return model, accuracy


def main():
    """
    Main training pipeline.
    """
    logger.info("=" * 60)
    logger.info("ScanLabel AI - Model Training Pipeline")
    logger.info("=" * 60)
    
    # Step 1: Load dataset
    logger.info("\n[Step 1] Loading dataset...")
    df = download_dataset()
    
    # Step 2: Clean data
    logger.info("\n[Step 2] Cleaning dataset...")
    df_clean = clean_dataset(df)
    logger.info(f"Cleaned dataset: {len(df_clean)} rows (removed {len(df) - len(df_clean)} rows)")
    
    # Step 3: Create health labels
    logger.info("\n[Step 3] Creating health labels...")
    df_labeled = create_health_label(df_clean)
    logger.info("\nHealth label distribution:")
    logger.info(f"{df_labeled['health_label'].value_counts()}")
    
    # Step 4: Train model
    logger.info("\n[Step 4] Training model...")
    model, accuracy = train_model(df_labeled)
    
    # Step 5: Save model
    logger.info("\n[Step 5] Saving model...")
    model_path = 'model.pkl'
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Training completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

