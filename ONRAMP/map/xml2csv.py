import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET

def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):  #读取xml文件
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df  #返回xml数据结果

def main():
    xml_df = xml_to_csv(xmlPath)
    xml_df.to_csv(savePath+'train.csv', index=None) #将xml结果保存于csv
    print('Successfully converted xml to csv.')

if __name__=='__main__':
    xmlPath = 'G:\RL code\ONRAMP\map\data'  #xml文件路径----修改第1处
    savePath = './' #保存路径文件夹-------修改第2处
    main()
#
# if __name__ == "__main__":
#     xml_path = 'G:\RL code\ONRAMP\map'  # 改为自己的xml文件所在文件夹路径
#     print(os.path.exists(xml_path))
#     xml_df = xml_to_csv(xml_path)
#     print('**********************************')
#     print(xml_df)
#     xml_df.to_csv('trajectory.csv', index=None)  # 改为自己csv存储路径
#     print('Successfully converted xml to csv.')