import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def parseTabular():
    codes = []
    try:
        tree = ET.parse('load/Tabular.xml')
        root = tree.getroot()
        for chapter in root.findall('chapter'):
            for section in chapter.findall('section'):
                for parent_diag in section.findall('diag'):
                    parent_diag_info = {}
                    parent_diag_code = parent_diag.find('name').text
                    parent_diag_info['_id'] = parent_diag_code
                    parent_diag_desc = parent_diag.find('desc').text
                    parent_diag_info['parent_desc'] = parent_diag_desc
                    child_diags = []
                    for child_diag in parent_diag.findall('diag'):
                        child_diag_obj = {}
                        child_diag_code = child_diag.find('name').text
                        child_diag_obj['child_code'] = child_diag_code
                        child_diag_desc = child_diag.find('desc').text
                        child_diag_obj['child_desc'] = child_diag_desc
                        child_incl_terms = []
                        inclusion_terms = child_diag.findall('inclusionTerm')
                        for inclusionTerm in inclusion_terms:
                            inclusion_notes = inclusionTerm.findall('note')
                            for inclusion_text in inclusion_notes:
                                child_incl_text = {}
                                child_incl_text['text'] = inclusion_text.text
                                child_incl_terms.append(child_incl_text)
                        child_diag_obj['inclusionTerms'] = child_incl_terms
                        child_diags.append(child_diag_obj)
                    parent_diag_info['child_diags'] = child_diags
                    codes.append(parent_diag_info)
        return codes
    except ParseError as parseErr:
        print("Unable to parse Tabular.xml: {0}".format(parseErr))
        sys.exit(0)


def loadMongo(chapter_docs):
    try:
        client = MongoClient('mongodb://localhost:27017/',
                             serverSelectionTimeoutMS=100)
        db = client['icd10']
        col = db['icd2016Codes']
        for chapter in chapter_docs:
            col.insert_one(chapter)
        return col.count()
    except ConnectionFailure as connectError:
        print("Connection Failure to MongoDB: {0}".format(connectError))
        sys.exit(1)
    except ServerSelectionTimeoutError as timeoutErr:
        print("Unable to connect Timeout: {0}".format(timeoutErr))
        sys.exit(1)
    except Exception as err:
        print ("Error: {0}".format(err.args))


if __name__ == '__main__':
    print('Parsing Tabular.xml')
    load_codes = parseTabular()
    print('Parsed {0} codes'.format(len(load_codes)))
    print('Loading codes into DB')
    loaded_codes = loadMongo(load_codes)
    print('Loaded {0} codes into the DB'.format(loaded_codes))
