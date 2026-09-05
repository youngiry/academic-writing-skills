#!/usr/bin/env python3
"""MIT licensed Markdown review helper. Reports clues; never edits or grades a paper.

Exit 0: inspection ran, even if findings exist. Exit 2: input/usage failure.
The public implementation retains the original helper's inspection purposes,
without its private word lists, project-specific thresholds, or quality claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics
import sys
from urllib.parse import unquote, urlsplit


def mask(match):
    return ''.join('\n' if c == '\n' else ' ' for c in match.group())


def body_and_refs(text):
    text = re.sub(r'<!--.*?-->', mask, text, flags=re.S)
    text = re.sub(r'^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', mask, text, flags=re.S | re.M)
    text = re.sub(r'`[^`\n]*`', mask, text)
    heading = re.search(r'^\s*#{1,6}\s*(?:参考文献|references)\s*$', text, re.M | re.I)
    return (text[:heading.start()], text[heading.end():]) if heading else (text, None)


def citation_numbers(body):
    result = []
    # Deliberately bounded to common numeric brackets; Markdown links are ignored.
    pattern = r'\[(\d{1,5}(?:\s*[-–,，]\s*\d{1,5})*)\](?!\s*\()'
    for m in re.finditer(pattern, body):
        parts = re.split(r'[,，]', m.group(1))
        for part in parts:
            ends = re.split(r'[-–]', part)
            if len(ends) == 1:
                result.append(int(ends[0]))
            else:
                start, end = map(int, ends)
                if end < start or end - start > 1000:
                    raise ValueError('Invalid or excessive citation range')
                result.extend(range(start, end + 1))
    return result


def inspect(path, scope='excerpt', numbering='preserve', baseline=None, terms=None, hints=None):
    body, refs = body_and_refs(path.read_text(encoding='utf-8-sig'))
    findings = []

    def add(category, message, line=None):
        item = {'category': category, 'message': message}
        if line is not None:
            item['line'] = line
        findings.append(item)

    cites = citation_numbers(body)
    order = list(dict.fromkeys(cites))
    if numbering == 'sequential' and order != list(range(1, len(order) + 1)):
        add('citation-order', 'First appearances differ from the selected 1..N convention.')
    if baseline:
        old = citation_numbers(body_and_refs(baseline.read_text(encoding='utf-8-sig'))[0])
        if Counter(old) != Counter(cites):
            add('citation-change', f'Citation counts changed: before {dict(Counter(old))}, after {dict(Counter(cites))}.')
        if list(dict.fromkeys(old)) != order:
            add('citation-first-appearance', 'Citation first-appearance order changed from the baseline.')
    if refs is not None and scope == 'full':
        ref_list = [int(x) for x in re.findall(r'^\s*\[(\d+)\]', refs, re.M)]
        missing = sorted(set(cites) - set(ref_list))
        unused = sorted(set(ref_list) - set(cites))
        if missing:
            add('references', f'Cited numbers without bibliography entries: {missing}.')
        if unused:
            add('references', f'Bibliography entries not found in body citations: {unused}.')
        if len(ref_list) != len(set(ref_list)):
            add('references', 'Duplicate bibliography numbers; inspect the selected convention.')
    elif refs is None and scope == 'full' and cites:
        add('references', 'Numeric citations found; a supported References heading was not found.')

    for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', body):
        raw = m.group(1).strip().strip('<>')
        if re.search(r'\s+[\"\']', raw):
            add('image-path', 'Image title syntax requires manual path verification.')
            continue
        parsed = urlsplit(raw)
        if not parsed.scheme and not parsed.netloc:
            if not (path.parent / unquote(parsed.path)).is_file():
                add('image-path', 'Local image target is missing: ' + raw, body[:m.start()].count('\n')+1)

    if scope == 'full':
        caption = re.compile(r'^\s*(?:\*\*)?([图表])\s*(\d+)\s+[^\n]+$', re.M)
        caps = {(m[1], m[2]) for m in caption.finditer(body)}
        prose = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', caption.sub('', body))
        mentions = set(re.findall(r'([图表])\s*(\d+)', prose))
        for kind, number in sorted(mentions - caps):
            add('figure-table', f'Mentioned {kind}{number} has no supported caption line.')
        for kind, number in sorted(caps - mentions):
            add('figure-table', f'Caption {kind}{number} has no body mention.')

    tags = re.findall(r'\\tag\{([^}]+)\}', body)
    if len(tags) != len(set(tags)):
        add('equation', 'Duplicate explicit equation tags.')
    if body.count('$$') % 2:
        add('equation', 'Unpaired display-math delimiter; inspect source.')
    for group, variants in (terms or {}).items():
        if not isinstance(variants, list) or not variants or not all(isinstance(x, str) and x for x in variants):
            raise ValueError('Each terminology group must contain nonempty strings')
        pattern = '|'.join(re.escape(x) for x in sorted(set(variants), key=len, reverse=True))
        present = sorted(set(re.findall(pattern, body)))
        if len(present) > 1:
            add('terminology', f'{group}: multiple surface forms {present}; context decides whether they differ.')
    for word in hints or []:
        if not isinstance(word, str) or not word:
            raise ValueError('Style hints must be nonempty strings')
        for i, line in enumerate(body.splitlines(), 1):
            if word in line:
                add('style-hint', f'Configured expression found: {word}; inspect its actual function.', i)

    sentences = [re.sub(r'\s+', '', s) for s in re.split(r'[。；！？!?]', body)]
    lengths = [len(s) for s in sentences if re.search(r'[\u4e00-\u9fff]', s)]
    return {'status': 'inspection-completed', 'scope': scope, 'numbering': numbering,
            'findings': findings,
            'descriptive_only': {'numeric_citation_occurrences': len(cites),
                                 'approx_sentence_char_median': statistics.median(lengths) if lengths else None},
            'limits': 'No citation truth, causal validity, semantic equivalence, paper quality, or AI-origin assessment.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manuscript', type=Path)
    parser.add_argument('--scope', choices=['excerpt', 'full'], default='excerpt')
    parser.add_argument('--numbering', choices=['preserve', 'sequential'], default='preserve')
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--terms', type=Path)
    parser.add_argument('--hints', type=Path)
    args = parser.parse_args()
    try:
        terms = json.loads(args.terms.read_text(encoding='utf-8')) if args.terms else {}
        hints = json.loads(args.hints.read_text(encoding='utf-8')) if args.hints else []
        if not isinstance(terms, dict) or not isinstance(hints, list):
            raise ValueError('terms must be an object; hints must be a list')
        result = inspect(args.manuscript, args.scope, args.numbering, args.baseline, terms, hints)
    except (OSError, ValueError) as error:
        parser.exit(2, f'Input error: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
