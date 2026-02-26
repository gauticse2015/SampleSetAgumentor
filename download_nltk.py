"""
Download NLTK corpora required by the text augmentor (WordNet + OMW-1.4).

Run from anywhere – the script always saves data next to itself:

    python download_nltk.py          # from the project root
    python /path/to/download_nltk.py # from any directory

The data is saved to  <project_root>/nltk_data/  which is the exact location
the application reads from, so no environment variables need to be set
manually.
"""

import os
import sys
import nltk


# Always resolve relative to THIS file so the script works correctly
# regardless of the working directory it is called from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, 'nltk_data')

PACKAGES = ['wordnet', 'omw-1.4']


def _corpus_exists(package):
    """Return True if the corpus zip or unpacked directory is present."""
    corpora = os.path.join(TARGET_DIR, 'corpora')
    return (
        os.path.exists(os.path.join(corpora, package + '.zip')) or
        os.path.exists(os.path.join(corpora, package))
    )


def download_nltk_data():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"NLTK data directory: {TARGET_DIR}\n")

    all_ok = True
    for package in PACKAGES:
        if _corpus_exists(package):
            print(f"  [OK]  {package} – already present, skipping.")
            continue

        print(f"  [ ]   Downloading {package} ...", end=' ', flush=True)
        try:
            success = nltk.download(package, download_dir=TARGET_DIR, quiet=True)
            if success and _corpus_exists(package):
                print("done.")
            else:
                print("FAILED (download returned False or file not found).")
                all_ok = False
        except Exception as exc:
            print(f"ERROR – {exc}")
            all_ok = False

    print()
    if all_ok:
        print("All NLTK corpora are ready.")
        print("The application will find them automatically (no extra config needed).")
    else:
        print("One or more packages failed to download.")
        print("Check your internet connection and try again.")
        sys.exit(1)


if __name__ == '__main__':
    download_nltk_data()
