#!/usr/bin/env python3

import fileinput
import os
import re

import aiohttp
import anybadge
import asyncio


coverage_re = re.compile("TOTAL.*\s+([+-]?([0-9]+\.?[0-9]*|\.[0-9]+)\%)")
thresholds = {
    75: "red",
    85: "orange",
    95: "yellow",
    100: "green",
}


async def write_badge():
    gh_token = os.environ.get("GIST_SECRET")

    for line in fileinput.input():
        match = coverage_re.match(line)
        percentage = float(match.group(2))
        coverage = "{:.2f}".format(percentage)
        badge = anybadge.Badge("Test Coverage", coverage, thresholds=thresholds, value_suffix="%")
        #print(badge.badge_svg_text)
        headers={"Authorization": f"Bearer {gh_token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.patch(
                "https://api.github.com/gists/14417a5617e959df89a524f327f86c92",
                json={
                    "description": "aiohttp-catcher coverage badge",
                    "files": {
                        "aiohttp-catcher-cov.svg": {
                            "content": badge.badge_svg_text
                        }
                    }
                }
            ) as resp:
                print(resp.status)
                print(await resp.text())


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(write_badge())
    finally:
        loop.close()
    exit(0)


if __name__ == "__main__":
    main()
