import os
import sqlite3
import logging
import base64
from mutagen.id3 import ID3
# from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from backend.config import MEDIA_DIR, DB_PATH, AUDIO_METADATA_KEY_TYPES, ALBUM_METADATA_KEY_TYPES, SUPPORTED_EXTS


def find_duplicates(target_list: list) -> list:
    """Find duplicates in a list."""
    seen = set()
    duplicates = set()
    for item in target_list:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)


def find_common_substring(strings: list, option: str = "left") -> str:
    """
    Find the common substring of a list of strings, starting from the left or right, or longest common substring.
    Args:
        strings (list): The list of strings to compare.
        option (str): The option to choose from: "left", "right", "longest".
    Returns:
        str: The common substring.
    """
    if not strings:
        return None
    if len(strings) == 1:
        return strings[0]
    
    def find_from_left(stuff):
        common = []
        for i in range(min(map(len, strings))):
            if len(set(string[i] for string in strings)) == 1:
                common.append(strings[0][i])
            else:
                break
        return "".join(common)
    
    if option == "left":
        return find_from_left(strings)
    elif option == "right":
        return find_from_left([string[::-1] for string in strings])[::-1]
    elif option == "longest":
        longest = ""
        min_string = min(strings, key=len)
        for i in range(len(min_string)):
            for j in range(i + 1, len(min_string) + 1):
                substring = min_string[i:j]
                if all(substring in string for string in strings):
                    if len(substring) > len(longest):
                        longest = substring
        return longest


def find_largest_subset(target_list: list) -> list:
    """
    Find the largest subset of a list of lists.
    Args:
        target_list (list): The list of lists.
    Returns:
        list: The largest subset.
    """
    if not target_list:
        return []
    if len(target_list) == 1:
        return target_list[0]
    
    largest = []
    min_list = min(target_list, key=len)
    for item in min_list:
        if all(item in sublist for sublist in target_list):
            largest.append(item)
    return largest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
