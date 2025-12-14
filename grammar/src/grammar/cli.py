import argparse
import sys
import os
from .analyzer import MorphAnalyzer
from .syntax import SyntaxAnalyzer
from .utils import get_data_dir


def main():
    # Version check handled by package manager

    parser = argparse.ArgumentParser(description="KULIM Morphological Analyzer CLI")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Subcommands"
    )

    # Command: Analyze (Default usage)
    analyze_parser = subparsers.add_parser(
        "analyze", aliases=["run"], help="Analyze text"
    )
    analyze_parser.add_argument("text", nargs="?", help="Text to analyze")
    analyze_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    analyze_parser.add_argument(
        "--rust", action="store_true", help="Use Rust acceleration"
    )
    analyze_parser.add_argument(
        "--gpu", action="store_true", help="Use GPU acceleration"
    )
    analyze_parser.add_argument(
        "--neural", action="store_true", help="Use Transformer Neural Model"
    )

    # Command: Train
    train_parser = subparsers.add_parser("train", help="Train model")
    train_parser.add_argument("corpus", nargs="?", help="Path to corpus file")
    train_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive training mode"
    )
    train_parser.add_argument(
        "--neural",
        action="store_true",
        default=True,
        help="Train Neural Models (Default: True)",
    )
    train_parser.add_argument(
        "--no-neural",
        action="store_false",
        dest="neural",
        help="Disable Neural Training",
    )
    train_parser.add_argument("--device", default="cpu", help="Device (cpu/cuda)")
    train_parser.add_argument(
        "--epochs", type=int, default=10, help="Number of epochs for neural training"
    )
    train_parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch size for neural training"
    )
    train_parser.add_argument(
        "--rust", action="store_true", help="Use Rust acceleration for training"
    )

    # Command: Benchmark
    bench_parser = subparsers.add_parser(
        "benchmark", aliases=["bench"], help="Run performance benchmark"
    )
    bench_parser.add_argument(
        "--rust", action="store_true", help="Include Rust in benchmark"
    )

    args = parser.parse_args()

    if args.command in ["analyze", "run"]:
        handle_analyze(args)
    elif args.command == "train":
        handle_train(args)
    elif args.command in ["benchmark", "bench"]:
        handle_benchmark(args)


