# Read csv of revision history and output editor-article affiliation network

# History CSV format
# page_title, page_namespace, page_id, redirect, rev_num, rev_id, timestamp, user_name, user_id, rev_minor, rev_comment, rev_bytes, rev_bytes_diff, rev_deleted

import csv
import re

# Config
history_file = "data/final_history_output-sample.csv"
skipped_file = "output/history_skipped.csv"
edges_file = "output/usertalk_edges.csv"
blacklist_file = "output/user_blacklist.csv"

# Regular expressions
usertalk_re = re.compile(
    "User talk:(.+)"
)
ip_re = re.compile(
    "\d+\.\d+\.\d+\.\d+"
)

try:
    f_hist = open(history_file, "rb")
    f_skipped = open(skipped_file, "wb")
    f_edges = open(edges_file, "wb")
    f_blacklist = open(blacklist_file, "wb")

    # Load edges into memory
    user_ids = {}
    source_targets = {}
    blacklist = set()
    reader = csv.reader(f_hist)
    print "Parsing CSV"
    for i, row in enumerate(reader):
        if i % 100000 == 0:
            print "Starting row %d" % i
            print "  %d sources" % len(source_targets)
        # Skip header
        if i == 0:
            continue
        try:
            if len(row) != 14:
                raise AssertionError
            page_title = row[0]
            page_namespace = row[1]
            user_name = row[7]
            user_id = row[8]
            page_id = row[2]
            if page_namespace != "3":
                continue
            if user_id == "0" or len(user_id) == 0:
                # Anonymous, skip
                continue
            if len(page_id) == 0:
                raise AssertionError
            try:
                target_name, = re.match(usertalk_re, page_title).groups()
                if re.match(ip_re, target_name):
                    # Skip anonymous users
                    continue
            except TypeError:
                raise AttributeError
            # Add edge
            try:
                targets = source_targets[user_name]
            except KeyError:
                targets = set()
                source_targets[user_name] = targets
            targets.add(target_name)
            # Link id to name
            try:
                source_id = user_ids[user_name]
                if source_id != int(user_id):
                    blacklist.add(user_name)
                    f_blacklist.write(user_name + "\n")
            except KeyError:
                user_ids[user_name] = user_id
        except AssertionError:
            f_skipped.write(",".join([str(i)] + row) + "\n")
    
    # Convert to undirected edges and deduplicate
    print "Converting names to ids"
    edges = set()
    for source_id, targets in source_targets.iteritems():
        for target in targets:
            try:
                target_id = user_ids[target]
            except KeyError:
                print "No user id: %s" % target
                continue
            edges.add( (min([source_id,target_id]), max([source_id,target_id])) )
    
    print "Writing edges"
    f_edges.write("source_id,target_id\n")
    for e in edges:
        f_edges.write("%d,%d\n" % e)    
finally:
    try:
        f_hist.close()
        f_skipped.close()
        f_edges.close()
        f_blacklist.close()
    except:
        pass
