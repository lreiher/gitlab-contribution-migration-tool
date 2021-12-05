# gitlab-contribution-migration-tool

This little scripts can be used to mirror the number of GitLab contributions (i.e., commits) on a specific day to a different repositoy. The dedicated repository can then be uploaded got GitHub, in order to have a mirrored contribution page.

## Usage

```
❯ ./gitlab-contrib-migrator.py --help 
usage: gitlab-contrib-migrator.py [-h] html repo

Parses GitLab contributions from profile page HTML and commits with same frequency to other
repository.

positional arguments:
  html        HTML-file of GitLab profile page
  repo        path to repository for mirroring commits

optional arguments:
  -h, --help  show this help message and exit
```
