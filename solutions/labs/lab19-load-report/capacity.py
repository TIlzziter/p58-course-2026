"""Прикидка мощности (задача 4)."""
import math


def concurrency(rps: float, latency_ms: float) -> float:
    """Закон Литтла: одновременно в системе L = λ · W запросов (W в секундах). 2 знака."""
    return round(rps * latency_ms / 1000, 2)


def max_rps(workers: int, latency_ms: float) -> float:
    """Предел пропускной способности: каждый воркер обрабатывает 1000 / latency_ms запросов в секунду. 1 знак."""
    if latency_ms <= 0:
        raise ValueError("latency_ms > 0")
    return round(workers * 1000 / latency_ms, 1)


def replicas_needed(target_rps: float, per_replica_rps: float, headroom: float = 0.3) -> int:
    """Сколько реплик нужно, чтобы каждая была загружена не больше чем на (1 − headroom). Минимум 1."""
    if per_replica_rps <= 0 or not 0 <= headroom < 1:
        raise ValueError("параметры")
    return max(1, math.ceil(target_rps / (per_replica_rps * (1 - headroom)) - 1e-9))


def utilization(rps: float, workers: int, latency_ms: float) -> float:
    """Загрузка ρ = rps / max_rps (3 знака). ρ ≥ 1 — очередь растёт без предела."""
    return round(rps / (workers * 1000 / latency_ms), 3)
