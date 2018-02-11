import os
import argparse
import datetime
import math
import heapq

def get_filepaths():
    '''
    Reads command line argument for input/output filepaths

    Parameters:
        None

    Returns:
        input filepath (string)
        output filepath (string)
        percentile filepath (string)
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('itcont')
    parser.add_argument('percentile')
    parser.add_argument('output')
    args = parser.parse_args()

    return args.itcont, args.output, args.percentile

def parse_itcont(itcont_raw):
    '''
    Parses each line of itcont.txt and returns useful information
    Raises ValueError if data is malformed

    Parameters:
        itcont_raw (string): raw input line from itcont.txt 

    Returns:
        cmtd_id (string)
        name (string)
        zip_code (string)
        year (int)
        trans_amount (float)
    '''
    itcont = itcont_raw.split('|')

    if itcont[15]:
        raise ValueError('OTHER_ID field contains value')

    cmtd_id = itcont[0]
    name = itcont[7]
    year = get_year(itcont[13])
    zip_code = get_zip_code(itcont[10])

    try:
        trans_amount = int(round(float(itcont[14])))
    except:
        raise ValueError('Transaction Amount is malformed')

    if not cmtd_id:
        raise ValueError('CMTD ID field does not contain any value')
    if not name:
        raise ValueError('Name field does not contain any value')

    return cmtd_id, name, zip_code, year, trans_amount

def get_zip_code(zip_code):
    '''
    Verifies if zip code has more than 5 digits and returns the 5-digit zip code
    Raises ValueError if zip_code is malformed

    Parameters:
        zip_code (string): raw string of zip code from itcont.txt

    Return:
        5-digit zip code (string)
    '''
    if (len(zip_code) < 5) or (not zip_code.isdigit()):
        raise ValueError('Invalid zip code')
    else:
        return zip_code[0:5]

def get_year(date):
    '''
    Verifies if date is well-formed and returns the year
    Raises ValueError if date is malformed

    Parameters:
        date (string): raw string of date from itcont.txt

    Returns:
        year (int)
    '''
    try:
        month = date[0:2]
        day = date[2:4]
        year = date[4:8]
        date = datetime.datetime(year = int(year), month = int(month), day = int(day))

        return date.year
    except (ValueError, IndexError):
        raise ValueError('Invalid transaction date')

def update_repeat_donation(percentile, repeat_donation, trans_amount):
    '''
    Updates information about contributions received by recipient from the 
    contributor's zip code streamed in so far in this calendar year
     and computes donation amount in a given percentile using the nearest-rank method

     Parameters:
         percentile (float): percentile to compute
         repeat_donation (dict): { 'total_amount': total amount of contributions from repeat donors (float),
                                   'num_trans': total number of transactions from repeat donors (int),
                                   'max_heap': contains the smallest n% of transaction amounts (heapq)
                                                 i.e.: largest value in max_heap is n-th percentile value
                                   'min_heap': contains the rest of the transaction amounts (heapq) }
         trans_amount (float): transaction amount of new contribution from a repeat donor

     Returns:
         None
     '''
    repeat_donation['total_amount'] += trans_amount
    repeat_donation['num_trans'] += 1

    # computes the ordinal rank of n-th percentile value
    ordinal_rank = int( math.ceil(percentile/100. * repeat_donation['num_trans'] ) )

    max_heap = repeat_donation['max_heap']
    min_heap = repeat_donation['min_heap']

    if(trans_amount <= -(max_heap[0])):
        heapq.heappush(max_heap, -trans_amount)
    else:
        heapq.heappush(min_heap, trans_amount)

    if(len(max_heap) > ordinal_rank):        # max_heap contains more than n% of elements
        temp = -heapq.heappop(max_heap)        # removes the largest value in max_heap and adds to min_heap
        heapq.heappush(min_heap, temp)

    if(len(max_heap) < ordinal_rank):        # max_heap contains fewer than n% of elements
        temp = heapq.heappop(min_heap)        # removes the smallest value in min_heap and adds to max_heap
        heapq.heappush(max_heap, -temp)

def get_repeat_donation_stats(repeat_donation):
    '''
    Returns repeat donation statistics for output

     Parameters:
         repeat_donation (dict): { 'total_amount': total amount of contributions from repeat donors (float),
                                   'num_trans': total number of transactions from repeat donors (int),
                                   'max_heap': contains the smallest n% of transaction amounts (heapq)
                                                 i.e.: largest value in max_heap is n-th percentile value
                                   'min_heap': contains the rest of the transaction amounts (heapq) }

     Returns:
         total contribution amount (int)
         total number of transactions (int)
         percentile value (int)
     '''
    total_amount = repeat_donation['total_amount']
    number_of_transactions = repeat_donation['num_trans']
    percentile_value = -(repeat_donation['max_heap'][0])    # largest value in max_heap is the n-th percentile value

    return total_amount, number_of_transactions, percentile_value


if __name__ == "__main__":
    itcont_filepath, output_filepath, percentile_filepath = get_filepaths()

    with open(percentile_filepath) as f:
        percentile = float(f.readline())

    repeat_donors_dict = {}        # key: (name, zip_code); value: year of contribution.
    repeat_donations_dict = {}        # key: (cmtd_id, zip_code, year); value: contribution info

    with open(itcont_filepath, 'r') as input_file, open(output_filepath, 'w') as output_file:
        itcont_raw = input_file.readline()

        while(itcont_raw):    # if new line of itcont.txt is not empty

            try:
                cmtd_id, name, zip_code, year, amount = parse_itcont(itcont_raw)

                if (name, zip_code) in repeat_donors_dict:    # this donor is a repeated donor

                    if year >= repeat_donors_dict[(name, zip_code)]:    # skips the record if transaction date is for a previous calendar year

                        if (cmtd_id, zip_code, year) in repeat_donations_dict:
                            update_repeat_donation(percentile, repeat_donations_dict[(cmtd_id, zip_code, year)], amount)
                        else:
                            # creates a new repeat donation record
                            max_heap = [-amount]    # uses the negative value because heapq only supports min-heap. 
                            min_heap = []
                            heapq.heapify(max_heap)
                            heapq.heapify(min_heap)
                            repeat_donations_dict[(cmtd_id, zip_code, year)] = {'max_heap': max_heap, 
                                                                                'min_heap': min_heap, 
                                                                                'total_amount':amount, 
                                                                                'num_trans': 1}

                        total_amount, number_of_transactions, percentile_value \
                            = get_repeat_donation_stats(repeat_donations_dict[(cmtd_id, zip_code, year)])

                        # Writes to output file
                        output_file.write('{}|{}|{}|{}|{}|{}\n'.format(cmtd_id, zip_code, year, 
                                                                        percentile_value, total_amount, number_of_transactions))
                else:
                    # adds donor to repeat_donors_dict
                    repeat_donors_dict[(name, zip_code)] = year

            except ValueError:    # If record is malformed, ignore and skip the record
                pass

            itcont_raw = input_file.readline()    # reads new line from itcont.txt


