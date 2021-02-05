import difflib
import json

import aiohttp
import bs4


COLLEGES_JSON = "static/colleges.json"
OXFORD_DOMAIN = "https://www.{}.ox.ac.uk/"
COLLEGE_LISTING = "https://www.ox.ac.uk/admissions/undergraduate/colleges/college-listing/{}"


class College:

    _loaded_colleges = []

    def __init__(self, name, aliases, website, info_page):
        self.name = name
        self.aliases = aliases
        self.website = website
        self.info_page = info_page

        # this for reusing previously-fetched data to reduce
        # the amount of times we access the oxford website.
        self.cached_info = {}

    def __str__(self):
        return self.name

    @classmethod
    def load_colleges_from_json(cls):
        cls._loaded_colleges.clear()

        with open(COLLEGES_JSON) as json_file:
            all_data = json.load(json_file)

        for college_name, college_data in all_data.items():
            name = college_name
            aliases = set()

            # the aliases, including the full name given by
            # college_name, will be used when searching for
            # a college.
            for alias in college_data["aliases"] + [college_name]:
                aliases.add(alias.lower())

                # some colleges have apostrophes which many
                # people will omit when typing these names.
                if "'" in alias:
                    aliases.add(alias.replace("'", "").lower())

                aliases.add(college_data["subdomain"].lower())

            website = OXFORD_DOMAIN.format(college_data["subdomain"])
            info_page = COLLEGE_LISTING.format(college_data["info_page"])

            college = cls(college_name, aliases, website, info_page)
            cls._loaded_colleges.append(college)

    @classmethod
    def search_for_college(cls, college_name: str, match_threshold: int = 0):
        best_match = set()  # using a set to avoid duplicates.
        best_ratio = 0

        matcher = difflib.SequenceMatcher(a=college_name.lower())

        for college in cls._loaded_colleges:
            # check how close the search matches each alias.
            for alias in college.aliases:
                # note: in the unlikely case that this operation
                # is slow or demanding, we should consider using
                # the `.quick_ratio()` or `.real_quick_ratio()`
                # methods instead, at the loss of some accuracy.
                matcher.set_seq2(alias)
                ratio = matcher.ratio()

                # we may get multiple colleges matching equally.
                # this ambiguity can be handled by the caller.
                if ratio == best_ratio and ratio != 0:
                    best_match.add(college)

                # if there is a distinct improvement, keep it.
                elif ratio > best_ratio:
                    best_match = {college}
                    best_ratio = ratio

        # prevent silly people from searching for "college". you
        # know it would happen, don't even lie to yourself haha.
        matcher.set_seq2("college")
        if matcher.ratio() > best_ratio:
            best_match = set()

        # if the match is below the threshold, consider it a miss.
        # this prevents people from searching for "penis" to get
        # queen's college, as hilarious as that would be. maybe it
        # could be a feature if we use a low threshold! haha.
        if best_ratio < match_threshold:
            best_match = set()

        return best_match

    async def fetch_info_page(self):
        if "info_page" in self.cached_info:
            return self.cached_info["info_page"]

        # since we don't have this page cached, fetch it now.
        async with aiohttp.ClientSession() as session:
            async with session.get(self.info_page) as response:
                response.raise_for_status()  # propagate errors.
                content = await response.text()
                self.cached_info["info_page"] = content

        return content

    async def get_summary(self):
        if "summary" in self.cached_info:
            return self.cached_info["summary"]

        page_content = await self.fetch_info_page()
        soup = bs4.BeautifulSoup(page_content, "html.parser")

        summary = soup.find("meta", {"name": "description"}).get("content")

        self.cached_info["summary"] = summary
        return summary


College.load_colleges_from_json()
