import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def parseTabular():
    chapters = []
    try:
        tree = ET.parse('load/Tabular.xml')
        root = tree.getroot()
        for chapter in root.findall('chapter'):
            chapter_doc = {}
            name = chapter.find('name')
            desc = chapter.find('desc')
            chapter_doc['_id'] = name.text
            chapter_doc['desc'] = desc.text
            for include_notes in chapter.findall('includes'):
                chapter_includes = []
                for notes in include_notes.findall('note'):
                    include_note = {}
                    note = notes.text
                    include_note['text'] = note
                    chapter_includes.append(include_note)
                chapter_doc['includes'] = chapter_includes
            for addCodeNotes in chapter.findall('useAdditionalCode'):
                chapter_addCode_notes = []
                for useAdd in addCodeNotes.findall('note'):
                    useAdditionalCodes = {}
                    useAdditionalCodes['text'] = useAdd.text
                    chapter_addCode_notes.append(useAdditionalCodes)
                chapter_doc['useAdditionalCode'] = chapter_addCode_notes
            for exc1_notes in chapter.findall('excludes1'):
                chapter_excl1 = []
                for exclude1 in exc1_notes.findall('note'):
                    exclude1_note = {}
                    exclude1_note['text'] = exclude1.text
                    chapter_excl1.append(exclude1_note)
                chapter_doc['excludes1'] = chapter_excl1
            for exc2_notes in chapter.findall('excludes2'):
                chapter_excl2 = []
                for exclude2 in exc2_notes.findall('note'):
                    exclude2_note = {}
                    exclude2_note['text'] = exclude2.text
                    chapter_excl2.append(exclude2_note)
                chapter_doc['excludes2'] = chapter_excl2
            chapter_sections = []
            for section in chapter.findall('section'):
                chapter_section = {}
                section_desc = section.find('desc').text
                chapter_section['section_desc'] = section_desc
                parent_diags = []
                for parent_diag in section.findall('diag'):
                    parent_diag_info = {}
                    parent_diag_code = parent_diag.find('name').text
                    parent_diag_info['parent_code'] = parent_diag_code
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
                    parent_diags.append(parent_diag_info)
                chapter_section['diags'] = parent_diags
                chapter_sections.append(chapter_section)
            chapter_doc['sections'] = chapter_sections
            chapters.append(chapter_doc)
        return chapters
    except ParseError as parseErr:
        print("Unable to parse Tabular.xml: {0}".format(parseErr))
        sys.exit(0)


def loadMongo(chapter_docs):
    try:
        client = MongoClient('mongodb://localhost:27017/',
                             serverSelectionTimeoutMS=100)
        db = client['icd10']
        col = db['ICD2016']
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
    load_chapters = parseTabular()
    print('Parsed {0} chapters'.format(len(load_chapters)))
    print('Loading Chapters into DB')
    loaded_chapters = loadMongo(load_chapters)
    print('Loaded {0} chapters into the DB'.format(loaded_chapters))
