"""Command line tools for chat, public search and source snapshots."""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from .config import ProviderRole, load_provider_config, load_store_config
from .errors import AgenticRAGError
from .ingestion import Ingestor
from .providers.openai_compatible import build_chat_provider
from .postgres_store import PostgresCorpusStore
from .store import SQLiteCorpusStore
from .web_chat import WebChat
from .web_search import configured_search_provider, configured_search_label, local_web_search_available


def build_parser():
    parser = argparse.ArgumentParser(prog='agenticrag', description='Chat and web search')
    parser.add_argument('--db', default='.data/corpus.db')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init-db')
    commands.add_parser('doctor')
    server = commands.add_parser('serve', help='Start Chat & Web')
    server.add_argument('--host', default='127.0.0.1')
    server.add_argument('--port', type=int, default=8787)
    server.add_argument('--no-open', action='store_true')
    server.add_argument('--allow-remote', action='store_true')
    ingest = commands.add_parser('ingest', help='Store a local source without loading an embedding model')
    ingest.add_argument('path', type=Path)
    ingest.add_argument('--collection', required=True)
    ingest.add_argument('--scope', action='append', required=True)
    source = commands.add_parser('show-source')
    source.add_argument('source_version_id')
    source.add_argument('--scope', action='append', required=True)
    ask = commands.add_parser('ask', help='One normal completion, optionally with public web pages')
    ask.add_argument('question')
    ask.add_argument('--web', action='store_true', help='Authorize sending this question to the configured search provider')
    ask.add_argument('--collection', default='default')
    ask.add_argument('--scope', action='append', default=['private'])
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == 'serve':
            from .server import serve
            serve(host=args.host, port=args.port, db_path=args.db, open_browser=not args.no_open, allow_remote=args.allow_remote)
            return 0
        if args.command == 'doctor':
            chat = load_provider_config(ProviderRole.CHAT)
            print(json.dumps({'chat': chat.public_dict(), 'web': {'provider': configured_search_label(), 'available': local_web_search_available()}}))
            return 0
        config = load_store_config(args.db)
        store = SQLiteCorpusStore(config.sqlite_path) if config.backend == 'sqlite' else PostgresCorpusStore.connect(config.postgres_dsn, config.objects_root)
        with store:
            store.initialize()
            if args.command == 'init-db':
                result = {'status': 'initialized'}
            elif args.command == 'ingest':
                result = asdict(Ingestor(store).ingest_file(args.path, args.collection, args.scope))
            elif args.command == 'show-source':
                result = asdict(store.get_source(args.source_version_id, scopes=args.scope))
            else:
                chat = build_chat_provider(load_provider_config(ProviderRole.CHAT))
                result = WebChat(chat, store, search=configured_search_provider() if args.web else None).run(
                    args.question, scopes=args.scope, collection=args.collection).to_dict()
            print(json.dumps(result, ensure_ascii=False))
        return 0
    except (AgenticRAGError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
