#coding: utf-8

import os
import io
import sys
import getopt
from xml.dom import minidom

class LocalStringsCreator:
    def usage(self):
        print("""
 Usage: -p [base_file] -i [ios_project_directory] -a [android_project_directory]
 
 See --help for more.
    """)

    def help(self):
        print("""
 -p  | --path\t\tПуть к базовому файлу .csv со всеми строчками
 -i  | --ios\t\tПуть к папке с проектом ios
 -a  | --android\tПуть к папке с проектом android
 -s  | --splitter\tПозволяет задать один из разделителей. Доступны следующие варианты:""")
        self.splitters_help()
        print("""
 -l  | --light\t\tГенерация всех языков в текущей папке с дефолтным сплиттером [;].
 -li | --light_ios\tГенерация всех языков только для ios в текущей папке с дефолтным сплиттером [;].
 -la | --light_android\tГенерация всех языков только для android в текущей папке с дефолтным сплиттером [;].
 -h  | --help\t\tСправка
 
 Usage: -p [base_file] -i [ios_project_directory] -a [android_project_directory] -s [splitter]
 
 or
 
 Usage: -p [base_file] -i [ios_project_directory]
 
 or
 
 Usage: -p [base_file] -a [android_project_directory]
    """)
    
    # вывод на экран сплиттеров в виде ключ-сплиттер (например, ": - colon")
    def splitters_help(self):
        indent = (' ' * len('-s  | --splitter'))
        for s in self.__splitters:
            if s[0] == 'tab':
                print("\t{}{}{}".format(indent, s[1], s[0]))
            else:
                print("\t{}{}\t{}".format(indent, s[1], s[0]))

    # дефолтные аргументы для --light сборки
    __base_file_path              = 'test_strings.csv'
    __ios_directory               = ''
    __android_directory           = ''
    __splitter                    = ';'

    # константы
    # число соответствует номеру столбца в базовом .csv
    __key_word    = 0
    __flag        = 1
    __languages = (('ru', 2),('en', 3),('fr', 4),('it', 5),('ge', 6),('sp', 7))
    __splitters = (('dot','.'),('pipe','|'),('comma',','),('tab','\t'),('colon',':'),('semicolon',';'))

    __list_with_ios_strings       = []
    __list_with_android_strings   = []
    
    # флаги, указывающие, для какой из платформ генерировать строки локализаций
    # по дефолту генерация для всех платформ отключена, включаются при парсинге аргументов
    __create_ios                  = 0
    __create_android              = 0
    
    # минимальное количество аргументов командной строки
    # первый аргумент всегда имя скрипта, далее путь и хотя бы одна комбинация ключ платформы + путь
    __minimal_number_of_arguments = 5
    
    # метод, устанавливающий сплиттер
    def set_splitter(self, splitter):
        for s in self.__splitters:
            if splitter == s[0]:
                self.__splitter = splitter
                return
            else:
                print("\nНекорректный сплиттер. Для того, чтобы увидеть список допустимых значений, введите --help.\nБыло установлено значение по-умолчанию: semicolon.")
                return
    
    # метод, считывающий инфу из общего файла и делящий строки на списки для ios и android платформ
    def split_base_file_on_language_lists(self):
        with io.open(self.__base_file_path, encoding='utf-8') as base_file:
            
            string_of_base_file = 'This is the start of reading the base file'
            string_of_base_file = base_file.readline()

            while string_of_base_file != '':
                split_string = string_of_base_file.split(self.__splitter)
                
                key_word = self.__key_word
                flag = self.__flag
                
                if split_string[key_word] != '':
                    if split_string[flag] == '' or split_string[flag] == 'ios':
                        self.__list_with_ios_strings.append(split_string)

                    if split_string[flag] == '' or split_string[flag] == 'android':
                        self.__list_with_android_strings.append(split_string)
                
                string_of_base_file = base_file.readline()

        base_file.closed

    # метод, создающий файлы локализаций для ios (.string)
    def create_ios_lproj(self, lang):
        ios_directory = self.__ios_directory
        ios_directory = os.path.dirname(ios_directory + '/' + lang[0] + '.lproj/')
        path = ios_directory + '/Localizable.strings'

        if not os.path.exists(ios_directory):
            os.mkdir(ios_directory)

        with io.open(path, 'w+', encoding='utf-8') as new_ios_file:
            for string in self.__list_with_ios_strings:
                word = string[lang[1]]
                new_ios_file.write('\"' + string[self.__key_word] + '\"=\"' + word.replace('\\x22','\\"') + '\";\n')

        new_ios_file.closed


    # метод, создающий файлы локализаций для android (.xml)
    def create_android_xml(self, lang):
        android_directory = self.__android_directory
        android_directory = os.path.dirname(android_directory + 'values-' + lang[0] + '/')
        path = android_directory + '/strings.xml'

        if not os.path.exists(android_directory):
            os.mkdir(android_directory)

        xml_doc = minidom.Document()

        root = xml_doc.createElement('resources')
        xml_doc.appendChild(root)

        for string in self.__list_with_android_strings:
            attr = string[self.__key_word]
            text = string[lang[1]].replace('\\x22','\\u0022')

            str_node = xml_doc.createElement('string')
            str_node.setAttribute('name', attr)
            str_node.appendChild(xml_doc.createTextNode(text))
            root.appendChild(str_node)

        xml_doc = xml_doc.toprettyxml(indent="  ")

        with io.open(path, 'w+', encoding='utf-8') as new_android_file:
            new_android_file.write(xml_doc)

    # метод, парсящий аргументы командной строки
    def set_arguments(self):

        if len(sys.argv) < 2:
            self.usage()
            return 0
        elif sys.argv[1] in ('-h', '--help'):
            self.help()
            return 0
        elif len(sys.argv) < self.__minimal_number_of_arguments:
            self.usage()
            return 0

        if sys.argv[1] in ('-l', '--light'):
            self.__create_ios = 1
            self.__create_android = 1
            return 1
        elif sys.argv[1] in ('-li', '--light_ios'):
            self.__create_ios = 1
            return 1
        elif sys.argv[1] in ('-la', '--light_android'):
            self.__create_android = 1
            return 1

        for index in range(len(sys.argv)):
            if sys.argv[index] in ('-p', '--path') and sys.argv[index + 1]:
                self.__base_file_path = sys.argv[index + 1]
            if sys.argv[index] in ('-i', '--ios') and sys.argv[index + 1]:
                self.__ios_directory = sys.argv[index + 1]
                self.__create_ios = 1
            if sys.argv[index] in ('-a', '--android') and sys.argv[index + 1]:
                self.__android_directory = sys.argv[index + 1] + '/app/src/main/res/'
                self.__create_android = 1
            if sys.argv[index] in ('-s', '--splitter'):
                self.set_splitter(sys.argv[index])
        return 1
    
    # главный метод, запускающий скрип
    def run(self):
        if self.set_arguments():
            self.split_base_file_on_language_lists()
            
            if self.__create_ios:
                print('\nСоздание строк локализаций для iOS')
                print('>> {}\n'.format(self.__ios_directory))
                for lang in self.__languages:
                    print('* {}'.format(lang[0]))
                    self.create_ios_lproj(lang)
                             
            if self.__create_android:
                print('\nСоздание строк локализаций для Android')
                print('>> {}\n'.format(self.__android_directory))
                for lang in self.__languages:
                    print('* {}'.format(lang[0]))
                    self.create_android_xml(lang)

script = LocalStringsCreator()
script.run()


