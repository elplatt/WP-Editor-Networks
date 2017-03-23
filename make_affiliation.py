# Read csv of revision history and output editor-article affiliation network

# History CSV format
# page_title, page_namespace, page_id, redirect, rev_num, rev_id, timestamp, user_name, user_id, rev_minor, rev_comment, rev_bytes, rev_bytes_diff, rev_deleted

import csv

# Config
history_file = "data/final_history_output.csv"
skipped_file = "output/history_skipped.csv"
community_file = "output/editor_article.csv"
edges_file = "output/wpusertalk-edges.csv"

dates = ["2007-03-23", "2007-03-24", "2007-03-25", "2007-03-26", "2007-03-27", "2007-03-28", "2007-03-29", ]

try:
    f_hist = open(history_file, "rb")
    f_skipped = open(skipped_file, "wb")
    f_com = open(community_file, "wb")

    # Load subset of users in user talk network
    print "Loading usertalk network and extracting ids"
    user_ids = set()
    with open (edges_file) as f_edges:
        f_edges.next()
        for row in f_edges:
            source, target = row.rstrip().split(",")
            user_ids.add(int(source))
            user_ids.add(int(target))
    
    # Load edges into memory
    article_users = {}
    reader = csv.reader(f_hist)
    print "Parsing revision CSV"
    for i, row in enumerate(reader):
        if i % 100000 == 0:
            print "Starting row %d" % i
        # Skip header
        if i == 0:
            continue
        try:
            if len(row) != 14:
                raise AssertionError
            # Skip entries outside the configured date range
            if row[6][0:10] not in dates:
                continue
            page_namespace = row[1]
            # Get user id and skip if not part of user talk network
            user_id = row[8]
            if (int(user_id) not in user_ids):
                continue
            page_id = row[2]
            if page_namespace != "0" and page_namespace != "1":
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
    f_com.write("node_id,community_id,member_prob\n")
    for i, d in enumerate(size_id):
        page_id = d[1]
        # Skip articles with only a couple editors
        if len(article_users[page_id]) < 3:
            continue
        for user_id in sorted(list(article_users[page_id])):
            f_com.write(",".join([str(user_id), str(i), "1.0"]) + "\n")    
finally:
    try:
        f_hist.close()
        f_skipped.close()
        f_com.close()
    except:
        pass
