    import argparse
    from audit_engine.pipelines.full_pipeline import run_full_audit
    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.pipelines.fe_pipeline import run_fe_report

    def main():
        parser = argparse.ArgumentParser(prog="audit-engine")
        subparsers = parser.add_subparsers(dest="command", required=True)

        master = subparsers.add_parser("master")
        master.add_argument("file", nargs="?")

        fe = subparsers.add_parser("fe")
        fe.add_argument("file", nargs="?")

        full = subparsers.add_parser("full")
        full.add_argument("file", nargs="?")

        args = parser.parse_args()

        if args.command == "master":
            run_master_report(args.file)
        elif args.command == "fe":
            run_fe_report(args.file)
        elif args.command == "full":
            run_full_audit(args.file)

    if __name__ == "__main__":
        main()
    
