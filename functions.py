def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    
    return ((left, top), (right, bottom))

def getAge(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top - 30
    
    return (left, top)

def getName(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top + 60

    return(left, top)