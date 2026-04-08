#!/usr/bin/env python3
import click
from app.cli.papers import papers
from app.cli.reports import report, categories
from app.cli.jobs import jobs

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Paper Search CLI - Manage research papers from multiple sources"""
    pass

cli.add_command(papers)
cli.add_command(report)
cli.add_command(categories)
cli.add_command(jobs)

if __name__ == '__main__':
    cli()
