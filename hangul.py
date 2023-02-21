import tika
from tika import parser
from disaster_detection import get_disasters
from collections import Counter
from get_file_metadata import extract_metadata
from location_detection import detected_potential_countries,pretty_print_dict
from report_type import detect_report_type
import spacy


nlp = spacy.load('en_core_web_sm')


# def eextract_metadata(pdf_metadata):
#     metadata_final = {}
#     for my_key, my_value in pdf_metadata.items():
#         if my_key in ['Author', 'creator']:
#             metadata_final['Author'] = my_value
#         elif my_key in ['xmpTPg:NPages']:
#             metadata_final['No.of Pages'] = my_value
#         elif my_key in ['resourceName']:
#             metadata_final['Document Title'] = my_value.replace(
#                 "b'", '').replace(".pdf'", "")  # create contenders for titles
#         elif my_key in ['Keywords', 'subject']:
#             metadata_final['Subject'] = my_value
#         elif my_key in ['dc:title', 'title']:
#             metadata_final[my_key] = my_value
#         elif my_key in ['Content-Type', 'Creation-Date', 'producer']:
#             metadata_final[my_key] = my_value
#         elif my_key in ['pdf:charsPerPage']:
#             metadata_final['charsPerPage'] = my_value
#         else:
#         	metadata_final[my_key] = my_value
#     return metadata_final

def get_doc_title(pages_as_list, metadata):
    from statistics import median
    # from textblob import TextBlob
    char_per_page_list = list(map(int, metadata['charsPerPage'][:3]))
    mi = min(char_per_page_list)
    indexes = [index for index in range(len(char_per_page_list)) if char_per_page_list[index] == mi]
    # textBlb = TextBlob(pages_as_list[indexes[0]])            # Making our first textblob
    # textCorrected = textBlb.correct()

    print('doc title')
    print(pages_as_list[indexes[0]], indexes)
    # print(textCorrected)

def get_doc_summary(pages_as_list, metadata):
    from statistics import median
    # from textblob import TextBlob
    char_per_page_list = list(map(int, metadata['charsPerPage'][:4]))
    mi = min(char_per_page_list)
    indexes = [index for index in range(len(char_per_page_list)) if char_per_page_list[index] > mi]
    # textBlb = TextBlob(pages_as_list[indexes[0]])            # Making our first textblob
    # textCorrected = textBlb.correct()

    #go over content in the pages and check for the word summary, message from president
    for i in indexes:
    	if 'Message From' in pages_as_list[i]:
    		print('doc summary')
    		print(pages_as_list[i])

    # print('doc title')
    # print(pages_as_list[indexes[0]])
    # print(textCorrected)
	
# def extract_pdf_content(pdf_path,content_as_pages):
# 	'''extracts the the content pas pages or as full blog of text'''
# 	if content_as_pages:
# 		raw_xml = parser.from_file(pdf_path, xmlContent=True)
# 		body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
# 		body_without_tag = body.replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>","\n").replace("<p />","\n")
# 		text_pages = body_without_tag.split("""<div class="page">""")[1:]
# 		num_pages = len(text_pages)
# 		print(num_pages)
# 		if num_pages==int(raw_xml['metadata']['xmpTPg:NPages']) : #check if it worked correctly
# 			for i in range(5):
# 			# for i in range(num_pages):
# 				print('page number: '+ str(i+1))
# 				print(text_pages[i].replace("\n", ""))
# 				print('\n')
# 		pdf_content = body_without_tag
# 	else:
# 		parsed_pdf = parser.from_file(pdf_path)
# 		# parsed_data_full = parser.from_file(pdf_path,xmlContent=True) 
# 		# parsed_data_full = parsed_data_full['content']
# 		# print(parsed_data_full)
# 		# print(parsed_pdf["content"])
# 		pdf_content= parsed_pdf["content"].replace("\n", "")
# 		# return parsed_pdf["content"]
# 	return pdf_content

def extract_pdf_content(pdf_path, content_as_pages):

    if content_as_pages:
        raw_xml = parser.from_file(pdf_path, xmlContent=True)
        body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
        # body_without_tag = body.replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>","\n").replace("<p />","\n")
        body_without_tag = body.replace("<p>", " ").replace("</p>", "\n").replace("<div>", " ").replace("</div>","\n").replace("<p />","\n")
        text_pages = body_without_tag.split("""<div class="page">""")[1:]
        num_pages = len(text_pages)
        # print(body_without_tag)
        # print(text_pages)
        print(num_pages)
        pages_content=[]
        if num_pages==int(raw_xml['metadata']['xmpTPg:NPages']) : #check if it worked correctly
            # for i in range(5):
            for i in range(num_pages):
            #     print('page number: '+ str(i+1))
            #     # print(text_pages[i])
            #     # print(text_pages[i].replace("\n", ""))
            #     print('\n')
                pages_content.append(text_pages[i].replace("\n", ""))
        # pdf_content = body_without_tag
        pdf_content = pages_content
        # pdf_content = text_pages
    else:
        parsed_pdf = parser.from_file(pdf_path)
        # parsed_data_full = parser.from_file(pdf_path,xmlContent=True) 
        # parsed_data_full = parsed_data_full['content']
        # print(parsed_data_full)
        # print(parsed_pdf["content"])
        pdf_content= parsed_pdf["content"].replace("\n", "")
        # return parsed_pdf["content"]
    return pdf_content



