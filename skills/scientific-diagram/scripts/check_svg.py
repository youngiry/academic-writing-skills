#!/usr/bin/env python3
"""Inspect a self-contained SVG. Exit 0 clean static check, 1 findings, 2 input error.

This checks syntax, references and declared labels/relations, not visual truth.
"""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def inspect(path, grayscale=False, spec=None):
    raw = path.read_text(encoding='utf-8-sig')
    if re.search(r'<!DOCTYPE|<!ENTITY', raw, re.I):
        raise ValueError('DTD/entity declarations are outside the supported SVG subset')
    root = ET.fromstring(raw)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Expected an SVG root with the SVG namespace')
    findings, ids = [], {}
    for node in root.iter():
        name = node.tag.rsplit('}', 1)[-1]
        nid = node.get('id')
        if nid:
            if nid in ids:
                findings.append('duplicate id: ' + nid)
            ids[nid] = node
        if name in {'script', 'foreignObject', 'metadata', 'image', 'style', 'animate', 'set'}:
            findings.append('element requires removal or separate review: ' + name)
        for key, value in node.attrib.items():
            local = key.rsplit('}', 1)[-1]
            if local.lower().startswith('on'):
                findings.append('event handler present')
            if local in {'href', 'src'} and not value.startswith('#'):
                findings.append('external or embedded resource present')
            if re.search(r'url\(\s*(?!#)[^)]', value):
                findings.append('non-fragment URL requires review')
            if local in {'display', 'visibility', 'opacity'} and value in {'none','hidden','0'}:
                findings.append('hidden element requires review')
            if grayscale:
                colors = []
                if local in {'fill','stroke','color','stop-color'}:
                    colors.append(value)
                if local == 'style':
                    colors += re.findall(r'(?:fill|stroke|color|stop-color)\s*:\s*([^;]+)', value)
                for color in colors:
                    color = color.strip()
                    if color in {'none','black','white','transparent'} or color.startswith('url(#'):
                        continue
                    if not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', color):
                        findings.append('unsupported color syntax, inspect manually: ' + color)
                        continue
                    digits = color[1:]
                    if len(digits) == 3:
                        digits = ''.join(c*2 for c in digits)
                    channels = [int(digits[i:i+2],16) for i in (0,2,4)]
                    if max(channels) - min(channels) > 6:
                        findings.append('non-grayscale color: ' + color)
    for node in root.iter():
        for key, value in node.attrib.items():
            refs = re.findall(r'url\(#([^)]+)\)',value)
            if key.rsplit('}',1)[-1] == 'href' and value.startswith('#'):
                refs.append(value[1:])
            for target in refs:
                if target not in ids:
                    findings.append('missing fragment target: ' + target)
    if spec is not None:
        labels = {n.get('id'): ''.join(n.itertext()).strip() for n in root.iter()
                  if n.tag.rsplit('}',1)[-1] == 'text'}
        if labels != spec['labels']:
            findings.append('visible text labels differ from the supplied specification')
        edges = {nid:[n.get('data-source'),n.get('data-target')] for nid,n in ids.items()
                 if n.get('data-source') is not None or n.get('data-target') is not None}
        if edges != spec['edges']:
            findings.append('declared edge endpoints differ from the supplied specification')
        for pair in edges.values():
            if any(x not in ids for x in pair):
                findings.append('declared edge endpoint id is missing')
    return {'findings':list(dict.fromkeys(findings)),
            'limits':'Geometry, clipping, actual arrow direction, source accuracy and all metadata channels require visual/manual review.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg',type=Path)
    parser.add_argument('--grayscale',action='store_true')
    parser.add_argument('--spec',type=Path)
    args=parser.parse_args()
    try:
        spec=json.loads(args.spec.read_text(encoding='utf-8')) if args.spec else None
        if spec is not None and (not isinstance(spec,dict) or not isinstance(spec.get('labels'),dict)
                                 or not isinstance(spec.get('edges'),dict)):
            raise ValueError('Specification requires labels and edges objects')
        result=inspect(args.svg,args.grayscale,spec)
    except (OSError,ValueError,ET.ParseError) as error:
        parser.exit(2,f'Input error: {error}\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['findings'] else 0)


if __name__=='__main__':
    main()
