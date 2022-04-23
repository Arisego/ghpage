# import markdownify
import markdownify
import sys
import os
from os import walk
  
def ConvertHtmlToMarkdown(InFileName):
    
    with open(InFileName, encoding='utf-8') as file_in:
        # create html
        html =  file_in.read()
        # convert html to markdown
        h = markdownify.markdownify(html, heading_style="ATX")
        #print(h)

        ts_RawFileName = os.path.splitext(InFileName)[0]
        print("ts_RawFileName: {0}".format(ts_RawFileName))

        text_file = open(ts_RawFileName+".markdown", "w")
        n = text_file.write(h)
        text_file.close()




def main(argv):

    TargetFile = '_posts/'

    td_file_cnt = 0
    for (dirpath, dirnames, filenames) in walk(TargetFile):
        for file in filenames:
            file_name, file_ext = os.path.splitext(file)
            if file_ext == '.html':
                ConvertHtmlToMarkdown(os.path.join(dirpath, file))

        dirnames.clear()    #不遍历子目录
    #TargetFile = '_posts/2021-11-16-note-of-video-by-jonastyroller.html'

    # if len(TargetFile) == 0:
    #     print("Bad target file")
    #     exit(9)

    # ConvertHtmlToMarkdown(TargetFile)


if __name__ == "__main__":
    print("==== Script start ====")
    main(sys.argv[1:])
    print("==== Script ends ====")