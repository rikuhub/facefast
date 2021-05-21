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
    top = rect.top - 20
    
    return (left, top)