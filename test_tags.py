import boto3,json
import sys,argparse
#import pprint
#pp = pprint.PrettyPrinter(indent=4)
from yaml import safe_load, dump

#declaring api connection
client_tagging_api = boto3.client('resourcegroupstaggingapi', 'us-east-1')

def load_yaml(filename=None):
    '''loading data.yaml as python dictionary
    filename : it should be the filename that holds data in yaml
    data should be holding tags and their allowed values'''
    with open (filename) as data:
        global ref_data
        ref_data = safe_load(data)
        global ref_tagnames
        ref_tagnames = ref_data.keys()
        print(tuple(ref_tagnames))
        

all_tags=[]
rsrcs_with_missed_tags=[]
tag_results = []


def get_all_res():
    '''used to read the aws account to scan all resources
    it will return all resources with their corresponding tags'''
    response = client_tagging_api.get_resources()
    all_tags.extend(response['ResourceTagMappingList'])
    return all_tags

def dump_all_tags():
    '''this function is used to write all the tags extracted in get_all_res() method
    the data is dumped into all_tags.txt
    so this function is dependant on get_all_res function call'''
    with open('all_tags.txt','w') as file_dump:
        for each in all_tags:
            file_dump.write(str(each))
            file_dump.write('\n')



def tag_validation(each_reference_tag, all_tags={}):
    '''this function will validate every resource for a given tag, allowed values for all ARNs
    outputs are redirecto to arnswithouttags.txt for resources without tags
    every tag has a different output dump which holds resources missing that tag or with invalid value'''
    # print('function called',each_ref_tag)
    file= str(each_reference_tag)
    tag_not_found = []
    out_f1 = open('{}.log'.format(file), 'w')
    with open('arnswithouttags.txt','w') as out_f:
        for each in all_tags:
            # print(each,'this is each')
            if len(each['Tags'])==0:
                out_f.write('Tags are not found for :{} '.format(each['ResourceARN']))
                out_f.write('\n')
                print('Tags are not found for :{} '.format(each['ResourceARN']))
                
            #print(type(each['Tags']),each_reference_tag, 'debug1')
            available_tags = [every['Key'].lower() for every in each['Tags']]
            set_available_tags = set(available_tags)
            #print(set_available_tags,'debug5')
            set_ref_tagnames = set(ref_tagnames)
            #print(set_ref_tagnames,'debug 6')
            for every in each['Tags']:
                if each_reference_tag not in every.keys():
                    if each['ResourceARN'] not in rsrcs_with_missed_tags:
                        rsrcs_with_missed_tags.append(each['ResourceARN'])
                tag_value = ref_data.get(each_reference_tag)
                if every['Key']==each_reference_tag:
                    if every['Value'] not in tag_value:
                        #pass 
                        
                        temp = 'for the key : {} Found a different value for : {}'.format(each_reference_tag, each['ResourceARN'],every['Value'])
                        #out_f1.write('for the key : {} Found a different value for : {}'.format(each_reference_tag, each['ResourceARN'],every['Value']))
                        if temp not in tag_not_found:
                            tag_not_found.append(temp)
                            out_f1.write('\n')
                            print('for the key : {} Found a different value for : {}'.format(each_reference_tag, each['ResourceARN'],every['Value']))
                if set_available_tags.issubset(set_ref_tagnames):
                    deffered = set_ref_tagnames.difference(set_available_tags)
                    if each_reference_tag in deffered:
                    #pass 
                        temp1 = 'The key : {} is not found for : {}'.format(each_reference_tag, each['ResourceARN'])
                        if temp1 not in tag_not_found:
                            tag_not_found.append(temp1)
                            out_f1.write(temp1)
                            out_f1.write('\n')
                            #print(tag_not_found,'debug8')
                            print('the key : {} is not found for : {}'.format(each_reference_tag, each['ResourceARN']))
        out_f1.close()
def each_validation():
    ''' this function calls tag_validation for each tag that we extracted from get_all_res
    so this is dependant on get_all_res function call'''
    # print(all_tags,'hehe')
    for i in ref_tagnames:
        #if i not in ('environment','function','name','ops-owner','company-name','business-domain'):
        if 1 or i not in ('environment','function','name','ops-owner','company-name','business-domain'):
            tag_validation(i, all_tags=all_tags)

#load_yaml(filename='data.yaml')
#get_all_res()
#dump_all_tags()
#each_validation()