def extract_pdf_data(list_of_path_to_pdf, want_metadata=True, want_content=False, content_as_pages=True):
	'''Given a list of path to PDFs, iterate over the list,
	 and for each string, read in the PDF form its path and 
	 return extracted text.

	 The flags might be changed during further development. 
	 Right now they are designed to help in the process of 
	 development and debugging.
	 Developing what details about the document we want to 
	 look at closely - metadata or content or both.
	 It also returns content as pages so that we can decide 
	 which pages to target going forward for information.

	 @type list_of_path_to_pdf: list of string - [str1, str2]
	 @param list_of_path_to_pdf: path of the pdf file to be read
	 @type want_metadata: boolean
	 @param want_metadata: Gets metadata about a document - default value True
	 @type want_content: boolean
	 @param want_content: Gets all the content of the document - default value False
	 @type content_as_pages: boolean
	 @param content_as_pages: Gets the content of the documents as pages else as a single text blob- default value True
	 @rtype: List of dictionaries - [{metadata:'', 'content: ''}, {metadata:'', 'content: ''}, {metadata:'', 'content: ''}]
	 @return:  For each document we get its metadata or content or both

	'''
	data_of_pdfs = []
	for pdf_path in list_of_path_to_pdf:
		pdf={}
		parsed_pdf = parser.from_file(pdf_path)

		if want_metadata:
			extracted_pdf_metadata = extract_metadata(parsed_pdf["metadata"])
			pdf['metadata'] = extracted_pdf_metadata
			# print(extracted_pdf_metadata)

		if want_content:
			extracted_pdf_content = extract_pdf_content(pdf_path,content_as_pages)
			pdf['content'] = extracted_pdf_content

		data_of_pdfs.append(pdf)

	return data_of_pdfs

# def extract_summary(content,text):

# def detect_location(content):
# 	import spacy
# 	from collections import Counter
# 	nlp = spacy.load('en_core_web_sm')
# 	nlped = nlp(content)
# 	locations = [ (x.text.replace('\n', ''), x.label_) for x in nlped.ents if x.label_ == 'GPE']
# 	return (Counter(locations).most_common(2))

def detect_location(content):
    nlped = nlp(content)
	
    locations = [x.text.replace('\n', '').lower()
                 for x in nlped.ents if x.label_ == 'GPE']
    # most_common = [(x, z) for ((x, y), z) in Counter(locations).most_common()]
    most_common_location = Counter(locations).most_common(3)
    # return most_common_location
    return locations



def main():
	# Start running the tika service
	tika.initVM()
	# path_dir = '/Users/sidraeffendi/Documents/si699/project/'
	path_dir = '/Users/sidraeffendi/Documents/si699/project/annual/'
	filename =['Asylum-Access-Annual-Report-15-16_WEB_1','2019-Airlink-Annual-Report',
	'Annual_Report_2005', 'Annual-Report-2019-Final','HSS-Annual-Summary-Report-Payinjiar-County-2023_3', 
	'irex-annual-impact-report-2020', 'Watch List 2022 Autumn Update _ Crisis Group']
	# filename= ['1', 'SitRep-no-5_Libya_Tripoli-11-April', 'Asylum-Access-Annual-Report-15-16_WEB_1', 'Asia-RWR_FINAL','IPC_Zanzibar_Acute_FoodInsec_2022Oct2023May_Report']
	file_path = path_dir + filename[1] +'.pdf'
	# file_path ='/Users/sidraeffendi/Documents/si699/project/1.pdf'
	# file_path = '/Users/sidraeffendi/Documents/si699/project/SitRep-no-5_Libya_Tripoli-11-April.pdf'
	# text = extract_pdf_data(['/Users/sidraeffendi/Documents/si699/project/SitRep-no-5_Libya_Tripoli-11-April.pdf'])
	metadata_of_pdfs = extract_pdf_data([file_path],want_content=True,content_as_pages=True )

	# after I have the metadata , I need to make decision about what other info to extract and what 
	# metadata to show and what metadata to parse internally
	print('Metadata Extracted:')
	pretty_print_dict(metadata_of_pdfs[0]['metadata'])
	print('')
	# this link has comprehensive country names
	# https://stackoverflow.com/questions/41245330/check-if-a-country-entered-is-one-of-the-countries-of-the-world
	# this will make life way easier
	#detec location
	location =detect_location(('/n').join(metadata_of_pdfs[0]['content']))
	location_new =detected_potential_countries(('/n').join(metadata_of_pdfs[0]['content']))
	print('Initially detected locations:')
	print(location)
	print('Locations detected now:')
	print(location_new)


	disaster_types = get_disasters(('/n').join(metadata_of_pdfs[0]['content']))
	print('Different disaster types mentioned in the document:')
	print(disaster_types)

	doc_report_type = detect_report_type(metadata_of_pdfs[0]['metadata']['File name'])
	print('The Report type is:')
	print(doc_report_type)
	
	# # disasters = get_disasters(metadata_of_pdfs[0]['content'])
	# doc_title = get_doc_title(metadata_of_pdfs[0]['content'],metadata_of_pdfs[0]['metadata'])
	# get_doc_summary(metadata_of_pdfs[0]['content'],metadata_of_pdfs[0]['metadata'])
	# print(location, disasters, doc_title)
	# 	extract_summary(content,text)
	# 
	#separate the content and metadat and process accordingly
	# display the metadata
	#use the content for language detection



if __name__ == "__main__":
    main()

# class Hangul(object):
#     def __init__(self, filename):
#         self.file = open(filename)
#         tika.initVM()

#     def __enter__(self):
#         return self.file

#     def __exit__(self, ctx_type, ctx_value, ctx_traceback):
#         self.file.close()

# with Hangul('file') as f:
#     contents = f.read()


