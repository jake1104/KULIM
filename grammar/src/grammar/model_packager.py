"""
Model Packaging Utility for KULIM Grammar

Consolidates all model files into a single .kg package for easy distribution.
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from .utils import get_data_dir
from .logger import logger
from .kg_format import KGFormat, encode_kg_from_directory, decode_kg_to_directory


class ModelPackager:
    """Handles packaging and unpacking of KULIM Grammar models."""
    
    # Model files to include in package
    MODEL_FILES = [
        "dictionary.pkl",
        "rust_trie.bin",
        "neural_model.pt",
        "neural_morph_model.pt",
        "syntax_patterns.json",
    ]
    
    @staticmethod
    def package_model(output_path: str, data_dir: Optional[str] = None) -> str:
        """
        Package all model files into a single .kg file.
        
        Args:
            output_path: Output path for the packaged model
            data_dir: Source directory containing model files (default: get_data_dir())
            
        Returns:
            Path to the created package file
        """
        if data_dir is None:
            data_dir = get_data_dir()
        
        # Ensure output path has .kg extension
        if not output_path.endswith('.kg'):
            if output_path.endswith('.tar.gz') or output_path.endswith('.model'):
                output_path = output_path.replace('.tar.gz', '.kg').replace('.model', '.kg')
            else:
                output_path = f"{output_path}.kg"
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Packaging model from {data_dir} to {output_path}")
        
        # Collect files to package
        files = []
        for filename in ModelPackager.MODEL_FILES:
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = f.read()
                files.append((filename, data))
                logger.debug(f"Added {filename} to package ({len(data)} bytes)")
            else:
                logger.warning(f"Model file not found: {filename}")
        
        # Encode to .kg format
        result_path = KGFormat.encode(files, output_path)
        
        file_size = os.path.getsize(result_path) / (1024 * 1024)  # MB
        logger.info(f"Model packaged successfully: {result_path} ({file_size:.2f} MB)")
        
        return result_path
    
    @staticmethod
    def unpack_model(package_path: str, target_dir: Optional[str] = None) -> str:
        """
        Unpack a model package to target directory.
        
        Args:
            package_path: Path to the .kg package file
            target_dir: Target directory to extract files (default: get_data_dir())
            
        Returns:
            Path to the directory containing extracted files
        """
        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Model package not found: {package_path}")
        
        if target_dir is None:
            target_dir = get_data_dir()
        
        logger.info(f"Unpacking model from {package_path} to {target_dir}")
        
        # Create target directory if needed
        os.makedirs(target_dir, exist_ok=True)
        
        # Decode .kg file
        extracted_files = decode_kg_to_directory(package_path, target_dir)
        logger.debug(f"Extracted {len(extracted_files)} files")
        
        logger.info(f"Model unpacked successfully to {target_dir}")
        
        return target_dir
    
    @staticmethod
    def load_from_package(package_path: str) -> str:
        """
        Load model from package to a temporary directory.
        
        Args:
            package_path: Path to the .kg package file
            
        Returns:
            Path to temporary directory containing extracted files
        """
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='kulim_model_')
        
        try:
            ModelPackager.unpack_model(package_path, temp_dir)
            return temp_dir
        except Exception as e:
            # Clean up on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
