# Read csv of revision history and output editor-article affiliation network

# History CSV format
# page_title, page_namespace, page_id, redirect, rev_num, rev_id, timestamp, user_name, user_id, rev_minor, rev_comment, rev_bytes, rev_bytes_diff, rev_deleted

import csv

# Config
history_file = "data/final_history_output.csv"
skipped_file = "output/history_skipped.csv"
edges_file = "output/editor_article.csv"


try:
    f_hist = open(history_file, "rb")
    f_skipped = open(skipped_file, "wb")
    f_edges = open(edges_file, "wb")

    # Load edges into memory    
    article_users = {}
    reader = csv.reader(f_hist)
    print "Parsing CSV"
    for i, row in enumerate(reader):
        if i % 100000 == 0:
            print "Starting row %d" % i
        # Skip header
        if i == 0:
            continue
        try:
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
                users = article_users[int(page_id)]
            except KeyError:
                users = set()
                article_users[int(page_id)] = users
            users.add(int(user_id))
        except AssertionError:
            f_skipped.write(",".join([str(i)] + row) + "\n")
    
    # Write edges to file
    print "Sorting edges"
    # Sort page_id from from largest number of users to smallest
    size_id = sorted([(len(article_users[page_id]), page_id) for page_id in article_users.keys()], reverse=True)
    print "Writing edges"
    f_edges.write("node_id,community_id,member_prob\n")
    for i, d in enumerate(size_id):
        page_id = d[1]
        for user_id in sorted(list(article_users[page_id])):
            f_edges.write(",".join([str(user_id), str(i), "1.0"]) + "\n")    
finally:
    try:
        f_hist.close()
        f_skipped.close()
        f_edges.close()
    except:
        pass
