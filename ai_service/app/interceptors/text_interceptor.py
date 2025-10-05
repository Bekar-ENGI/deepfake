# ================== advanced_text_interceptor.py ==================
# Pure-Python heuristic detector tuned to catch GPT-4 / Gemini / Meta-like outputs
# No external pip installs. Uses stylometric and structural heuristics + prototype matching.

import re
import math
from collections import Counter, defaultdict


# ------------------- Utility helpers -------------------

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_sentences(text: str):
    # naive sentence splitter
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


# ------------------- Low-level metrics -------------------

def tokens(text: str):
    # simple tokenization: words and punctuation
    return re.findall(r"\w+|[.,;:()—%-]", text)


def words(text: str):
    return [w for w in re.findall(r"[A-Za-z']+", text)]


def avg_sentence_length(sentences):
    lens = [len(s.split()) for s in sentences]
    if not lens:
        return 0.0
    return sum(lens) / len(lens)


def sentence_length_std(sentences):
    lens = [len(s.split()) for s in sentences]
    if len(lens) < 2:
        return 0.0
    mean = sum(lens) / len(lens)
    var = sum((l - mean) ** 2 for l in lens) / len(lens)
    return math.sqrt(var)


def burstiness(sentences):
    mean = avg_sentence_length(sentences)
    if mean == 0:
        return 0.0
    var = sentence_length_std(sentences) ** 2
    return var / mean


def type_token_ratio(ws):
    return len(set(ws)) / max(1, len(ws))


def hapax_legomena_ratio(ws):
    freq = Counter(ws)
    hapax = sum(1 for _, c in freq.items() if c == 1)
    return hapax / max(1, len(ws))


def zipf_deviation(ws):
    freq = Counter(ws)
    if not freq:
        return 0.0
    freqs = sorted(freq.values(), reverse=True)
    expected = [freqs[0] / (i + 1) for i in range(len(freqs))]
    deviation = sum(abs(a - e) for a, e in zip(freqs, expected)) / len(expected)
    return deviation / max(1, len(ws))


def entropy_score(ws):
    freq = Counter(ws)
    total = sum(freq.values())
    if total == 0:
        return 0.0
    probs = [f / total for f in freq.values()]
    return -sum(p * math.log2(p) for p in probs)


def repetition_score(ws, n=3):
    if len(ws) < n:
        return 0.0
    ngrams = [' '.join(ws[i:i + n]) for i in range(len(ws) - n + 1)]
    freq = Counter(ngrams)
    most = freq.most_common(1)
    if not most:
        return 0.0
    return most[0][1] / len(ngrams)


# ------------------- Structural & stylistic checks -------------------

def contraction_ratio(text: str):
    cont = re.findall(
        r"\b(?:I'm|don't|didn't|can't|won't|isn't|it's|that's|there's|we're|we'll|you're|you've|they're)\b",
        text, flags=re.I
    )
    ws = len(re.findall(r"[A-Za-z']+", text))
    return len(cont) / max(1, ws)


def enumerated_list_density(text: str):
    lines = text.splitlines()
    hits = 0
    for l in lines:
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", l):
            hits += 1
    return hits / max(1, len(lines))


def transition_density(text: str, sentences):
    transitions = ['moreover', 'furthermore', 'however', 'thus', 'therefore',
                   'additionally', 'in conclusion', 'on the other hand', 'nevertheless']
    hits = sum(text.lower().count(t) for t in transitions)
    return hits / max(1, len(sentences))


def hedging_phrases(text: str):
    hedges = ['it is possible that', 'it could be argued', 'may suggest',
              'might indicate', 'it seems that', 'appears to be', 'as far as we can tell']
    return sum(text.lower().count(h) for h in hedges)


def numeric_density(text: str):
    nums = re.findall(r"\b\d+\b", text)
    ws = len(re.findall(r"[A-Za-z']+", text))
    return len(nums) / max(1, ws)


def parenthetical_density(text: str):
    return text.count('(') + text.count(')')


def punctuation_diversity(text: str):
    puncts = [';', ':', '—', '(', ')', '...']
    return sum(text.count(p) for p in puncts)


def sensory_language(text: str):
    sensory = ['feel', 'see', 'hear', 'taste', 'touch', 'smell', 'remember', 'experience']
    return sum(text.lower().count(s) for s in sensory)


def real_world_anchors(text: str):
    date_patterns = r"\b(19|20)\d{2}\b"
    pronouns = [' i ', ' we ', ' my ', ' our ', ' me ', ' us ']  # crude check
    hits = sum(text.lower().count(p) for p in pronouns)
    dates = len(re.findall(date_patterns, text))
    return hits + dates


# ------------------- Prototype signatures (heuristic) -------------------

_PROTOTYPES = {
    'gpt4': {
        'avg_sent_len': 18.0, 'sentence_std': 8.0, 'burstiness': 3.0,
        'zipf_dev': 0.02, 'entropy': 4.0, 'repetition': 0.02,
        'contraction': 0.02, 'function_word_ratio': 0.38,
        'transition_density': 0.12, 'enumerated_density': 0.06,
        'numeric_density': 0.03, 'sensory': 1.0,
    },
    'gemini': {
        'avg_sent_len': 14.0, 'sentence_std': 6.0, 'burstiness': 2.5,
        'zipf_dev': 0.018, 'entropy': 4.2, 'repetition': 0.02,
        'contraction': 0.015, 'function_word_ratio': 0.35,
        'transition_density': 0.08, 'enumerated_density': 0.08,
        'numeric_density': 0.06, 'sensory': 0.8,
    },
    'meta_llama': {
        'avg_sent_len': 16.0, 'sentence_std': 7.0, 'burstiness': 2.8,
        'zipf_dev': 0.025, 'entropy': 3.9, 'repetition': 0.03,
        'contraction': 0.03, 'function_word_ratio': 0.40,
        'transition_density': 0.10, 'enumerated_density': 0.05,
        'numeric_density': 0.035, 'sensory': 0.9,
    }
}


