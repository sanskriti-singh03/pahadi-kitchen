import os
import random
from datetime import datetime, timedelta

start_date = datetime(2026, 3, 24)
end_date = datetime(2026, 4, 24)

current_date = start_date

while current_date <= end_date:
    # Random skip: 0 or 1 day
    skip_days = random.choice([0, 1])
    
    # Random number of commits per day (optional, makes it more natural)
    commits_today = random.randint(1, 3)

    for _ in range(commits_today):
        # Random time in the day
        random_time = current_date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        date_str = random_time.strftime("%Y-%m-%d %H:%M:%S")

        # Make a dummy change
        with open("dummy.txt", "a") as f:
            f.write(f"Commit at {date_str}\n")

        os.system("git add dummy.txt")

        # Set commit date
        env = f'GIT_AUTHOR_DATE="{date_str}" GIT_COMMITTER_DATE="{date_str}"'
        os.system(f'{env} git commit -m "Backdated commit {date_str}"')

    # Move forward (1 day + optional skip)
    current_date += timedelta(days=1 + skip_days)

print("done creating commits!")