def handle_analyze(args):
    if not args.text and not args.interactive:
        print("Error: Please provide text to analyze or use --interactive (-i)")
        sys.exit(1)

    print("Initializing MorphAnalyzer...")
    analyzer = MorphAnalyzer(
        use_double_array=True,
        use_sejong=True,
        use_rust=args.rust,
        use_gpu=args.gpu,
        use_neural=getattr(args, "neural", False),
        debug=False,
    )
    syntax_analyzer = SyntaxAnalyzer(use_neural=getattr(args, "neural", False))

    print("Optimization enabled: " + (f"Rust={args.rust}, GPU={args.gpu}"))

    if args.text:
        result = analyzer.analyze(args.text)
        print(f"\nInput: {args.text}")
        print(f"Morphs: {format_result(result)}")

        # Syntax Analysis
        syntax_result = syntax_analyzer.analyze(text=args.text, morph_analyzer=analyzer)
        print("Syntax: ", end="")
        for word, pos, comp in syntax_result:
            print(f"{word}({comp.value}) ", end="")
        print()

    if args.interactive:
        print("\nEntering interactive analysis mode (Type 'exit' to quit).")
        while True:
            try:
                text = input("\n>>> ")
                if text.strip().lower() in ["exit", "quit"]:
                    break
                if not text.strip():
                    continue

                if text.startswith("!train"):
                    print(
                        "⚠ 'train' command is moved to 'python main.py train --interactive'"
                    )
                    continue

                result = analyzer.analyze(text)
                print(f"Morphs: {format_result(result)}")

                syntax_result = syntax_analyzer.analyze(
                    text=text, morph_analyzer=analyzer
                )
                print("Syntax: ", end="")
                for word, pos, comp in syntax_result:
                    print(f"{word}({comp.value}) ", end="")
                print()

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def handle_train(args):
    print("Initializing MorphAnalyzer&SyntaxAnalyzer for training...")
    # Training always needs HMM
    analyzer = MorphAnalyzer(
        use_double_array=False,  # Must be False to allow insertion during training
        use_sejong=True,
        use_rust=getattr(args, "rust", False),
        debug=False,
    )
    syntax_analyzer = SyntaxAnalyzer()

    def train_file_conllu(filepath, analyzer, syntax_analyzer):
        """Train from a single CoNLL-U file or CoNLL-like txt file."""
        count = 0
        try:
            from .conllu import ConlluParser

            parser = ConlluParser()
            sentences = parser.parse(filepath)

            if not sentences:
                return 0

            print(f"  [v] Training from: {filepath} ({len(sentences)} sentences)")
            for sent in sentences:
                all_morphs = []
                valid_sentence = True

                for token in sent["tokens"]:
                    if not token["morphs"]:
                        valid_sentence = False
                        break
                    all_morphs.extend(token["morphs"])

                    # Syntax Training
                    pos_seq = "+".join(m[1] for m in token["morphs"])
                    deprel = token["deprel"]
                    syntax_analyzer.train_pattern(pos_seq, deprel)

                if valid_sentence:
                    # Neural Training (Sentence Level)
                    # analyzer.train is still needed if it updates Neural Model online?
                    # Current analyzer.train does: 1. Neural online train (if enabled), 2. Trie insert.
                    # We should keep calling train() for Neural, but use train_eojeol for Trie.

                    analyzer.train(sent["text"], all_morphs, save=False)

                    # Explicit Irregular Learning
                    for token in sent["tokens"]:
                        if token["morphs"]:
                            analyzer.train_eojeol(token["form"], token["morphs"])

                    count += 1
            return count
        except Exception as e:
            # Fallback to simple format if allowed, or just log error
            # Simple format logic was previously embedded.
            # Let's keep strict CoNLL check for now or basic fallback?
            # User request specifically mentioned "conllu", so we prioritize that.
            print(f"  [!] Failed to parse {filepath} as CoNLL-U: {e}")
            return 0

    def train_file_simple(filepath, analyzer):
        """Train from simple text file (Sent | Morph/Tag...)"""
        count = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.split("|")
                    if len(parts) == 2:
                        sent = parts[0].strip()
                        morphemes = parse_morphemes(parts[1].strip())
                        analyzer.train(sent, morphemes, save=False)
                        count += 1
            return count
        except Exception as e:
            print(f"  [!] Failed to parse {filepath} as Simple Text: {e}")
            return 0

    if args.corpus:
        target_files = []
        if os.path.isdir(args.corpus):
            print(f"Scanning directory: {args.corpus}")
            for root, dirs, files in os.walk(args.corpus):
                for file in files:
                    full_path = os.path.join(root, file)
                    if file.endswith(".conllu") or file.endswith(".txt"):
                        target_files.append(full_path)
            print(f"Found {len(target_files)} potential training files.")
        elif os.path.exists(args.corpus):
            target_files.append(args.corpus)
        else:
            print(f"Error: Path not found: {args.corpus}")
            sys.exit(1)

        total_sentences = 0
        for filepath in target_files:
            # Determine format
            # Heuristic: Try CoNLL-U first if .conllu or .txt
            # If Conllu parser returns 0 sentences or fails, maybe simple format?
            # For this task, let's assume .conllu is CoNLL-U, .txt could be either if user wants.
            # But the requirement is "conllu file in directory".

            is_conllu = filepath.endswith(".conllu")

            # If simple .txt, we might need a flag or heuristic.
            # Current `ConlluParser` is robust enough to return empty if strictly not matching?
            # Let's try Conllu training first.

            sents = train_file_conllu(filepath, analyzer, syntax_analyzer)
            if sents > 0:
                total_sentences += sents
            else:
                # If Conllu failed or 0, try simple format for .txt files
                if filepath.endswith(".txt"):
                    sents = train_file_simple(filepath, analyzer)
                    if sents > 0:
                        print(
                            f"  [v] Trained simple format: {filepath} ({sents} sentences)"
                        )
                        total_sentences += sents

        analyzer.save()
        syntax_analyzer.save_model()
        print(
            f"[v] Total Training Complete: {total_sentences} sentences from {len(target_files)} files."
        )
        print(f"[v] Syntax Patterns Learned: {len(syntax_analyzer.learned_patterns)}")

        # ---------------------------------------------------------
        # Neural Training
        # ---------------------------------------------------------
        if args.neural and args.corpus and not args.interactive:
            print("\n" + "=" * 60)
            print("  Neural Model Training")
            print("=" * 60)

            try:
                from .neural_trainer import NeuralTrainer

                # Determine Corpus Path for Neural Trainer
                # NeuralTrainer expects a single path or glob pattern.
                # If args.corpus is a directory, construct glob.
                neural_corpus = args.corpus
                if os.path.isdir(args.corpus):
                    neural_corpus = os.path.join(args.corpus, "*.conllu")
                    print(f"  Target Dir: {args.corpus} -> {neural_corpus}")

                trainer = NeuralTrainer(device=args.device)

                # 1. Morph Model
                print("\n[Stage 1] Training Morphological Model (Transformer)...")
                trainer.train_morph(
                    neural_corpus,
                    epochs=args.epochs,
                    batch_size=args.batch_size
                    * 2,  # Morph model usually handles larger batch
                    save_path=os.path.join(get_data_dir(), "neural_morph_model.pt"),
                )

                # 2. Syntax Model
                print("\n[Stage 2] Training Syntax Model (Transformer-Biaffine)...")
                trainer.train(
                    neural_corpus,
                    epochs=args.epochs,
                    batch_size=args.batch_size,
                    save_path=os.path.join(get_data_dir(), "neural_model.pt"),
                )

                print("\n[v] Neural Training Complete.")

            except Exception as e:
                print(f"\n[!] Neural Training Failed: {e}")
                import traceback

                traceback.print_exc()

    elif args.interactive:
        print("\nEntering interactive TRAINING mode.")
        print("Usage: [Sentence] | [Morph1/Tag + Morph2/Tag ...]")
        print("Type 'exit' to quit.")

        while True:
            try:
                text = input("\n(Train) >>> ")
                if text.strip().lower() in ["exit", "quit"]:
                    break
                if not text.strip():
                    continue

                parts = text.split("|")
                if len(parts) != 2:
                    print("Usage: [Sentence] | [Morph1/Tag + Morph2/Tag ...]")
                    continue

                sent_text = parts[0].strip()
                morph_str = parts[1].strip()

                try:
                    correct_morphemes = parse_morphemes(morph_str)
                    analyzer.train(sent_text, correct_morphemes, save=True)
                    print("✓ Learned and saved.")

                    # Verify
                    res = analyzer.analyze(sent_text)
                    print(f"Current Analysis: {format_result(res)}")

                except Exception as e:
                    print(f"Error: {e}")

            except KeyboardInterrupt:
                break


