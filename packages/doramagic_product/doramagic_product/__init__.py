"""Doramagic product pipeline."""


def __getattr__(name: str):
    """Lazy import to avoid loading pipeline.py (heavy deps) at package init."""
    if name in ("CandidateInfo", "DoramagicProductPipeline", "DoramagicRunResult"):
        from .pipeline import CandidateInfo, DoramagicProductPipeline, DoramagicRunResult

        _exports = {
            "CandidateInfo": CandidateInfo,
            "DoramagicProductPipeline": DoramagicProductPipeline,
            "DoramagicRunResult": DoramagicRunResult,
        }
        return _exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["CandidateInfo", "DoramagicProductPipeline", "DoramagicRunResult"]
