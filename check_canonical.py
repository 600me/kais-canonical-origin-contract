#!/usr/bin/env python3
"""Check a local HTML canonical against an explicit origin; no network I/O."""
import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

MAX_BYTES = 2 * 1024 * 1024


def origin(url, contract=False):
    if not isinstance(url, str) or not url or any(c.isspace() or ord(c) < 32 for c in url) or '\\' in url:
        raise ValueError('URL must be a nonempty HTTP(S) URL without whitespace or backslashes')
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise ValueError('URL must have an HTTP(S) origin, without credentials or fragment')
    if contract and (parsed.path not in ('', '/') or parsed.query):
        raise ValueError('Expected origin must not include a path or query')
    host = parsed.hostname.encode('idna').decode('ascii').lower()
    port = parsed.port if parsed.port is not None else (443 if parsed.scheme.lower() == 'https' else 80)
    return parsed.scheme.lower(), host, port


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.canonicals = []
        self.bases = []
        self.invalid_attributes = False
    def handle_starttag(self, tag, attrs):
        if tag == 'head': self.in_head = True
        if tag == 'body': self.in_head = False
        if not self.in_head: return
        values = dict(attrs)
        if tag in ('link', 'base'):
            names = [x[0] for x in attrs]
            if names.count('href') > 1 or names.count('rel') > 1: self.invalid_attributes = True
        if tag == 'base' and 'href' in values: self.bases.append(values['href'])
        if tag == 'link' and 'canonical' in (values.get('rel') or '').lower().split():
            self.canonicals.append(values.get('href'))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_endtag(self, tag):
        if tag == 'head': self.in_head = False


def evaluate(html, page_url, expected_origin):
    try:
        expected = origin(expected_origin, contract=True)
        origin(page_url)
        if not html or len(html.encode('utf-8')) > MAX_BYTES:
            raise ValueError('HTML must be nonempty and at most 2 MiB')
        parser = Head()
        parser.feed(html)
        parser.close()
        if parser.invalid_attributes or len(parser.bases) > 1:
            raise ValueError('Ambiguous href/rel attributes or multiple base URLs')
        if len(parser.canonicals) != 1:
            raise ValueError('Exactly one canonical link in head is required')
        raw = parser.canonicals[0]
        if not raw or not raw.strip(): raise ValueError('Canonical href must be nonempty')
        base = page_url
        if parser.bases:
            if not parser.bases[0]: raise ValueError('Base href must be nonempty')
            base = urljoin(page_url, parser.bases[0])
            origin(base)
        target = urljoin(base, raw)
        if origin(target) != expected:
            return {'passed': False, 'code': 'ORIGIN_MISMATCH'}
        return {'passed': True, 'code': 'ORIGIN_MATCH'}
    except (ValueError, UnicodeError, TypeError):
        return {'passed': False, 'code': 'INVALID_OR_INCOMPLETE_CONTRACT'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html-file', required=True)
    parser.add_argument('--page-url', required=True)
    parser.add_argument('--expected-origin', required=True)
    args = parser.parse_args()
    try:
        with Path(args.html_file).open('rb') as stream: raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES: raise ValueError('Too large')
        result = evaluate(raw.decode('utf-8-sig'), args.page_url, args.expected_origin)
    except (OSError, UnicodeError, ValueError):
        result = {'passed': False, 'code': 'UNREADABLE_HTML'}
    print(json.dumps(result))
    return 0 if result['passed'] else 1

if __name__ == '__main__': sys.exit(main())
