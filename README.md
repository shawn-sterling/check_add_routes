
Check_add_routes
================

[![Build Status](https://travis-ci.org/shawn-sterling/check_add_routes.svg?branch=master)](https://travis-ci.org/shawn-sterling/check_add_routes)

# Introduction

Check_add_routes is a simple script that will check for any
/etc/sysconfig/network-scripts/route-* files, and make sure those routes are
added to the route table.

Why? Because I want to add routes without restarting the network service.

I'm calling this via puppet, when I change a route- file, on a KVM hypervisor
that has 6 physical interfaces that are each bonded, and each has a few sub
interfaces for vlans. Basically doing a service network restart is disruptive
and I don't want to do it just because I'm adding a few routes.

It's entirely possible this is only useful to me, but you never know.

# License

check_add_routes is released under the [GPL v2](http://www.gnu.org/licenses/gpl-2.0.html).

# Find a bug?

Open an Issue on github and I will try to fix it asap.

# Contributing

I'm open to any feedback / patches / suggestions.

Shawn Sterling shawn@systemtemplar.org
