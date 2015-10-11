#!/usr/bin/python -tt
# vim: set ts=4 sw=4 tw=79 et :
# Copyright (C) 2015  Shawn Sterling <shawn@systemtemplar.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# check_add_routes: This program will check for new route entries and add them
# without restarting network services (don't want to bring down interfaces,etc)
#
# The latest version of this code will be found on my github page:
# https://github.com/shawn-sterling

import glob
import logging
import logging.handlers
import os
import re
import subprocess
import sys

############################################
# You may need to change some of the below #

ip_cmd = "/sbin/ip"                             # location of ip command
# routes_dir = "./routes"                       # dir for local testing
routes_dir = "/etc/sysconfig/network-scripts"   # route dir (redhat)
route_glob = "route-*"                          # filename for route files
debug = False                                   # if set we won't do the change

log_file = 'check_add_routes.log'               # logfile name
log_dir = '/tmp'                                # logfile dir
log_level = 'DEBUG'                             # how much logging to do
log_max_size = 12048576                         # log max size in bytes

# You should stop changing things unless you know what you are doing #
######################################################################

# log info

log = logging.getLogger('log')
log_handler = logging.handlers.RotatingFileHandler(
    os.path.join(log_dir, log_file),
    maxBytes=log_max_size,
    backupCount=20
)
log_format = logging.Formatter(
    "%(asctime)s %(process)d %(funcName)s %(message)s",
    "%B %d %H:%M:%S"
)
log_handler.setFormatter(log_format)
log.addHandler(log_handler)
log.setLevel(log_level)
if log_level == 'DEBUG':
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.WARNING)


def read_route_table():
    """
    reads route table and returns list + default route
    """
    p = subprocess.Popen("/sbin/ip route ls".split(" "),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p.wait()
    if p.returncode != 0:
        log.critical("couldn't check route table, wtf!")
        print "Couldn't read route table, terminating."
        sys.exit(2)
    route_table = []
    for route in p.stdout:
        route = re.sub('\s+', ' ', route).strip()
        route_table.append(route)
        if "default" in route:
            default = route
    # print route_table
    return route_table, default


def read_file(file_name):
    """
    reads file and returns list
    """
    with open(file_name) as f:
        file_content = f.readlines()
        file_array = []
        for line in file_content:
            line = re.sub('\s+', ' ', line).strip()
            line = line.lstrip()
            if len(line) > 5 and line[0] != '#':
                file_array.append(line)
    return file_array


def check_update_routes(route_dir):
    """
    checks if we need to update any routes, then updates them.
    """
    # file_list = [os.path.join(route_dir, f) for f in os.listdir(route_dir)]
    path = "%s/%s" % (route_dir, route_glob)
    log.debug("Path is: %s" % path)
    file_list = glob.glob(path)
    if len(file_list) >= 1:
        for file_name in file_list:
            tmp = file_name.rsplit('/', 1)[1]
            interface = tmp.rsplit('-', 1)[1]
            (route_table, default_route) = read_route_table()
            file_array = read_file(file_name)
            for route in file_array:
                match = False
                if 'default' in route:
                    cmd = "route change"
                    cmd_post = ""
                else:
                    cmd = "route add"
                    cmd_post = "dev %s" % (interface)
                for new_route in route_table:
                    log.debug("r:%s o:%s" % (route, new_route))
                    if route in new_route:
                        match = True
                        log.debug("MATCH! %s in %s" % (route, new_route))
                if not match:
                    update_route("%s %s %s" % (cmd, route, cmd_post))
                else:
                    log.debug("Didn't need to update route: %s" % route)
    else:
        print "CRITICAL: No files to read in : %s" % path
        log.critical("CRITICAL: No files to read in : %s" % path)
        sys.exit(1)


def update_route(cmd):
    """
    updates route using global ip_cmd, will print result if debug = True
    """
    new_cmd = "%s %s" % (ip_cmd, cmd)
    if debug:
        log.debug("new_cmd: %s" % new_cmd)
        log.debug("not running :%s because debug = True" % new_cmd)
    else:
        p = subprocess.Popen(new_cmd.split(" "), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        p.wait()
        if p.returncode != 0:
            log.critical("failed to update route '%s'" % new_cmd)
        print "added route '%s'" % new_cmd
        log.debug("added route '%s'" % new_cmd)


def main():
    """
    My cat's breath smells like catfood. -Ralph Wiggum
    """
    global ip_cmd
    log.debug('check_add_routes startup.')
    if os.geteuid() != 0:
        log.debug("we are not root, will try sudo.")
        ip_cmd = "/usr/bin/sudo %s" % ip_cmd
    check_update_routes(routes_dir)
    log.debug('check_add_routes end')
    sys.exit(0)


if __name__ == '__main__':
    main()
