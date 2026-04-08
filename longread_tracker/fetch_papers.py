#!/usr/bin/env python3
"""
Fetch new long-read transcriptomics papers from bioRxiv, PubMed, and arXiv.
Downloads PDFs and returns metadata for papers not yet in the index.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

TRACKER_DIR = Path(__file__).parent
INDEX_FILE = TRACKER_DIR / "index.json"
PDF_DIR = TRACKER_DIR / "pdfs"
PDF_DIR.mkdir(exist_ok=True)

# Long-read technology terms (at least one required)
TECH_TERMS = [
    "long-read", "long read", "nanopore", "pacbio", "isoseq", "iso-seq",
    "oxford nanopore", " ont ", "smrt sequencing", "minion", "promethion",
]
# Transcriptomics focus terms (at least one required)
TOPIC_TERMS = [
    "transcript", "rna", "mrna", "isoform", "splicing", "splice",
    "gene expression", "cdna", "polyadenyl", "rnaseq", "rna-seq",
]

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            return json.load(f)
    return {"read_papers": [], "last_run": None, "total_processed": 0}

def is_relevant(title, abstract):
    combined = (title + " " + abstract).lower()
    has_tech = any(t in combined for t in TECH_TERMS)
    has_topic = any(t in combined for t in TOPIC_TERMS)
    return has_tech and has_topic

def fetch_biorxiv(days_back=2):
    """Query bioRxiv general endpoint with pagination and client-side keyword filtering."""
    papers = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    cursor = 0
    pages_fetched = 0
    MAX_PAGES = 20  # safety cap

    while pages_fetched < MAX_PAGES:
        url = f"https://api.biorxiv.org/details/biorxiv/{start_str}/{end_str}/{cursor}/json"
        try:
            print(f"  bioRxiv cursor={cursor}...", file=sys.stderr)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            collection = data.get("collection", [])
            messages = data.get("messages", [{}])[0]
            total = int(messages.get("total", 0))

            for paper in collection:
                title = paper.get("title", "")
                abstract = paper.get("abstract", "")
                if is_relevant(title, abstract):
                    doi = paper.get("doi", "")
                    version = paper.get("version", 1)
                    papers.append({
                        "id": doi,
                        "source": "biorxiv",
                        "title": title,
                        "authors": paper.get("authors", ""),
                        "abstract": abstract,
                        "date": paper.get("date", ""),
                        "doi": doi,
                        "pdf_url": f"https://www.biorxiv.org/content/{doi}v{version}.full.pdf",
                    })

            cursor += len(collection)
            pages_fetched += 1

            if cursor >= total or len(collection) == 0:
                print(f"  bioRxiv done: scanned {cursor}/{total} papers", file=sys.stderr)
                break
            time.sleep(1)

        except Exception as e:
            print(f"  bioRxiv error at cursor={cursor}: {e}", file=sys.stderr)
            break

    print(f"  bioRxiv matches: {len(papers)}", file=sys.stderr)
    return papers

def fetch_pubmed(days_back=2):
    """Query PubMed with targeted search."""
    papers = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    query = (
        '("long-read"[Title/Abstract] OR "nanopore"[Title/Abstract] OR '
        '"PacBio"[Title/Abstract] OR "Oxford Nanopore"[Title/Abstract] OR '
        '"IsoSeq"[Title/Abstract] OR "SMRT sequencing"[Title/Abstract]) '
        'AND ("transcriptom*"[Title/Abstract] OR "RNA isoform"[Title/Abstract] OR '
        '"mRNA isoform"[Title/Abstract] OR "splice variant"[Title/Abstract] OR '
        '"full-length transcript"[Title/Abstract])'
    )
    date_filter = f'{start_date.strftime("%Y/%m/%d")}:{end_date.strftime("%Y/%m/%d")}[pdat]'
    full_query = f"{query} AND {date_filter}"

    encoded = urllib.parse.quote(full_query)
    search_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={encoded}&retmax=20&retmode=json"
    )

    try:
        print(f"  Querying PubMed...", file=sys.stderr)
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            search_data = json.loads(resp.read().decode())

        ids = search_data.get("esearchresult", {}).get("idlist", [])
        print(f"  PubMed: {len(ids)} results", file=sys.stderr)

        if not ids:
            return papers

        ids_str = ",".join(ids)
        fetch_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={ids_str}&retmode=xml"
        )
        req = urllib.request.Request(fetch_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_content = resp.read().decode()

        root = ET.fromstring(xml_content)
        for article in root.findall(".//PubmedArticle"):
            pmid_el = article.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""

            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""

            abstract_parts = article.findall(".//AbstractText")
            abstract = " ".join((el.text or "") for el in abstract_parts if el.text)

            authors_list = []
            for author in article.findall(".//Author"):
                last = author.find("LastName")
                fore = author.find("ForeName")
                if last is not None:
                    name = last.text
                    if fore is not None:
                        name += f", {fore.text}"
                    authors_list.append(name)

            pub_date = article.find(".//PubDate")
            date_str = ""
            if pub_date is not None:
                year = pub_date.find("Year")
                month = pub_date.find("Month")
                date_str = f"{year.text if year is not None else ''}-{month.text if month is not None else ''}"

            doi = ""
            pmc = ""
            for id_el in article.findall(".//ArticleId"):
                if id_el.get("IdType") == "doi":
                    doi = id_el.text
                if id_el.get("IdType") == "pmc":
                    pmc = id_el.text

            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/pdf/" if pmc else ""

            papers.append({
                "id": f"PMID:{pmid}",
                "source": "pubmed",
                "title": title,
                "authors": "; ".join(authors_list[:5]),
                "abstract": abstract,
                "date": date_str,
                "doi": doi,
                "pdf_url": pdf_url,
                "pmc": pmc,
            })

    except Exception as e:
        print(f"  PubMed error: {e}", file=sys.stderr)

    return papers

def fetch_arxiv(max_results=30, days_back=14):
    """Query arXiv for long-read transcriptomics papers, with recent date filter."""
    papers = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    # arXiv date format: YYYYMMDDHHMMSS
    start_str = start_date.strftime("%Y%m%d") + "000000"
    end_str = end_date.strftime("%Y%m%d") + "235959"

    query = urllib.parse.quote(
        f'(ti:"long-read" OR ti:"nanopore" OR ti:"PacBio" OR abs:"long-read sequencing" OR abs:"Oxford Nanopore") '
        f'AND (ti:"transcriptom" OR abs:"RNA isoform" OR abs:"full-length transcript" OR abs:"mRNA isoform") '
        f'AND submittedDate:[{start_str} TO {end_str}]'
    )
    url = (
        f"https://export.arxiv.org/api/query?search_query={query}"
        f"&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )

    try:
        print(f"  Querying arXiv...", file=sys.stderr)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode()

        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        print(f"  arXiv: {len(entries)} results", file=sys.stderr)

        for entry in entries:
            arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            abstract = entry.find("atom:summary", ns).text.strip()
            published = entry.find("atom:published", ns).text[:10]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

            if is_relevant(title, abstract):
                papers.append({
                    "id": f"arxiv:{arxiv_id}",
                    "source": "arxiv",
                    "title": title,
                    "authors": "; ".join(authors[:5]),
                    "abstract": abstract,
                    "date": published,
                    "doi": f"arxiv:{arxiv_id}",
                    "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                })
    except Exception as e:
        print(f"  arXiv error: {e}", file=sys.stderr)

    return papers

def download_pdf(paper):
    """Download PDF. Returns local path or None."""
    if not paper.get("pdf_url"):
        return None

    safe_id = paper["id"].replace("/", "_").replace(":", "_")
    pdf_path = PDF_DIR / f"{safe_id}.pdf"

    if pdf_path.exists() and pdf_path.stat().st_size > 5000:
        print(f"  Cached: {pdf_path.name}", file=sys.stderr)
        return str(pdf_path)

    try:
        print(f"  Downloading: {paper['title'][:55]}...", file=sys.stderr)
        req = urllib.request.Request(
            paper["pdf_url"],
            headers={"User-Agent": "Mozilla/5.0 (research use)", "Accept": "application/pdf"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()

        if len(content) < 5000:
            print(f"    Too small ({len(content)} bytes), skipping", file=sys.stderr)
            return None

        with open(pdf_path, "wb") as f:
            f.write(content)

        print(f"    Saved {pdf_path.name} ({len(content)//1024}KB)", file=sys.stderr)
        time.sleep(3)
        return str(pdf_path)
    except Exception as e:
        print(f"    PDF failed: {e}", file=sys.stderr)
        return None

def main():
    index = load_index()
    read_ids = set(index.get("read_papers", []))

    print("=== Long-Read Transcriptomics Paper Fetcher ===", file=sys.stderr)

    biorxiv_papers = fetch_biorxiv(days_back=2)
    time.sleep(1)
    pubmed_papers = fetch_pubmed(days_back=2)
    time.sleep(1)
    arxiv_papers = fetch_arxiv()

    all_papers = biorxiv_papers + pubmed_papers + arxiv_papers

    # Deduplicate
    seen_ids = set()
    unique_papers = []
    for p in all_papers:
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"])
            unique_papers.append(p)

    new_papers = [p for p in unique_papers if p["id"] not in read_ids]

    print(f"\nTotal matches: {len(unique_papers)} | Unread: {len(new_papers)}", file=sys.stderr)

    if not new_papers:
        print(json.dumps({"papers": [], "total_new": 0, "message": "No new papers found today"}))
        return

    papers_to_process = new_papers[:5]

    print(f"\nDownloading PDFs for {len(papers_to_process)} papers...", file=sys.stderr)
    for paper in papers_to_process:
        paper["local_pdf"] = download_pdf(paper)

    result = {
        "papers": papers_to_process,
        "total_new": len(new_papers),
        "remaining_unread": len(new_papers) - len(papers_to_process),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
