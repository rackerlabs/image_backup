#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import keyring
import logging
import logging.handlers
import sys

import pyrax
import pyrax.exceptions as exc


logger = logging.getLogger("MyLogger")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler()
logger.addHandler(handler)

def logit(msg):
    logger.info("RackspaceImageScheduler: %s" % msg)


# Configuration settings are stored using keyring. These
# are the keys for those settings.
ID_OF_INSTANCE = "scheduled_image_instance_id"
ACCOUNT_NAME = "cloud_username"
COPIES_TO_KEEP = "scheduled_image_number_of_copies"

parser = argparse.ArgumentParser(description="Run regularly scheduled images of a cloud server.")
parser.add_argument("--username", "-u",  help="The account's username")
parser.add_argument("--server-id", "-s", action="append", help="The ID of the server to back up. "
        "You may specify this parameter multiple times to back up multiple servers.")
parser.add_argument("--retain", "-r", type=int, help="Number of backups to retain")
parser.add_argument("--persist", "-p", action="store_true", help="Store the values specified in "
        "this call to be used as the default in future runs.")
args = parser.parse_args()

username = args.username or keyring.get_password("pyrax", ACCOUNT_NAME)
instance_ids = args.server_id or keyring.get_password("pyrax", ID_OF_INSTANCE)
if isinstance(instance_ids, basestring):
    instance_ids = json.loads(instance_ids)
num_copies = args.retain or keyring.get_password("pyrax", COPIES_TO_KEEP)
if args.persist:
    j_ids = json.dumps(instance_ids)
    logit("Setting username='%s'; ids='%s'; retention='%s'." % (username, j_ids, num_copies))
    keyring.set_password("pyrax", ACCOUNT_NAME, username)
    keyring.set_password("pyrax", ID_OF_INSTANCE, j_ids)
    keyring.set_password("pyrax", COPIES_TO_KEEP, str(num_copies))
    
if not username:
    username = raw_input("Please enter the account username: ")
    if not username:
        logit("Cannot continue without account username.")
        sys.exit()
    keyring.set_password("pyrax", ACCOUNT_NAME, username)
try:
    pyrax.keyring_auth(username)
except exc.AuthenticationFailed:
    api_key = raw_input("Please enter the API key for account '%s': " % username)
    keyring.set_password("pyrax", username, api_key)
    try:
        pyrax.keyring_auth(username)
    except exc.AuthenticationFailed:
        logit("Unable to authenticate.")
        sys.exit()
# Turn off debug output
pyrax.set_http_debug(False)

if not instance_ids:
    print "Please enter the ID of the server(s) to backup. You may enter more "\
            "than one ID, separated by spaces. "
    input_ids = raw_input()
    if not input_ids:
        logit("Cannot continue without ID of instance.")
        sys.exit()
    # Strip commas, in case they added them to the input
    input_ids = input_ids.replace(",", "")
    instance_ids = [iid.strip() for iid in instance_ids.split(" ")]
    keyring.set_password("pyrax", ID_OF_INSTANCE, json.dumps([instance_ids]))

if not num_copies:
    num_copies = raw_input("How many backup images should be retained? ")
    if not num_copies:
        logit("Cannot continue without copy retention value.")
        sys.exit()
    keyring.set_password("pyrax", COPIES_TO_KEEP, num_copies)
num_copies = int(num_copies)

#TODO: add support for other regions
cs_dfw = pyrax.connect_to_cloudservers("DFW")
cs_ord = pyrax.connect_to_cloudservers("ORD")
regions = (cs_dfw, cs_ord)
now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

for instance_id in instance_ids:
    for region in regions:
        try:
            instance = region.servers.get(instance_id)
            logit("Found instance '%s' in region '%s'" % (instance.name, region.client.region_name))
            break
        except exc.ServerNotFound:
            continue

    image_name = "%s-%s" % (instance.name, now)

    images = region.images.list()
    backups = [image for image in images
            if image.name.startswith(instance.name)]
    # Sorting by name will result in the oldest first.
    backups.sort(lambda x,y: cmp(x.name, y.name))

    to_delete = []
    # Don't delete just yet; the image creation step below
    # could fail.
    while len(backups) >= num_copies:
        to_delete.append(backups.pop(0))

    try:
        instance.create_image(image_name)
        logit("Successfully created backup image: %s" % image_name)
    except exc.ServerClientException as e:
        logit("Unable to create image: %s" % e)
        continue

    for old_image in to_delete:
        old_image.delete()
        logit("Deleted old image: %s" % old_image.name)
