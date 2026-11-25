# Sitemap Crawler

Read a site's `sitemap.xml` and list all its URLs. Handles plain
sitemaps (`<urlset>`) and sitemap indexes (`<sitemapindex>`), following
nested sitemaps recursively.

## Requirements

- Python 3 (standard library only — no third-party packages)
- Internet access for sitemap URLs (a local XML file also works)

## Usage

```bash
python3 main.py https://example.com/sitemap.xml
python3 main.py https://example.com/sitemap.xml --output urls.txt
python3 main.py sitemap.xml --limit 20
```

## Options

| Option | Description |
| --- | --- |
| `--output`, `-o` | Write URLs to a file (one per line) |
| `--timeout` | Request timeout in seconds (default: `30`) |
| `--user-agent` | User-Agent header to send |
| `--limit` | Maximum URLs to list (`0` = no limit) |
| `--max-depth` | Max recursion depth for sitemap indexes (default: `5`) |

## Example

```bash
$ python3 main.py https://example.com/sitemap.xml
https://example.com/
https://example.com/about
https://example.com/blog
Found 3 URL(s)
```

## License

MIT — see `LICENSE`.
