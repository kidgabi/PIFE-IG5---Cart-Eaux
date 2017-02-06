# -*- coding: utf-8 -*-
import urllib
import urllib2
import random
import sys
import json
import os
from pprint import pprint
import html2text
import codecs
from datetime import datetime, timedelta
import re
import time
import ssl


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders



def convert_pdf_to_txt(path):
    """ Convert a PDF document into text.
        Args:
            path: the path of the PDF document

        Returns:
            The text converted from the PDF document.

    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
# Supply the password for initialization.
    document = PDFDocument(parser, password)
    if document.is_extractable:
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text


date = datetime.now().strftime('%Y-%m-%d_%Hh%M')    # Current date and time in format YYYY-mm-dd_HhM

# User's keys required for the functioning of the program
key="YOUR_API_KEY"   # Enter here your Google API Key
cx="YOUR_SEARCH_ENGINE_ID"  # Enter here your search engine ID


# The user enters the city name on which he wants to run the search
city=raw_input("Sur quelle ville voulez-vous effectuer la recherche ?")

# Replacing characters that can cause issue once inserted in the URL
city=city.replace(" ","%20")
city=city.replace("’","%27")
city=city.replace("'","%27")

cpt_query=0     # Counter for the queries
path_city=city  
if not os.path.exists(path_city):   # If the directory of the city does not exist, it creates it
    os.makedirs(path_city)
    print("Creation of directory for "+str(city))
    print("\n")
    
path=os.path.join(path_city,"Sources_JSON")     # Defines the path for the JSON directory
if not os.path.exists(path):    # If the JSON directory does not exist, it creates it
    os.makedirs(path)
    print("Creation of JSON directory")
    print("\n")

path2=os.path.join(path_city,"Documents_sources")   # Defines the path for the directory of source documents
if not os.path.exists(path2):   # If the directory does not exist, it creates it
    os.makedirs(path2)
    print("Creation of Documents_sources directory")
    print("\n")

path3=os.path.join(path_city,"Documents_texte")     # Defines the path for the directory of text documents
if not os.path.exists(path3):   # If the directory does not exist, it creates it
    os.makedirs(path3)
    print("Creation of Documents_texte directory")
    print("\n")

with open("keywords.txt") as keywords_file:     # Open the keywords file and read the lines
    words = keywords_file.readlines()
    print("Reading keywords.txt ...")
    print("\n")
with open("types_documents.txt") as docs_file:  # Open the type of documents file and read the lines
    docs = docs_file.readlines()
    print("Reading types_documents.txt ...")
    print("\n")

for i in range(0, len(words)) : # Replacing characters that can cause issue once inserted in the URL
    words[i] = words[i].replace("\n","")
    words[i] = words[i].replace(" ", "%20")
    words[i] = words[i].replace("’", "%27")

for i in range(0, len(docs)) :  # Replacing characters that can cause issue once inserted in the URL
    docs[i] = docs[i].replace("\n","")
    docs[i] = docs[i].replace(" ", "%20")
    docs[i] = docs[i].replace("’", "%27")

for i in range(0,len(words),1):     # Iterate on the keywords list
    for j in range(0, len(docs),1):     # Iterate on the type of documents
        f = open(os.path.join(path,'out' + str(i) + "-" + str(j) + '.json'),'w+')     # Open a JSON file
        query = city + "%20" + words[i] + "%20" + docs[j]     # Modeling the query
        print("Query : " + query)
        if (cpt_query<100):     # Checking that the number of queries is not exceeded
            response = urllib2.urlopen("https://www.googleapis.com/customsearch/v1?key="+key+"&cx="+cx+"&q="+query)     # Open the URL from the API
            cpt_query = cpt_query+1     # Incrementation of the number of query
            # Printing the results in the JSON file
            html = response.read()
            f.write(html)
            f.close()
            print("JSON file created")
            print("\n")
            res=open(os.path.join(path_city,'resume'+date+'.txt'), 'a')     # Opening text file for the search report
            
            print("Processing new query:" + str(words[i]) + " + " + str(docs[j]))
            print("\n")
            with open(os.path.join(path,'out'+str(i)+"-"+str(j)+'.json')) as data_file:     # Reading the results from JSON file
                data1=json.load(data_file)
                rq = data1['queries']['request'][0]['searchTerms']      # Retrieving keywords of the query and writing it in the report
                res.write("################################################ \n")
                res.write("#############   Nouvelle requete   ############# \n")
                res.write("################################################ \n")
                res.write("\n")
                res.write("Mots clés de la requete : "+rq.encode('utf-8')+"\n")
                total_res = int(data1['queries']['request'][0]['totalResults'])     # Retrieving total number of results
                res.write("Nombre total de résultats : "+str(total_res)+"\n")
            if (total_res>10):  # If the number of results is bigger than 10, we display the 10 first results else we display all the results
                nb_result = 10
            else:
                nb_result = total_res
            res.write("Nombre de resultats affichés : "+str(nb_result)+"\n")
            res.write("\nListe des résultats\n")
            res.write("\n")

            for k in range (0, nb_result):  # Iterating on the number of results displayed to get the details of each of them
                url = data1['items'][k]['link']
                docName = data1['items'][k]['title']
                docName = docName.replace("\"", "_")
                docName = docName.replace("/", "_")
                docName = docName.replace(" ", "_")
                docName = docName.replace("<", "_")
                docName = docName.replace(">", "_")
                docName = docName.replace(":", "_")
                docName = docName.replace("|", "_")
                docName = docName.replace("\"", "_")
                docName = docName.replace("?", "_")
                docName = docName.replace("*", "_")
                snippet = data1['items'][k]['snippet']
                displayLink = data1['items'][k]['displayLink']
                displayLink = displayLink.replace("\"", "_")
                displayLink = displayLink.replace("/", "_")
                displayLink = displayLink.replace(" ", "_")
                displayLink = displayLink.replace("<", "_")
                displayLink = displayLink.replace(">", "_")
                displayLink = displayLink.replace(":", "_")
                displayLink = displayLink.replace("|", "_")
                displayLink = displayLink.replace("\"", "_")
                displayLink = displayLink.replace("?", "_")
                displayLink = displayLink.replace("*", "_")
                print(url)
                print(docName)
                res.write("URL : "+url+"\n")
                res.write("Nom : "+docName.encode('utf-8')+"\n")
                res.write("Résumé : "+snippet.encode('utf-8')+"\n")

                fileExtension = os.path.splitext(url)   # Splitting the URL to get the file format then writing it in the report 
                if ('fileFormat' in data1['items'][k]):
                    file_format = ".pdf"
                    res.write("Format : .pdf\n")
                elif (".pdf" in fileExtension[1] or ".PDF" in fileExtension[1] or ".php" in fileExtension[1]
                        or ".htm" in fileExtension[1] or ".asp" in fileExtension[1]):
                    file_format = fileExtension[1]
                    res.write("Format : "+fileExtension[1].encode('utf-8')+"\n")
                else:
                    file_format = "non renseigné"
                    res.write("Format : non renseigné\n")

                if (".pdf" in file_format or".PDF" in file_format):  # If it is a PDF we check if there is creation and modification date in the JSON doc then we write it in the report
                    if ('pagemap' in data1['items'][k]):
                        if ('creationdate' in data1['items'][k]['pagemap']['metatags'][0]):
                            creation_date=data1['items'][k]['pagemap']['metatags'][0]['creationdate']
                            if (creation_date.startswith("D:")):
                                creation_date=creation_date.replace('+', ':')
                                creation_date=creation_date.replace('Z', ':')
                                creation_date=creation_date.split(":")
                                creation_date=creation_date[1]
                                date_split=[creation_date[l:l+2] for l in range(0, len(creation_date), 2)]
                                try:
                                    creation_date=date_split[3]+"-"+date_split[2]+"-"+date_split[0]+date_split[1]
                                except:
                                    creation_date="Inconnu"
                                try:
                                    creation_hour=date_split[4]+":"+date_split[5]+":"+date_split[6]
                                except:
                                    creation_hour=" "
                                res.write("Date et heure de création : "+creation_date.encode("utf-8")+" "+creation_hour.encode("utf-8")+"\n")

                        if ('moddate' in data1['items'][k]['pagemap']['metatags'][0]):
                            modif_date=data1['items'][k]['pagemap']['metatags'][0]['moddate']
                            if (modif_date.startswith("D:")):
                                modif_date=modif_date.replace('+', ':')
                                modif_date=modif_date.replace('Z', ':')
                                modif_date=modif_date.split(":")
                                modif_date=modif_date[1]
                                date_split=[modif_date[l:l+2] for l in range(0, len(modif_date), 2)]
                                try:
                                    modif_date=date_split[3]+"-"+date_split[2]+"-"+date_split[0]+date_split[1]
                                except:
                                    modif_date="Inconnu"
                                try:
                                    modif_hour=date_split[4]+":"+date_split[5]+":"+date_split[6]
                                except:
                                    modif_hour=" "
                                res.write("Date et heure de modification : "+modif_date.encode("utf-8")+" "+modif_hour.encode("utf-8")+"\n")
                            
                res.write("\n")
                print(file_format)
                print(" ")

                if (".pdf" in file_format or".PDF" in file_format):     # If it is a PDF we retrieve the document and convert it into text
                    ctx=ssl.create_default_context()
                    ctx.check_hostname=False
                    ctx.verify_mode=ssl.CERT_NONE
                    testfile=urllib.FancyURLopener(context=ctx)
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".pdf"))):
                        testfile.retrieve(url,os.path.join(path2,"["+displayLink+"]"+docName+".pdf"))
                        path_to_pdf=os.path.join(path2,"["+displayLink+"]"+docName+".pdf")
                        print("PDF document saved")
                        print("Converting into text...")
                        try:
                            text=convert_pdf_to_txt(path_to_pdf)
                        except:
                            text=None
                        if text is not None:
                            f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                            f.write(text)
                            f.close
                            print("PDF document converted into text")
                            print("\n")
                    
                    
                if (".html" in file_format or ".htm" in file_format or ".asp" in file_format or ".aspx" in file_format): # If it is a html or asp we retrieve the document and convert it into text
                    h=html2text.HTML2Text()
                    html = urllib.urlopen(url).read()
                    html=html.decode("UTF-8","ignore")
                    html=html.encode("UTF-8","ignore")
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".html"))):
                        page=open(os.path.join(path2,"["+displayLink+"]"+docName+".html"),"w+")
                        page.write(html)
                        page.close()
                        print("Document saved")
                        result = h.handle(html.decode('utf-8'))
                        f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                        f.write(result.encode('utf-8'))
                        f.close()
                        print("Document converted into text")
                        print("\n")

                if (".php" in file_format): # Same for php
                    h=html2text.HTML2Text()
                    html = urllib.urlopen(url).read()
                    html=html.decode("UTF-8","ignore")
                    html=html.encode("UTF-8","ignore")
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".php"))):
                        page=open(os.path.join(path2,"["+displayLink+"]"+docName+".php"),"w+")
                        page.write(html)
                        page.close()
                        print("Document saved")
                        result = h.handle(html.decode('utf-8'))
                        f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                        f.write(result.encode('utf-8'))
                        f.close()
                        print("Document converted into text")
                        print("\n")
            res.close()

        else:
            print(str(datetime.now()) + ": Number limit of queries reached. Please wait 24 hours before the program restarts ...")
            tomorrow=datetime.now() + timedelta(hours=24)
            while datetime.now()<tomorrow:
                time.sleep(1)
            print(str(datetime.now()) + ": Number of queries back to 0. Restart of the program ...")
            print("\n")
            cpt_query=0
            response = urllib2.urlopen("https://www.googleapis.com/customsearch/v1?key="+key+"&cx="+cx+"&q="+query)     # Open the URL from the API
            cpt_query = cpt_query+1     # Incrementation of the number of query
            # Printing the results in the JSON file
            html = response.read()
            f.write(html)
            f.close()
            print("JSON file created")
            res=open(os.path.join(path_city,'resume'+date+'.txt'), 'a')     # Opening text file for the search report
            
            print("Processing new query:" + str(words[i]) + " + " + str(docs[j]))
            print("\n")
            with open(os.path.join(path,'out'+str(i)+"-"+str(j)+'.json')) as data_file:     # Reading the results from JSON file
                data1=json.load(data_file)
                rq = data1['queries']['request'][0]['searchTerms']      # Retrieving keywords of the query and writing it in the report
                res.write("################################################ \n")
                res.write("#############   Nouvelle requete   ############# \n")
                res.write("################################################ \n")
                res.write("\n")
                res.write("Mots clés de la requete : "+rq.encode('utf-8')+"\n")
                total_res = int(data1['queries']['request'][0]['totalResults'])     # Retrieving total number of results
                res.write("Nombre total de résultats : "+str(total_res)+"\n")
            if (total_res>10):  # If the number of results is bigger than 10, we display the 10 first results else we display all the results
                nb_result = 10
            else:
                nb_result = total_res
            res.write("Nombre de resultats affichés : "+str(nb_result)+"\n")
            res.write("\nListe des résultats\n")
            res.write("\n")

            for k in range (0, nb_result):  # Iterating over the number of results displayed to get the details of each of them
                url = data1['items'][k]['link']
                docName = data1['items'][k]['title']
                docName = docName.replace("\"", "_")
                docName = docName.replace("/", "_")
                docName = docName.replace(" ", "_")
                docName = docName.replace("<", "_")
                docName = docName.replace(">", "_")
                docName = docName.replace(":", "_")
                docName = docName.replace("|", "_")
                docName = docName.replace("\"", "_")
                docName = docName.replace("?", "_")
                docName = docName.replace("*", "_")
                snippet = data1['items'][k]['snippet']
                displayLink = data1['items'][k]['displayLink']
                displayLink = displayLink.replace("\"", "_")
                displayLink = displayLink.replace("/", "_")
                displayLink = displayLink.replace(" ", "_")
                displayLink = displayLink.replace("<", "_")
                displayLink = displayLink.replace(">", "_")
                displayLink = displayLink.replace(":", "_")
                displayLink = displayLink.replace("|", "_")
                displayLink = displayLink.replace("\"", "_")
                displayLink = displayLink.replace("?", "_")
                displayLink = displayLink.replace("*", "_")
                print(url)
                print(docName)
                res.write("URL : "+url+"\n")
                res.write("Nom : "+docName.encode('utf-8')+"\n")
                res.write("Résumé : "+snippet.encode('utf-8')+"\n")

                fileExtension = os.path.splitext(url)   # Splitting the URL to get the file format then writing it in the report 
                if ('fileFormat' in data1['items'][k]):
                    file_format = ".pdf"
                    res.write("Format : .pdf\n")
                elif (".pdf" in fileExtension[1] or ".PDF" in fileExtension[1] or ".php" in fileExtension[1]
                        or ".htm" in fileExtension[1] or ".asp" in fileExtension[1]):
                    file_format = fileExtension[1]
                    res.write("Format : "+fileExtension[1].encode('utf-8')+"\n")
                else:
                    file_format = "non renseigné"
                    res.write("Format : non renseigné\n")

                if (".pdf" in file_format or".PDF" in file_format):  # If it is a PDF we check if there is creation and modification date in the JSON doc then we write it in the report
                    if ('pagemap' in data1['items'][k]):
                        if ('creationdate' in data1['items'][k]['pagemap']['metatags'][0]):
                            creation_date=data1['items'][k]['pagemap']['metatags'][0]['creationdate']
                            if (creation_date.startswith("D:")):
                                creation_date=creation_date.replace('+', ':')
                                creation_date=creation_date.replace('Z', ':')
                                creation_date=creation_date.split(":")
                                creation_date=creation_date[1]
                                date_split=[creation_date[l:l+2] for l in range(0, len(creation_date), 2)]
                                try:
                                    creation_date=date_split[3]+"-"+date_split[2]+"-"+date_split[0]+date_split[1]
                                except:
                                    creation_date="Inconnu"
                                try:
                                    creation_hour=date_split[4]+":"+date_split[5]+":"+date_split[6]
                                except:
                                    creation_hour=" "
                                res.write("Date et heure de création : "+creation_date.encode("utf-8")+" "+creation_hour.encode("utf-8")+"\n")

                        if ('moddate' in data1['items'][k]['pagemap']['metatags'][0]):
                            modif_date=data1['items'][k]['pagemap']['metatags'][0]['moddate']
                            if (modif_date.startswith("D:")):
                                modif_date=modif_date.replace('+', ':')
                                modif_date=modif_date.replace('Z', ':')
                                modif_date=modif_date.split(":")
                                modif_date=modif_date[1]
                                date_split=[modif_date[l:l+2] for l in range(0, len(modif_date), 2)]
                                try:
                                    modif_date=date_split[3]+"-"+date_split[2]+"-"+date_split[0]+date_split[1]
                                except:
                                    modif_date="Inconnu"
                                try:
                                    modif_hour=date_split[4]+":"+date_split[5]+":"+date_split[6]
                                except:
                                    modif_hour=" "
                                res.write("Date et heure de modification : "+modif_date.encode("utf-8")+" "+modif_hour.encode("utf-8")+"\n")
                            
                res.write("\n")
                print(file_format)
                print(" ")

                if (".pdf" in file_format or".PDF" in file_format):     # If it is a PDF we retrieve the document and convert it into text
                    ctx=ssl.create_default_context()
                    ctx.check_hostname=False
                    ctx.verify_mode=ssl.CERT_NONE
                    testfile=urllib.FancyURLopener(context=ctx)
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".pdf"))):
                        testfile.retrieve(url,os.path.join(path2,"["+displayLink+"]"+docName+".pdf"))
                        path_to_pdf=os.path.join(path2,"["+displayLink+"]"+docName+".pdf")
                        print("PDF document saved")
                        print("Converting into text...")
                        try:
                            text=convert_pdf_to_txt(path_to_pdf)
                        except:
                            text=None
                        if text is not None:
                            f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                            f.write(text)
                            f.close
                            print("PDF document converted into text")
                            print("\n")
                    
                    
                if (".html" in file_format or ".htm" in file_format or ".asp" in file_format or ".aspx" in file_format): # If it is a html or asp we retrieve the document and convert it into text
                    h=html2text.HTML2Text()
                    html = urllib.urlopen(url).read()
                    html=html.decode("UTF-8","ignore")
                    html=html.encode("UTF-8","ignore")
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".html"))):
                        page=open(os.path.join(path2,"["+displayLink+"]"+docName+".html"),"w+")
                        page.write(html)
                        page.close()
                        print("Document saved")
                        result = h.handle(html.decode('utf-8'))
                        f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                        f.write(result.encode('utf-8'))
                        f.close()
                        print("Document converted into text")
                        print("\n")

                if (".php" in file_format): # Same for php
                    h=html2text.HTML2Text()
                    html = urllib.urlopen(url).read()
                    html=html.decode("UTF-8","ignore")
                    html=html.encode("UTF-8","ignore")
                    if not (os.path.isfile(os.path.join(path2,"["+displayLink+"]"+docName+".php"))):
                        page=open(os.path.join(path2,"["+displayLink+"]"+docName+".php"),"w+")
                        page.write(html)
                        page.close()
                        print("Document saved")
                        result = h.handle(html.decode('utf-8'))
                        f=open(os.path.join(path3,"["+displayLink+"]"+docName+".txt"),"w+")
                        f.write(result.encode('utf-8'))
                        f.close()
                        print("Document converted into text")
                        print("\n")
            res.close()



# When the program is over, send email with the report attached
fromaddr = "your.address@gmail.com" # YOUR ADDRESS
toaddr = "your.address@gmail.com" # EMAIL ADDRESS YOU SEND TO
 
msg = MIMEMultipart()
 
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "[Projet Cart'Eaux] - Fin du programme !" # SUBJECT OF THE EMAIL
 
body = "Execution du programme terminée, vous pouvez trouvez un compte rendu en pièce jointe." # TEXT YOU WANT TO SEND
 
msg.attach(MIMEText(body, 'plain'))
 
filename = 'resume'+date+'.txt' # NAME OF THE ATTACHED FILE WITH ITS EXTENSION
attachment = open(os.path.join(path_city,'resume'+date+'.txt'), "rb") # open("PATH OF THE FILE", "rb")
 
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
msg.attach(part)
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "PASSWORD") # server.login(fromaddr, "PASSWORD OF YOUR EMAIL ACCOUNT")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()

print("Fin de l'execution du programme ! Un email vient de vous etre envoyé")