# ------------------- Scoring utilities -------------------

def scalar_similarity(x, proto, weight=1.0):
    if proto == 0:
        return 1.0 if x == 0 else 0.0
    diff = abs(x - proto) / (abs(proto) + 1e-9)
    sim = math.exp(-3.0 * diff)  # exponential decay
    return sim * weight


# ------------------- Main detector -------------------

def analyze_text(text: str):
    t = normalize(text)
    sents = split_sentences(t)
    ws = [w.lower() for w in words(t)]

    metrics = {}
    metrics['avg_sent_len'] = avg_sentence_length(sents)
    metrics['sentence_std'] = sentence_length_std(sents)
    metrics['burstiness'] = burstiness(sents)
    metrics['type_token_ratio'] = type_token_ratio(ws)
    metrics['hapax_ratio'] = hapax_legomena_ratio(ws)
    metrics['zipf_dev'] = zipf_deviation(ws)
    metrics['entropy'] = entropy_score(ws)
    metrics['repetition'] = repetition_score(ws)
    metrics['contraction'] = contraction_ratio(t)
    metrics['enumerated_density'] = enumerated_list_density(t)
    metrics['transition_density'] = transition_density(t, sents)
    metrics['hedging'] = hedging_phrases(t)
    metrics['numeric_density'] = numeric_density(t)
    metrics['punctuation_diversity'] = punctuation_diversity(t)
    metrics['parenthetical'] = parenthetical_density(t)
    metrics['sensory'] = sensory_language(t)
    metrics['real_world_anchors'] = real_world_anchors(t)

    func_words = set(["the", "and", "but", "if", "or", "as", "because", "that", "which",
                      "of", "at", "by", "for", "with", "about", "into", "to"])
    metrics['function_word_ratio'] = sum(1 for w in ws if w in func_words) / max(1, len(ws))

    # AI-likeness scoring
    ai_like_score = 0.0
    ai_weights = {
        'zipf_dev': 0.12, 'repetition': 0.12, 'entropy': 0.12,
        'burstiness': 0.12, 'hapax_ratio': 0.08, 'contraction': 0.08,
        'function_word_ratio': 0.08, 'transition_density': 0.06,
        'enumerated_density': 0.06, 'numeric_density': 0.06
    }

    sub = {}
    sub['zipf_dev'] = min(1.0, metrics['zipf_dev'] / 0.05)
    sub['repetition'] = min(1.0, metrics['repetition'] / 0.12)
    sub['entropy'] = 1.0 - min(1.0, metrics['entropy'] / 5.0)
    sub['burstiness'] = 1.0 - min(1.0, metrics['burstiness'] / 3.0)
    sub['hapax_ratio'] = 1.0 - min(1.0, metrics['hapax_ratio'] / 0.15)
    sub['contraction'] = 1.0 - min(1.0, metrics['contraction'] / 0.05)

    fwr = metrics['function_word_ratio']
    sub['function_word_ratio'] = max(0.0, 1.0 - abs(fwr - 0.38) / 0.3)
    sub['transition_density'] = min(1.0, metrics['transition_density'] / 0.3)
    sub['enumerated_density'] = min(1.0, metrics['enumerated_density'] / 0.2)
    sub['numeric_density'] = min(1.0, metrics['numeric_density'] / 0.1)

    for k, w in ai_weights.items():
        ai_like_score += sub.get(k, 0.0) * w

    ai_like_score = ai_like_score / sum(ai_weights.values())

    # Model-specific similarity
    model_scores = {}
    for model, proto in _PROTOTYPES.items():
        sims = []
        sims.append(scalar_similarity(metrics['avg_sent_len'], proto['avg_sent_len']))
        sims.append(scalar_similarity(metrics['sentence_std'], proto['sentence_std']))
        sims.append(scalar_similarity(metrics['burstiness'], proto['burstiness']))
        sims.append(scalar_similarity(metrics['zipf_dev'], proto['zipf_dev']))
        sims.append(scalar_similarity(metrics['entropy'], proto['entropy']))
        sims.append(scalar_similarity(metrics['repetition'], proto['repetition']))
        sims.append(scalar_similarity(metrics['contraction'], proto['contraction']))
        sims.append(scalar_similarity(metrics['function_word_ratio'], proto['function_word_ratio']))
        sims.append(scalar_similarity(metrics['transition_density'], proto['transition_density']))
        sims.append(scalar_similarity(metrics['enumerated_density'], proto['enumerated_density']))
        sims.append(scalar_similarity(metrics['numeric_density'], proto['numeric_density']))
        sims.append(scalar_similarity(metrics['sensory'], proto['sensory']))
        model_scores[model] = sum(sims) / len(sims)

    raw = {m: model_scores[m] * ai_like_score for m in model_scores}
    total = sum(raw.values())
    normalized = {m: 0.0 for m in raw} if total <= 0 else {m: round(raw[m] / total, 3) for m in raw}

    top_model = max(normalized.items(), key=lambda x: x[1]) if total > 0 else (None, 0.0)
    verdict = 'Likely human-written'
    if ai_like_score > 0.55:
        verdict = f'Likely AI-generated (model-leaning: {top_model[0] if top_model[0] else "unknown"})'
    elif 0.35 < ai_like_score <= 0.55:
        verdict = 'Uncertain / Mixed (weak AI signals)'

    result = {
        'ai_like_score': round(ai_like_score, 3),
        'model_likelihoods': normalized,
        'metrics': metrics,
        'subscores': sub
    }

    return result


