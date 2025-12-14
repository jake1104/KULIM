import pytest
from unittest.mock import MagicMock
from grammar import MorphAnalyzer
from grammar.gpu import GPUBatchAnalyzer


class MockNeuralWrapper:
    def __init__(self):
        self.device = "cuda:0"

    def predict_morph_batch(self, eojeols):
        # Mock behavior: just return dummy results
        return [[(e, "NNG")] for e in eojeols]


def test_gpu_analyzer_init():
    # Mock MorphAnalyzer
    analyzer = MagicMock(spec=MorphAnalyzer)
    analyzer.use_neural = False
    analyzer.neural_wrapper = None

    gpu_analyzer = GPUBatchAnalyzer(analyzer)
    assert gpu_analyzer.device == "cpu"  # Default fallback


def test_gpu_analyzer_cpu_fallback():
    # Real MorphAnalyzer with mocking analyze
    analyzer = MagicMock(spec=MorphAnalyzer)
    analyzer.use_neural = False
    analyzer.analyze.return_value = [("test", "NNG")]

    gpu_analyzer = GPUBatchAnalyzer(analyzer)
    sentences = ["t1", "t2"]

    results = gpu_analyzer.analyze_batch(sentences)

    assert len(results) == 2
    assert results[0] == [("test", "NNG")]
    assert gpu_analyzer.stats["cpu_parallel_docs"] == 2


def test_gpu_analyzer_neural_batch():
    # Mock analyzer with neural wrapper
    analyzer = MagicMock(spec=MorphAnalyzer)
    analyzer.use_neural = True
    analyzer.neural_wrapper = MockNeuralWrapper()
    analyzer.trie = None  # Disable correction

    gpu_analyzer = GPUBatchAnalyzer(analyzer)

    sentences = ["A B", "C"]
    # "A B" -> ["A", "B"]
    # "C" -> ["C"]

    results = gpu_analyzer.analyze_batch(sentences, batch_size=2)

    # Expected:
    # 1. "A B" -> predict(["A", "B"]) -> [[("A", "NNG")], [("B", "NNG")]] -> flatten -> [("A", "NNG"), ("B", "NNG")]
    # 2. "C" -> predict(["C"]) -> [[("C", "NNG")]] -> flatten -> [("C", "NNG")]

    assert len(results) == 2
    assert len(results[0]) == 2
    assert results[0][0] == ("A", "NNG")
    assert results[1][0] == ("C", "NNG")
    assert gpu_analyzer.stats["gpu_docs"] == 2
