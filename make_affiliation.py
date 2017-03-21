# Read csv of revision history and output editor-article affiliation network

# History CSV format
# page_title, page_namespace, page_id, redirect, rev_num, rev_id, timestamp, user_name, user_id, rev_minor, rev_comment, rev_bytes, rev_bytes_diff, rev_deleted

import csv

# Config
history_file = "data/final_history_output-sample.csv"
skipped_file = "output/history_skipped.csv"
edges_file = "output/editor_article.csv"


try:
    f_hist = open(history_file, "rb")
    f_skipped = open(skipped_file, "wb")
    f_edges = open(edges_file, "wb")

    # Load edges into memory    
    user_articles = {}
    reader = csv.reader(f_hist)
    for i, row in enumerate(reader):
        # Skip header
        if i == 0:
            continue
        try:
            if i % 10000 == 0:
                print "Starting row %d" % i
            if len(row) != 14:
                raise AssertionError
            page_namespace = row[1]
            user_id = row[8]
            page_id = row[2]
            if page_namespace != "0":
                continue
            if user_id == "0" or len(user_id) == 0:
                # Anonymous, skip
                continue
            if len(page_id) == 0:
                raise AssertionError
            try:
                articles = user_articles[int(user_id)]
            except KeyError:
                articles = set()
                user_articles[int(user_id)] = articles
            articles.add(int(page_id))
        except AssertionError:
            f_skipped.write(",".join([str(i)] + row) + "\n")
    
    # Write edges to file
    for user_id in sorted(user_articles.keys()):
        for page_id in sorted(list(user_articles[user_id])):
            f_edges.write(",".join([str(user_id), str(page_id)]) + "\n")    
finally:
    try:
        f_hist.close()
        f_skipped.close()
        f_edges.close()
    except:
        pass