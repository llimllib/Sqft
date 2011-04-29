#!/usr/bin/env python
from sys import path
from ConfigParser import ConfigParser
from os import system

path.append("../sqft")
import settings

db = settings.DATABASE_NAME 
pw = settings.DATABASE_PASSWORD
un = settings.DATABASE_USER
mysql = "mysql --user='%(un)s' --password='%(pw)s' " % locals()

system("""%(mysql)s -e 'drop database if exists %(db)s' \\
&& %(mysql)s -e 'create database %(db)s' \\
&& %(mysql)s %(db)s < sqft.sql""" % locals())
