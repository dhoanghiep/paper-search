import logging
from app.config import settings
from app.database import SessionLocal
from app.models import Paper
from app.repositories import PaperRepository, CategoryRepository

logger = logging.getLogger(__name__)

# Keywords for each category (case-insensitive, matched against title + abstract)
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "AI":             ["machine learning", "deep learning", "neural network", "transformer",
                       "large language model", "llm", "artificial intelligence", "reinforcement learning",
                       "convolutional", "attention mechanism"],
    "singlecell":     ["single-cell", "single cell", "scrna-seq", "scrna seq", "scatac",
                       "cell type", "cell cluster", "umap", "seurat", "scanpy"],
    "longread":       ["long-read", "long read", "nanopore", "pacbio", "ont sequencing",
                       "oxford nanopore", "third-generation sequencing", "hifi"],
    "methods":        ["novel method", "new method", "algorithm", "pipeline", "framework",
                       "tool", "software", "workflow", "approach", "we present", "we introduce",
                       "we develop"],
    "benchmark":      ["benchmark", "benchmarking", "comparison", "evaluation", "assess",
                       "performance comparison", "gold standard"],
    "dataset":        ["dataset", "database", "data resource", "data collection", "repository",
                       "atlas", "corpus", "we release", "publicly available"],
    "epigenetics":    ["epigenetic", "methylation", "histone", "chromatin", "chip-seq",
                       "atac-seq", "dnase", "acetylation", "h3k", "cpg"],
    "transcriptomics":["rna-seq", "rna seq", "transcriptom", "gene expression", "mrna",
                       "bulk rna", "differential expression", "deseq", "edger"],
    "genomics":       ["genome", "genomic", "whole genome", "wgs", "dna sequencing", "variant",
                       "snp", "mutation", "genotype", "gwas", "exome"],
    "microbial":      ["microbiome", "microbiota", "bacteria", "bacterial", "pathogen",
                       "virus", "viral", "fungal", "16s", "metagenom", "prokaryot"],
    "ecology":        ["ecology", "ecological", "biodiversity", "species", "ecosystem",
                       "population", "habitat", "phylogen", "evolution", "conservation"],
    "spatial":        ["spatial transcriptom", "spatial omics", "spatial genomics",
                       "visium", "slide-seq", "in situ", "tissue section", "spatial resolution"],
    "assembly":       ["genome assembly", "sequence assembly", "de novo assembly", "scaffold",
                       "contig", "n50", "chromosome assembly", "haplotype assembly"],
    "alignment":      ["read alignment", "sequence alignment", "read mapping", "aligner",
                       "bowtie", "bwa", "hisat", "star aligner", "minimap"],
    "isoforms":       ["isoform", "transcript isoform", "alternative transcript",
                       "full-length transcript", "long-read isoform", "isoseq"],
    "splicing":       ["splicing", "splice site", "spliceosome", "alternative splicing",
                       "exon skipping", "intron retention", "splice junction"],
    "cancer":         ["cancer", "tumor", "tumour", "oncol", "carcinoma", "malignant",
                       "metastasis", "oncogene", "somatic mutation", "tcga"],
    "immunology":     ["immune", "immunol", "t cell", "b cell", "antibody", "antigen",
                       "immunotherapy", "checkpoint", "cytokine", "nk cell", "macrophage"],
}


def _classify(title: str, abstract: str) -> list[str]:
    """Keyword-based classification — no API calls required."""
    text = (title + " " + abstract).lower()
    return [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in text for kw in kws)]


def process_paper(paper_id: int) -> dict:
    """Classify a single paper and set its summary from the abstract."""
    db = SessionLocal()
    try:
        paper_repo = PaperRepository(db)
        category_repo = CategoryRepository(db)
        paper = paper_repo.get_by_id(paper_id)
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")

        # Keyword classification
        abstract_text = paper.abstract or ""
        category_names = _classify(paper.title or "", abstract_text)
        for name in category_names:
            cat = category_repo.get_or_create(name)
            if cat not in paper.categories:
                paper.categories.append(cat)

        # Summary = abstract (or title fallback)
        if paper.abstract and len(paper.abstract.strip()) >= settings.MIN_ABSTRACT_LENGTH:
            paper.summary = paper.abstract
        else:
            paper.summary = f"Research paper: {paper.title}"

        paper_repo.update(paper)
        return {"paper_id": paper_id, "categories": category_names}
    finally:
        db.close()


def process_papers_batch(limit: int = 10) -> dict:
    """Process unprocessed papers in a batch."""
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(
            (Paper.summary == None) | (Paper.summary == "")
        ).limit(limit).all()
        ids = [p.id for p in papers]
    finally:
        db.close()

    results = {"processed": 0, "errors": 0}
    for paper_id in ids:
        try:
            process_paper(paper_id)
            results["processed"] += 1
        except Exception as e:
            logger.error(f"Error processing paper {paper_id}: {e}")
            results["errors"] += 1
    return results
