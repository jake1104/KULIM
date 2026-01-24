import os
import sys
from importlib.metadata import version, PackageNotFoundError


def get_data_dir() -> str:
    """
    데이터 디렉토리 경로를 반환합니다.

    우선순위:
    1. KULIM_DATA_DIR 환경 변수
    2. 패키지 내부 'data' 디렉토리
    """
    # 1. 환경 변수
    if env_path := os.environ.get("KULIM_DATA_DIR"):
        return env_path

    # 2. 패키지 내부 data
    # __file__ is relative to this file (utils.py)
    # utils.py is in grammar/src/grammar/
    # data is in grammar/src/grammar/data/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    return data_dir


def get_version() -> str:
    """패키지 버전 반환"""
    try:
        return version("kulim")  # pyproject.toml name is "kulim"
    except PackageNotFoundError:
        # Fallback for local dev without install or if package name differs
        try:
            return version("grammar")
        except PackageNotFoundError:
            return "0.1.1"
