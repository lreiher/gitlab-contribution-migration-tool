#!/usr/bin/env python

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

import bs4
from tqdm import tqdm


def parseArguments():

    parser = argparse.ArgumentParser(description="Parses GitLab contributions from profile page HTML and commits with same frequency to other repository.")

    parser.add_argument("html", type=str, help="HTML-file of GitLab profile page")
    parser.add_argument("repo", type=str, help="path to repository for mirroring commits")

    args = parser.parse_args()

    return args


def parseContributions(html_file):

    contributions_per_date = {}

    with open(html_file, "r") as f:
        html = bs4.BeautifulSoup(f, "html.parser")

    rects = html.find_all("rect", {"class": "user-contrib-cell has-tooltip"})
    for rect in rects:
        contribs_and_date = rect["title"].split("<br />")
        try:
            contrib_count = int(contribs_and_date[0].split(" ")[0])
        except ValueError:
            continue
        date = contribs_and_date[1].split(">")[1].split("<")[0]
        date = datetime.strptime(date, "%A %b %d, %Y")
        contributions_per_date[date] = contrib_count
    
    return contributions_per_date


def commitContributions(repo, contributions_per_date):

    # check repo
    if not Path(repo).is_dir():
        print(f"Repository {repo} not found")
        return
    if subprocess.run(["git", "rev-parse"],
                      cwd=repo,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode != 0:
        print(f"Repository {repo} is not a valid Git repository")
        return

    # create contributions by making commits at certain date
    n_total_contribs = sum(contributions_per_date.values())
    n_committed_contribs = 0
    tq = tqdm(contributions_per_date)
    for date in tq:

        n_contribs = contributions_per_date[date]
        datestr = date.strftime("%m-%d-%Y")
        tq.set_description(datestr)

        # check for missing contributions on given day
        n_existing_contribs = int(
            subprocess.check_output(f"git log --pretty=format:%ad --after='{datestr} 00:00:00' --before='{datestr} 23:59:59' | sort | wc -l",
                                    shell=True,
                                    cwd=repo,
                                    stderr=subprocess.DEVNULL)
        )
        n_contribs -= n_existing_contribs
        if n_contribs <= 0:
            continue
        n_committed_contribs += n_contribs

        # make commits
        env = {
            **os.environ,
            "GIT_COMMITTER_DATE": date.strftime(f"{datestr} 12:00:00"),
            "GIT_AUTHOR_DATE": date.strftime(f"{datestr} 12:00:00"),
        }
        for k in range(n_contribs):
            p = subprocess.run(["git", "commit", "--allow-empty", "-m", "add contribution"],
                                env=env,
                                cwd=repo,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

    print(f"Created {n_committed_contribs} new commits in {repo} for a total of {n_total_contribs} mirrored commits.")


if __name__ == "__main__":
   
    args = parseArguments()

    contributions_per_date = parseContributions(args.html)

    commitContributions(args.repo, contributions_per_date)
