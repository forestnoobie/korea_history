import pymupdf

doc = pymupdf.open("../data/temp.png") # open a document
pdf_bytes = doc.convert_to_pdf()
pdf_doc = pymupdf.open("pdf", pdf_bytes)
out = open("output.txt", "wb") # create a text output
for page in pdf_doc: # iterate the document pages
    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
    out.write(text) # write text of page
    print(text)
    out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
out.close()



### 한국어 인식x