def handle_benchmark(args):
    run_benchmark(args)


def parse_morphemes(morph_str):
    correct_morphemes = []
    for token in morph_str.split("+"):
        token = token.strip()
        if "/" not in token:
            raise ValueError(f"Invalid token format: {token}")
        word, pos = token.rsplit("/", 1)
        correct_morphemes.append((word.strip(), pos.strip()))
    return correct_morphemes


def run_benchmark(args):
    import time

    print("=" * 60)
    print("  KULIM Performance Benchmark")
    print("=" * 60)

    # Benchmark scenarios
    scenarios = [
        ("Short Sentence (x1000)", "친구가 학교에 갔습니다." * 1000),
        (
            "Long Sentence (x100)",
            (
                "오랜만에 친구들이랑 만나서 맛있는 밥을 먹고 즐거운 시간을 보냈습니다. "
                "날씨도 좋고 바람도 시원해서 산책하기 딱 좋은 날이었습니다. "
            )
            * 100,
        ),
    ]

    # Configurations to test
    configs = [{"name": "Python", "use_rust": False}]

    # Check if Rust is available
    # Argument overrides auto-detect if provided?
    # Current behavior: Auto-add Rust if available.
    try:
        from .rust_ext import HAS_RUST

        if HAS_RUST:
            configs.append({"name": "Rust  ", "use_rust": True})
    except ImportError:
        pass

    for title, text in scenarios:
        print(f"\nScenario: {title}")
        print("-" * 60)

        for config in configs:
            try:
                # Initialize analyzer for this config
                analyzer = MorphAnalyzer(
                    use_double_array=True,
                    use_sejong=True,
                    use_rust=config["use_rust"],
                    use_gpu=False,  # GPU overhead might be too high for single sentence, keep CPU comparison for now
                    debug=False,
                )

                # Warmup
                analyzer.analyze("테스트입니다")

                # Measure
                start_time = time.time()
                result = analyzer.analyze(text)
                end_time = time.time()

                elapsed = end_time - start_time
                morphemes = len(result)

                print(
                    f"[{config['name']}] Time: {elapsed*1000:.2f} ms | Speed: {len(text)/elapsed/1000:.2f} kChars/sec | Morphemes: {morphemes}"
                )

            except Exception as e:
                print(f"[{config['name']}] Failed: {e}")


def format_result(result):
    if not result:
        return "(No result)"
    return " + ".join(f"{surf}/{pos}" for surf, pos in result)


if __name__ == "__main__":
    main()
