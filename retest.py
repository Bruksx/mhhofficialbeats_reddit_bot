

def extract():
    text = "(tesdswgs)"
    index = text.find("(")
    index2 = text.find(")")  
    text = text[index+1:index2] 
    return text

print(extract())