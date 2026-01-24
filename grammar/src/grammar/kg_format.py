"""
KULIM Grammar (.kg) File Format Encoder/Decoder

Custom binary format for packaging KULIM Grammar models.

File Structure:
    [Header: 16 bytes]
        - Magic: 4 bytes ("KLGM")
        - Version: 2 bytes (major.minor)
        - File Count: 2 bytes
        - Reserved: 8 bytes
    
    [File Table: variable]
        For each file:
            - Filename Length: 2 bytes
            - Filename: variable (UTF-8)
            - File Size: 8 bytes
            - Offset: 8 bytes
    
    [Data Section: variable]
        Raw file data concatenated
"""
import struct
import os
from pathlib import Path
from typing import List, Tuple, BinaryIO


class KGFormat:
    """KULIM Grammar (.kg) file format handler"""
    
    MAGIC = b'KLGM'  # Magic number
    VERSION_MAJOR = 0
    VERSION_MINOR = 1
    HEADER_SIZE = 16
    
    @staticmethod
    def encode(files: List[Tuple[str, bytes]], output_path: str) -> str:
        """
        Encode files into .kg format
        
        Args:
            files: List of (filename, file_data) tuples
            output_path: Output .kg file path
            
        Returns:
            Path to created .kg file
        """
        # Ensure .kg extension
        if not output_path.endswith('.kg'):
            output_path = output_path.replace('.tar.gz', '.kg').replace('.model', '.kg')
            if not output_path.endswith('.kg'):
                output_path += '.kg'
        
        with open(output_path, 'wb') as f:
            # Write header
            KGFormat._write_header(f, len(files))
            
            # Calculate offsets
            file_table_size = sum(
                2 + len(name.encode('utf-8')) + 8 + 8 
                for name, _ in files
            )
            data_offset = KGFormat.HEADER_SIZE + file_table_size
            
            # Write file table
            current_offset = data_offset
            file_entries = []
            for filename, data in files:
                name_bytes = filename.encode('utf-8')
                file_entries.append((name_bytes, len(data), current_offset))
                current_offset += len(data)
            
            for name_bytes, size, offset in file_entries:
                # Filename length (2 bytes)
                f.write(struct.pack('<H', len(name_bytes)))
                # Filename
                f.write(name_bytes)
                # File size (8 bytes)
                f.write(struct.pack('<Q', size))
                # Offset (8 bytes)
                f.write(struct.pack('<Q', offset))
            
            # Write data section
            for _, data in files:
                f.write(data)
        
        return output_path
    
    @staticmethod
    def decode(kg_path: str) -> List[Tuple[str, bytes]]:
        """
        Decode .kg file into files
        
        Args:
            kg_path: Path to .kg file
            
        Returns:
            List of (filename, file_data) tuples
        """
        with open(kg_path, 'rb') as f:
            # Read and validate header
            magic, version_major, version_minor, file_count = KGFormat._read_header(f)
            
            if magic != KGFormat.MAGIC:
                raise ValueError(f"Invalid .kg file: bad magic number")
            
            # Read file table
            file_entries = []
            for _ in range(file_count):
                # Filename length
                name_len = struct.unpack('<H', f.read(2))[0]
                # Filename
                filename = f.read(name_len).decode('utf-8')
                # File size
                file_size = struct.unpack('<Q', f.read(8))[0]
                # Offset
                offset = struct.unpack('<Q', f.read(8))[0]
                
                file_entries.append((filename, file_size, offset))
            
            # Read file data
            files = []
            for filename, size, offset in file_entries:
                f.seek(offset)
                data = f.read(size)
                files.append((filename, data))
            
            return files
    
    @staticmethod
    def _write_header(f: BinaryIO, file_count: int):
        """Write .kg file header"""
        # Magic (4 bytes)
        f.write(KGFormat.MAGIC)
        # Version (2 bytes: major, minor)
        f.write(struct.pack('<BB', KGFormat.VERSION_MAJOR, KGFormat.VERSION_MINOR))
        # File count (2 bytes)
        f.write(struct.pack('<H', file_count))
        # Reserved (8 bytes)
        f.write(b'\x00' * 8)
    
    @staticmethod
    def _read_header(f: BinaryIO) -> Tuple[bytes, int, int, int]:
        """Read .kg file header"""
        magic = f.read(4)
        version_major, version_minor = struct.unpack('<BB', f.read(2))
        file_count = struct.unpack('<H', f.read(2))[0]
        f.read(8)  # Skip reserved
        
        return magic, version_major, version_minor, file_count


def encode_kg_from_directory(data_dir: str, output_path: str, file_list: List[str]) -> str:
    """
    Create .kg file from directory
    
    Args:
        data_dir: Source directory containing files
        output_path: Output .kg file path
        file_list: List of filenames to include
        
    Returns:
        Path to created .kg file
    """
    files = []
    for filename in file_list:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = f.read()
            files.append((filename, data))
    
    return KGFormat.encode(files, output_path)


def decode_kg_to_directory(kg_path: str, target_dir: str) -> List[str]:
    """
    Extract .kg file to directory
    
    Args:
        kg_path: Path to .kg file
        target_dir: Target directory for extraction
        
    Returns:
        List of extracted filenames
    """
    os.makedirs(target_dir, exist_ok=True)
    
    files = KGFormat.decode(kg_path)
    extracted = []
    
    for filename, data in files:
        filepath = os.path.join(target_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        extracted.append(filename)
    
    return extracted


if __name__ == "__main__":
    # Test encoder/decoder
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Encode: python kg_format.py encode <data_dir> <output.kg>")
        print("  Decode: python kg_format.py decode <input.kg> <target_dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "encode":
        data_dir = sys.argv[2]
        output_kg = sys.argv[3]
        
        # Default file list
        file_list = [
            "dictionary.pkl",
            "rust_trie.bin",
            "neural_model.pt",
            "neural_morph_model.pt",
            "syntax_patterns.json",
        ]
        
        result = encode_kg_from_directory(data_dir, output_kg, file_list)
        print(f"✓ Encoded to: {result}")
        
        # Show file size
        size_mb = os.path.getsize(result) / (1024 * 1024)
        print(f"  Size: {size_mb:.2f} MB")
        
    elif command == "decode":
        input_kg = sys.argv[2]
        target_dir = sys.argv[3]
        
        extracted = decode_kg_to_directory(input_kg, target_dir)
        print(f"✓ Decoded {len(extracted)} files to: {target_dir}")
        for filename in extracted:
            print(f"  - {filename}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
