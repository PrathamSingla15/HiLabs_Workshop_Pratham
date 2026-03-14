"""Extract and calculate weighted scores from LLM logprobs."""
import math


def extract_weighted_score(response: dict) -> float:
    """
    Extract logprobs for score tokens 1-5, normalize, compute expected value.
    Falls back to parsing text output if logprobs unavailable.
    """
    try:
        top_logprobs = response["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    except (KeyError, IndexError, TypeError):
        # Fallback to text output
        return _fallback_parse(response)

    score_probs = {}
    for entry in top_logprobs:
        token = entry["token"].strip()
        if token in ("1", "2", "3", "4", "5"):
            prob = math.exp(entry["logprob"])
            score_probs[int(token)] = prob

    if not score_probs:
        return _fallback_parse(response)

    # Normalize probabilities
    total = sum(score_probs.values())
    weighted = sum(score * (prob / total) for score, prob in score_probs.items())
    return weighted


def get_top_logprob(response: dict) -> float:
    """Get the logprob of the most likely token (for early stopping)."""
    try:
        top_logprobs = response["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        return top_logprobs[0]["logprob"]
    except (KeyError, IndexError, TypeError):
        return -10.0  # Very low confidence


def _fallback_parse(response: dict) -> float:
    """Parse text output as score."""
    try:
        text = response["choices"][0]["message"]["content"].strip()
        if text and text[0] in "12345":
            return float(text[0])
    except (KeyError, IndexError, TypeError):
        pass
    return 3.0  # Neutral default


def average_pass_k_scores(scores: list) -> float:
    """Average scores from pass@k runs."""
    if not scores:
        return 3.0
    return sum(scores) / len(scores)
