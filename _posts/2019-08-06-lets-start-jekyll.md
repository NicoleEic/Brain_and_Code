---
layout: post
title: "Let's start to use Jekyll"
---

Ok... you might have figured out that this post was actually created automatically when I first initialized the repository. But in the end I would like to keep it to remind myself and you how to use Jekyll as a site generator and GitHub Pages to host the page.

I found some useful info to get started with Jekyll at the following links:
```
https://jekyllrb.com/docs/home
https://github.com/jekyll/jekyll
https://talk.jekyllrb.com/
https://onextrapixel.com/start-jekyll-blog-github-pages-free/
```

For to quick-start a site, just type the following in your computer terminal:
```
gem install bundler jekyll
jekyll new Brain_and_Code
cd Brain_and_Code
bundle exec jekyll serve
```
The site is generated locally and you can access it in your browser by navigating to:
```
http://localhost:4000
````

I wanted the blog to be connected to my already existing GitHub projects, so, for me, Github Pages seemed to be the perfect solution. I followed the instruction on GitHub to integrate my blog with my already existing repository:
```
https://help.github.com/en/articles/configuring-a-publishing-source-for-github-pages
```

This enables me to work on my projects and my blog at the same repository but under two separate branches:
```
https://github.com/NicoleEic/Brain_and_Code/tree/master/
https://github.com/NicoleEic/Brain_and_Code/tree/gh-pages/
```

# Error handling
If you see in your local command line something like:
```
jekyll 3.8.5 | Error:  Address already in use - bind(2) for xxx.x.x.x:4000
```
You need to kill the process that is running in the background manually by determining it's PID:
```
$ lsof -wni tcp:4000
COMMAND   PID       USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
ruby    43631      <user>  13u  IPv4 0x3453ebb5e10f92c9      0t0  TCP *:terabase (LISTEN)
$ kill -9 43631
$ jekyll --watch serve
bundle exec jekyll serve
```
