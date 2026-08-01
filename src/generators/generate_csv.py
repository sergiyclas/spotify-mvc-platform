# src/generators/generate_csv.py

"""CSV data generator"""

import csv
import random

from src.common.logger import get_logger

logger = get_logger(__name__)

# Configuration
NUM_USERS = 50
NUM_SONGS = 139
NUM_PLAYLISTS = 5
SUBSCRIPTION_TYPES = ["FREE", "PREMIUM", "STUDENT"]
GENRES = ["Rock", "Pop", "Hip-Hop", "Jazz", "EDM", "Classical", "Blues", "Country"]


def generate_csv_data(output_path: str = "spotify_data.csv"):
    """Generate test CSV data"""

    try:
        # Create CSV file
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "email",
                "subType",
                "playlistName",
                "songTitle",
                "artist",
                "duration",
                "genre",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Generate data
            rows = []
            for i in range(NUM_SONGS):
                user_id = random.randint(0, NUM_USERS - 1)
                email = f"user{user_id}@example.com"
                sub_type = random.choice(SUBSCRIPTION_TYPES)
                playlist_id = random.randint(0, NUM_PLAYLISTS - 1)
                playlist_name = f"Playlist_{playlist_id}"
                song_title = f"Song Title {i}"
                artist = f"Artist {random.randint(0, 19)}"
                duration = random.randint(120, 300)
                genre = random.choice(GENRES)

                row = {
                    "email": email,
                    "subType": sub_type,
                    "playlistName": playlist_name,
                    "songTitle": song_title,
                    "artist": artist,
                    "duration": duration,
                    "genre": genre,
                }
                rows.append(row)

            # Write rows
            writer.writerows(rows)

        logger.info(f"Generated {len(rows)} rows of data in {output_path}")
        return len(rows)

    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}")
        raise


if __name__ == "__main__":
    generate_csv_data()
