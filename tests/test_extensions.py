import pytest
import sys


def test_rust_extension_availability():
    try:
        from grammar.rust_ext import HAS_RUST, RustTrieWrapper

        if HAS_RUST:
            trie = RustTrieWrapper()
            trie.insert("테스트", "NNG", "테스트")
            res = trie.search("테스트")
            assert res is not None
        else:
            pytest.skip("Rust extension not compiled/available")
    except ImportError:
        pytest.skip("Rust module import failed")


def test_gpu_extension_availability():
    try:
        from grammar.gpu import get_gpu_info

        info = get_gpu_info()
        if not info.get("available"):
            pytest.skip("GPU not available")
        else:
            assert "device_name" in info
    except ImportError:
        pytest.skip("GPU module (cupy) not installed")
