#! /bin/bash


mysql -uroot -pmysql information < information_info_category.sql

mysql -uroot -pmysql information < information_info_news.sql