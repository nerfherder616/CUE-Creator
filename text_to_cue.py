#!/usr/bin/env python3

"""
@author nerfherder616
@date September, 2022
text_to_cue.py
Convert a text file exported from MediaInfo into a CUE sheet for m4b chapters.
"""

from sys import argv

def read_data(in_filename):
    """ Goes through the MediaInfo file and creates a CUE sheet for any
    title that has two sets of chapters. Always uses the second set. """
    with open(in_filename) as in_file:
        read_mode = False
        chap_data = []
        title = ""
        for line in in_file:
            if line.startswith("Complete name"):
                title = line.split("\\")[-1] #the filename you gave to MediaInfo
                title = title[:-5] #remove the '.m4b'
            if len(line) == 1 and read_mode:
                write_cue(chap_data, title)
                read_mode = False #we have all the chapters for this book
                chap_data = []
            if read_mode:
                chap_data.append(line)
            if line.startswith("Menu #2"):
                read_mode = True #the lines below this are the chapter info

def write_cue(chap_data, cue_filename):
    """ Creates the CUE sheet from the chapter data supplied """
    parsed_data = parse_chap_data(chap_data)
    with open(cue_filename + ".cue", "w") as cue:
        cue.write('FILE "' + cue_filename + '.m4b" WAVE\n') #first line of file
        for i in range(len(parsed_data)):
            cue.write("  TRACK " + str(i+1).rjust(2,"0") + " AUDIO\n") #track heading
            cue.write('    TITLE "' + parsed_data[i][0] + '"\n') #title
            cue.write("    INDEX 01 " + parsed_data[i][1] + "\n") #timestamp


def parse_chap_data(chap_data):
    """ Converts the time and title data into a format used by CUE sheets """
    parsed_data = [] #a list of tuples, each having the title and timestamp of a chapter
    for line in chap_data:
        time_stamp = convert_time_format(line[:12]) #the first 12 characters are the timestamp
        _, title = line[12:].split(": ", 1) #removing whitespaces and a colon before the title
        parsed_data.append((title[:-1], time_stamp)) #remove the newline character from title
    return parsed_data

def convert_time_format(time_stamp):
    """ MediaInfo exports chapter time stamps in HH:MM:SS format. A CUE sheet
    needs that info in MM:SS:FF format where FF is frames (75 frames/second). """
    hh, mm, ss = time_stamp.split(":")
    mm = str(int(hh) * 60 + int(mm)).rjust(2,"0") #combine hours into minutes
    ss, ms = ss.split(".")
    ff = str(round(int(ms) * .075)).rjust(2,"0") #convert milliseconds to frames
    return mm + ":" + ss + ":" + ff

def main():
    """ Main function that drives the program. """
    read_data(argv[1])

def usage():
    print('usage: python3 text_to_cue.py <input text file>')

if __name__ == '__main__':
   if len(argv) == 2:
      main()
   else:
      usage()
