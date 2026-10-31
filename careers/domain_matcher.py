"""
Score-based career domain matcher.

Iterates through CAREER_DOMAINS, counts keyword hits per entry,
respects exclusion rules, and returns the highest-scoring match.
"""

import re
from careers.domains import CAREER_DOMAINS


def get_domain_fallback(q_term):
    """Score-based career domain matcher. Iterates through CAREER_DOMAINS,
    counts keyword hits per entry, respects exclusion rules, and returns
    the highest-scoring match. Returns None if no domain matches."""
    q = q_term.lower()

    best_match = None
    best_score = 0

    for domain in CAREER_DOMAINS:
        score = 0
        excluded = False

        # Check global exclusions — if any exclude term is found, skip this domain
        for exc in domain.get('exclude', []):
            if exc in q:
                excluded = True
                break
        if excluded:
            continue

        # Score plain keyword hits (substring match)
        for kw in domain.get('keywords', []):
            if kw in q:
                score += domain.get('priority', 50)

        # Score conditional keywords (keyword present AND no exclusion terms present)
        for cond_kw, rules in domain.get('conditional_keywords', {}).items():
            if cond_kw in q:
                cond_excluded = any(exc in q for exc in rules.get('exclude', []))
                if not cond_excluded:
                    score += domain.get('priority', 50)

        # Score regex pattern hits
        for pattern in domain.get('regex_patterns', []):
            if re.search(pattern, q):
                score += domain.get('priority', 50)

        # Pick the domain with the highest total score
        if score > best_score:
            best_score = score
            best_match = domain.get('data')

    return best_match

