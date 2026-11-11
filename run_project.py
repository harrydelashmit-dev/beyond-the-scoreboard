"""One Python entry point for downloads, cleaning, analysis, charts, and tests."""
import argparse
from pathlib import Path
import subprocess
import sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--download',action='store_true',help='Retrieve/cache original official public files')
    p.add_argument('--from-processed',action='store_true',help='Re-estimate using versioned processed public data without raw downloads')
    p.add_argument('--test',action='store_true',help='Run the Python test suite after the build')
    p.add_argument('--expanded',action='store_true',help='Run the audited Knight/ESPN three-part feasibility analysis')
    p.add_argument('--report-only',action='store_true',help='Rebuild expanded report from versioned aggregate results; no registered workbook required')
    a=p.parse_args();root=Path(__file__).resolve().parent
    if a.report_only and not a.expanded:p.error('--report-only requires --expanded')
    if a.expanded:
        if a.from_processed:p.error('Expanded estimation requires the local registered source panel; use --report-only for aggregate-results reproduction')
        command=[sys.executable,'-m','scoreboard.feasibility']
        if a.report_only:command+=['--report-only']
        else:
            if a.download:
                subprocess.run([sys.executable,'-m','scoreboard.download'],cwd=root,check=True)
                command+=['--download']
            command+=['--build']
        subprocess.run(command,cwd=root,check=True)
        if a.test:subprocess.run([sys.executable,'-m','pytest','-q'],cwd=root,check=True)
        return
    if a.download:subprocess.run([sys.executable,'-m','scoreboard.download'],cwd=root,check=True)
    if not a.from_processed:
        subprocess.run([sys.executable,'-m','scoreboard.clean'],cwd=root,check=True)
    subprocess.run([sys.executable,'-m','scoreboard.report'],cwd=root,check=True)
    if a.test:subprocess.run([sys.executable,'-m','pytest','-q'],cwd=root,check=True)

if __name__=='__main__':main()
