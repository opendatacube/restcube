import re

def special_character_checker(string):
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
    if(regex.search(string) == None):
        return True

    else:
        return False
