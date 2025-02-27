"""
"""
import argparse
import asyncio
import os

from taotie.reporter.notion_reporter import NotionReporter
from taotie.utils import *


def parse_args(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(dest="command")

    # Sub-parser for report
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument(
        "--date-lookback",
        type=int,
        default=1,
        help="Number of days to look back for report",
    )
    report_parser.add_argument(
        "--type-filters",
        type=str,
        default="arxiv",
        help="Comma-separated list of type filters (arxiv, github-repo)",
    )
    report_parser.add_argument(
        "--topic-filters",
        type=str,
        default="",
        help="Comma-separated list of topic filters",
    )
    report_parser.add_argument(
        "--model-type",
        type=str,
        default="gpt-3.5-turbo-16k-0613",
        help="Model type for report",
    )
    report_parser.add_argument(
        "--language", type=str, default="English", help="Language for report"
    )

    # Sub-parser for delete key
    delete_parser = subparsers.add_parser("delete", help="Delete a key")
    delete_parser.add_argument("key", type=str, help="Key to delete")

    args = parser.parse_args()
    return args


async def run_notion_reporter(args: argparse.Namespace):
    """Run the script to generate the notion report."""
    load_dotenv()
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        raise ValueError("NOTION_DATABASE_ID not found in environment")
    type_filters = args.type_filters.split(",")
    topic_filters = args.topic_filters.split(",")
    reporter = NotionReporter(
        knowledge_source_uri=database_id,
        date_lookback=args.date_lookback,
        type_filters=type_filters,
        topic_filters=topic_filters
        if topic_filters
        else os.environ.get("CANDIDATE_TAGS", "").split(","),
        model_type=args.model_type,
        language=args.language,
    )
    database_id = os.environ.get("NOTION_REPORT_DATABASE_ID", None)
    await reporter.distill(
        database_id=database_id, type=type_filters[0], language=args.language
    )


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Argument Parser for Report and Delete Key"
    )
    args = parse_args(parser=parser)
    if args.command == "report":
        asyncio.run(run_notion_reporter(args))
    else:
        parser.print_help()
