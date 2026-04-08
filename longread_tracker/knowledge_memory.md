# Long-Read Transcriptomics Knowledge Base

*Auto-updated by daily paper tracker. Each run appends new insights.*

---

## Field Overview

Long-read transcriptomics uses sequencing technologies (PacBio, Oxford Nanopore) to sequence full-length RNA molecules, enabling:
- Discovery of novel isoforms and splice variants
- Detection of fusion transcripts
- Direct RNA modification detection
- Full-length single-cell transcriptomics

**Key platforms:** PacBio SMRT (IsoSeq), Oxford Nanopore (direct RNA-seq, cDNA)  
**Key tools:** FLAMES, IsoQuant, StringTie2, SQANTI3, Bambu, NanoSim, FLAIR

---

## Running Summary by Topic

### Isoform Disambiguation — Why Read Length Matters
- Long reads unambiguously assign ~33% of reads to a single isoform vs ~25% for 75 bp short reads (Cho et al. 2014 — foundational)
- The gap grows for genes with more exons and lower expression
- Core principle: a read must span a splice junction to disambiguate — this requires reads of ~150+ bp for most human genes, and kilobase-scale for full-length assignment
- Tools like FLAMES, IsoQuant, SQANTI3 all assume this full-junction-spanning property

### Single-Cell Long-Read Transcriptomics (sc-LR-seq)
- Nanopore can be applied to 10x Genomics multiome cDNA libraries for full-length profiling (Mears et al. 2026)
- **TSS capture:** Nanopore of multiome cDNA = 63% of TSS detected by dedicated short-read 5' assay — gap remains
- **Genetic demultiplexing:** Works on nanopore data despite higher error rate — SNP information preserved
- Key tools: FLAMES (isoform analysis), scNanoGPS; demux: vireo + cellsnp-lite

### Mapping Bias and Allele-Specific Expression (ASE)
- Long reads reduce mapping bias at low-mappability loci (pseudogenes, paralogs)
- Long reads enable haplotype assignment at ~7% of reads vs ~4% for short reads (Cho et al. 2014)
- Foundational insight: some ASE/ASAS loci are *only* detectable with long reads due to mappability constraints

### Keyword Filtering Note
- Search terms ("nanopore", "long-read") also match metagenomics and genome assembly papers
- Transcriptomics-specific filter terms to add in future: "mRNA isoform", "RNA-seq", "cDNA", "transcript start site", "alternative splicing" must co-occur

---

## Papers Processed Log

### 2026-04-09
- `arxiv:1405.7316v1` — Cho et al. (2014). "High-resolution transcriptome analysis with long-read RNA sequencing." Foundational read-length comparison study; established isoform disambiguation and ASE gains.
- `10.64898/2026.03.31.715454` — Mears et al. (2026). "Genetic demultiplexing and transcript start site identification from nanopore sequencing of 10x multiome libraries." 63% TSS capture; demux validated.
- Skipped (off-topic — genome assembly/metagenomics): `10.64898/2026.03.27.714782`, `10.64898/2026.03.31.715258`, `10.64898/2026.04.03.716430`, `10.64898/2026.04.03.716425`
- arXiv old papers skipped from index: `arxiv:1703.08260v1` (BIISQ — isoform model, relevant but 2017)

