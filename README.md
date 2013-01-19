# Cloud Server Backup Imaging

This script allows you to have scheduled image backups of your server. It is meant to be run as a cron job.

The first time it is run, it will ask for:

* Your account username
* Your account API key
* The ID of the server(s) to back up. You may enter more than one ID, separated by spaces.
* The number of backup images to maintain for each server

Once these are entered, these values will be stored and will not need to be entered again, unless you wish to change them.


## Command Line Arguments

You may also enter them on the command line as arguments if you prefer:

    -h, --help          show this help message and exit
    
    --username USERNAME, -u USERNAME
                        The account's username
    
    --server-id SERVER_ID, -s SERVER_ID
                        The ID of the server to back up. You may specify this
                        parameter multiple times to back up multiple servers.
    
    --retain RETAIN, -r RETAIN
                        Number of backups to retain
    
    --persist, -p       Write the passed values for future runs


## Adding to cron

To schedule the backup image creation, add a cron job. If you are unfamiliar with `cron`, it is a built-in utility for running programs at regular intervals.

To add a daily backup, run `crontab -e`, and add the following line:

     15 3 * * * /usr/bin/python /path/to/image_backup.py

This will run once a day at 3:15 am. To run at a different time, change the values in the first two columns to the desired values.

For a weekly backup, change the last asterisk to a value between 0-6 (Sunday-Saturday):

     40 22 * * 5 /usr/bin/python /path/to/image_backup.py

This will run the script every Friday at 10:40 pm.


## Scheduling backups for multiple servers

You can easily schedule regular backup images for multiple servers by passing the individual parameters to the cron command. Consider this example:

You have 3 servers which you want to back up every night at 11pm, retaining the 10 most recent backup images. You also have a single server which only requires weekly backup on Sundays, and you wish to retain the most recent 4 images for that server. Your cron entries to do this would be:

    0 11 * * *  /usr/bin/python /path/to/image_backup.py -s AAAAA-AAAAA -s BBBBB-BBBBB -s CCCCC-CCCCC -r 10
    0 11 * * 0  /usr/bin/python /path/to/image_backup.py -s DDDDD-DDDDD -r 4

