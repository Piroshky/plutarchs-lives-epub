import os
import requests
from bs4 import BeautifulSoup, Comment, Doctype
import codecs

#This code isn't too elegant, but it gets the job done.

def convert_page(filename, dest_dir="./converted/"):
    inputfile = codecs.open(filename, 'r', encoding='utf-8', errors='ignore')
    soup = BeautifulSoup(inputfile, 'html5lib')
    soup.prettify()
    
    truefilename = os.path.splitext(os.path.basename(filename))[0].replace('*', '')    

    # remove head
    head = soup.find("head")
    for child in head.findChildren(recursive=False):
        if child.name != "title":
            child.decompose()

    # add in proper stylesheet
    csslink = soup.new_tag("link", href="../Styles/Style0001.css", rel="stylesheet", type="text/css")
    head.append(csslink)

    # removing tags that aren't a part of the text
    for child in soup.find("body").findChildren(recursive=False):
        if child.name != "div":
            child.decompose()
        elif not child.has_attr('class'):
            child.decompose()

    green = soup.find("span",{"class":"green"})
    if green != None:
        green.parent.decompose()            
    soup.find("img",{"class":"setPageWidth"}).parent.decompose()

    headerbox = soup.find("table", {"class":"headerbox"})
    if headerbox != None:
        headerbox.decompose()
        
    navbar =  soup.find("table", {"id":"navbar"})
    if navbar != None:
        navbar.decompose()

    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    
    # Remove pagenums, etc
    for d in soup.findAll("span",{"class":"pagenum"}):
        d.decompose()

    for d in soup.findAll("a",{"class":"Tsec"}):
        d.decompose()        
    
    for d in soup.findAll("p",{"class":"ivy"}):
        d.decompose()

    for d in soup.findAll("hr"):
        d.decompose()
        
    REMOVE_ATTRIBUTES = ['onmouseout','onmouseover', 'name']    
    for tag in soup.recursiveChildGenerator():
        if hasattr(tag, 'attrs'):
            tag.attrs = {key:value for key,value in tag.attrs.items() 
                         if key not in REMOVE_ATTRIBUTES}

    ### <a> tags
    # strip leading and trailing space
    for d in soup.find_all("a", href=True):
        d['href'] = d['href'].rstrip().lstrip()

    # remove url from citation link, wrap displayed text in brackets
    for d in soup.findAll("a",{"class":"ref"}):
        d['href'] = '#' + d['href'].split('#')[1].rstrip()
        d.string = '[' + d.string + ']'

    for d in soup.findAll("a",{"class":"note"}):
        d['href'] = '#' + d['href'].split('#')[1].rstrip()
        d.string = '[' + d.string + ']'

    # Code to find any images in the text and download them, if not already present.
    # wget didn't seem to download them, or they were misplaced by me
p    # This is commented out so that people running the script wont be needlessly hammering
    # the website.
    # for d in soup.find_all("img", src=True):
    #     d['src'] = d['src'].lstrip().rstrip()
    #     src = d['src'].replace("*", "").split("/")
    #     image_name = src[-2]+"_"+src[-1]

    #     # download the images if they aren't in the Images directory
    #     if image_name not in os.listdir("./Images/"):
    #         imgfile = requests.get("https://penelope.uchicago.edu/Thayer/" + d['src'])
    #         open('./Images/' + image_name, 'wb').write(imgfile.content)

    #     d['src'] = "../Images/" + image_name
            
    
    # Add <base> to hrefs, epub doesn't support the base tag
    for d in  soup.findAll("a", href=True):
        if d.attrs['href'][:2] == "E/":
            d.attrs['href'] = "https://penelope.uchicago.edu/Thayer/" + d.attrs['href']

    for d in soup.findAll("script"):
        d.decompose()
    
    # Remove empty a tags that sometimes wrap pagenums
    for empty in soup.select('a[id]'):
        if len(empty.get_text(strip=True)) == 0:
            empty.decompose()    

    for item in soup.contents:
        if isinstance(item, Doctype):
            item.extract()

    # Adding in the doctype to the file directly is easier than using BeautifulSoup, which
    # treats this tag differently from all the others.
    doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">"""

    # epub doesn't play well with files that contain "+"
    newfilename = truefilename.replace("+", "_comp_")
    print(newfilename)
    
    newfile = open(dest_dir + newfilename + ".xhtml", "w")
    
    newfile.write("""<?xml version="1.0" encoding="utf-8"?>""" + "\n")
    newfile.write(doctype)

    unformatted_tag_list = []

    for i, tag in enumerate(soup.find_all(['span','a'])):
        unformatted_tag_list.append(str(tag))
        tag.replace_with('{' + 'unformatted_tag_list[{0}]'.format(i) + '}')

    pretty_markup = soup.prettify().format(unformatted_tag_list=unformatted_tag_list)

    newfile.write(pretty_markup)

    
def convert_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            convert_page(directory + filename)

