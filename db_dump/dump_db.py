#!/usr/bin/env python
from sys import path
from ConfigParser import ConfigParser
from os import system

path.append("../sqft")
import settings

db = settings.DATABASE_NAME 
pw = settings.DATABASE_PASSWORD
un = settings.DATABASE_USER
system("mysqldump -u%(un)s --password='%(pw)s' %(db)s > sqft.sql" % locals())
