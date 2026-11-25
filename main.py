#!/usr/bin/env python3
"""Read a site's sitemap.xml and list all its URLs.

Handles plain sitemaps (<urlset>) and sitemap indexes
(<sitemapindex>), following nested sitemaps recursively.

Usage:
    python3 main.py https://example.com/sitemap.xml
    python3 main.py https://example.com/sitemap.xml --output urls.txt
    python3 main.py sitemap.xml --limit 20
"""
import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; sitemap-crawler/1.0)"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def local(tag):
    return tag.split("}")[-1]


def fetch(source, timeout, user_agent):
    if urllib.parse.urlparse(source).scheme in ("http", "https"):
        request = urllib.request.Request(
            source, headers={"User-Agent": user_agent})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            print(f"error: HTTP {exc.code} {exc.reason} for {source}",
                  file=sys.stderr)
            return None
        except urllib.error.URLError as exc:
            print(f"error: cannot reach {source}: {exc.reason}", file=sys.stderr)
            return None
        except TimeoutError:
            print(f"error: timed out after {timeout}s fetching {source}",
                  file=sys.stderr)
            return None
    try:
        with open(source, "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        print(f"error: file not found: {source}", file=sys.stderr)
        return None
    except OSError as exc:
        print(f"error: cannot read {source}: {exc}", file=sys.stderr)
        return None


def crawl(source, timeout, user_agent, depth, max_depth, seen):
    if source in seen:
        return []
    seen.add(source)
    data = fetch(source, timeout, user_agent)
    if data is None:
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        print(f"error: cannot parse sitemap XML from {source}: {exc}",
              file=sys.stderr)
        return []

    urls = []
    if local(root.tag) == "sitemapindex":
        if depth >= max_depth:
            print(f"warning: max sitemap depth ({max_depth}) reached at {source}",
                  file=sys.stderr)
            return []
        for sitemap in root.findall(f"{{{SITEMAP_NS}}}sitemap"):
            loc = sitemap.find(f"{{{SITEMAP_NS}}}loc")
            if loc is not None and loc.text:
                child = loc.text.strip()
                urls.extend(crawl(child, timeout, user_agent,
                                  depth + 1, max_depth, seen))
    elif local(root.tag) == "urlset":
        for entry in root.findall(f"{{{SITEMAP_NS}}}url"):
            loc = entry.find(f"{{{SITEMAP_NS}}}loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
    else:
        print(f"error: unrecognised sitemap format in {source} "
              f"(root element: {local(root.tag)})", file=sys.stderr)
    return urls


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read a site's sitemap.xml and list all its URLs.")
    parser.add_argument("source", help="sitemap URL or local XML file")
    parser.add_argument("--output", "-o", help="write URLs to a file (one per line)")
    parser.add_argument("--timeout", type=float, default=30,
                        help="request timeout in seconds (default: 30)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT,
                        help="User-Agent header to send")
    parser.add_argument("--limit", type=int, default=0,
                        help="maximum URLs to list (0 = no limit)")
    parser.add_argument("--max-depth", type=int, default=5,
                        help="max recursion depth for sitemap indexes (default: 5)")
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    if args.limit < 0:
        parser.error("--limit must be 0 or more")

    urls = crawl(args.source, args.timeout, args.user_agent,
                 0, args.max_depth, set())
    total = len(urls)
    shown = urls[:args.limit] if args.limit else urls

    for url in shown:
        print(url)
    print(f"Found {total} URL(s)" + (f", showing {len(shown)}" if args.limit else ""),
          file=sys.stderr)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write("\n".join(urls) + ("\n" if urls else ""))
        except OSError as exc:
            print(f"error: cannot write {args.output}: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {total} URL(s) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
